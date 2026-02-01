"""
FastAPI router for product scan endpoints
Handles barcode-based product lookup and orchestrates risk assessment
"""

import logging
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse
from models.schemas import BarcodeLookupRequest, BarcodeLookupResponse, BarcodeProduct
from utils.barcode_lookup import lookup_product_by_barcode, BarcodeLookupError
from utils.risk_scorer import generate_risk_score_for_product, RiskScorerError
from utils.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

# Create router with /api prefix (will be included in main.py)
router = APIRouter()


async def get_safer_alternatives(product_type: str, exclude_product_id: int, limit: int = 3) -> list:
    """
    Fetch safer organic/non-toxic alternatives for a given product type
    
    Args:
        product_type: Type of product (e.g., 'pad', 'tampon')
        exclude_product_id: ID of the scanned product to exclude from results
        limit: Maximum number of alternatives to return
        
    Returns:
        List of safer alternative products
    """
    try:
        supabase = get_supabase_client()
        
        # Define organic/safe brand prefixes for each product type
        organic_brands = {
            "pad": ["Rael", "Cora", "Organyc"],
            "tampon": ["Organyc", "Cora", "Honey Pot"]
        }
        
        brands_to_search = organic_brands.get(product_type, [])
        alternatives = []
        
        # Query for each organic brand
        for brand in brands_to_search:
            if len(alternatives) >= limit:
                break
                
            result = supabase.table("products") \
                .select("id, brand_name, product_type, barcode, coverage_score") \
                .eq("product_type", product_type) \
                .neq("id", exclude_product_id) \
                .ilike("brand_name", f"%{brand}%") \
                .eq("status", "ready") \
                .limit(1) \
                .execute()
            
            if result.data:
                product = result.data[0]
                alternatives.append({
                    "id": product["id"],
                    "brand_name": product["brand_name"],
                    "product_type": product["product_type"],
                    "safety_label": "Safe"
                })
        
        logger.info(f"Found {len(alternatives)} safer alternatives for {product_type}")
        return alternatives
        
    except Exception as e:
        logger.error(f"Error fetching safer alternatives: {e}", exc_info=True)
        return []


async def save_scan_to_history(
    scan_id: str,
    user_id: str,
    product: BarcodeProduct,
    risk_level: str,
    risk_score: Optional[int],
    risky_ingredients: list,
    explanation: str
) -> bool:
    """
    Save scan to scan_history table in Supabase
    Non-blocking function - runs in background task
    
    Args:
        scan_id: Unique UUID for this scan
        user_id: User ID who performed the scan
        product: Product object with details
        risk_level: Overall risk level (Low Risk, Caution, High Risk)
        risk_score: Numeric score 0-100 (optional)
        risky_ingredients: List of risky ingredient objects
        explanation: LLM-generated explanation
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        supabase = get_supabase_client()
        
        data = {
            "scan_id": scan_id,
            "user_id": user_id,
            "product_id": product.id,
            "barcode": product.barcode,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risky_ingredients": risky_ingredients,
            "explanation": explanation
        }
        
        result = supabase.table("scan_history").insert(data).execute()
        
        if result.data:
            logger.info(f"Scan history saved: {scan_id}")
            return True
        else:
            logger.warning(f"Failed to save scan history: {scan_id}")
            return False
            
    except Exception as e:
        # Log error but don't crash - this is a background task
        error_msg = str(e)
        
        # RLS errors are expected in some environments - log as warning
        if "row-level security policy" in error_msg or "401 Unauthorized" in error_msg:
            logger.warning(f"Scan history save blocked by RLS policy (expected in some envs): {scan_id}")
        else:
            logger.error(f"Error saving scan history: {e}", exc_info=True)
        
        return False


@router.post("/scan/barcode", tags=["Scan"], response_model=BarcodeLookupResponse)
async def scan_barcode(
    request: BarcodeLookupRequest
) -> dict:
    """
    Scan and lookup a product by barcode
    Returns product details including brand, ingredients, and coverage information
    
    Args:
        request: BarcodeLookupRequest containing:
            - barcode: Product barcode to lookup
            - user_id: Optional user ID for personalization
        
    Returns:
        JSON response with:
        - found: Boolean indicating if product was found
        - product: Product details (id, brand_name, barcode, ingredients, product_type, coverage_score, research_count)
        
    Raises:
        HTTPException 400: Invalid or missing barcode
        HTTPException 404: Product not found in database
        HTTPException 500: Lookup error
    """
    try:
        # Validate barcode
        if not request.barcode or not request.barcode.strip():
            logger.warning("Scan request with empty barcode")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Barcode cannot be empty"
            )
        
        barcode = request.barcode.strip()
        logger.info(f"Received barcode scan request: {barcode}")
        
        # Lookup product by barcode
        try:
            product_data = await lookup_product_by_barcode(barcode)
        except BarcodeLookupError as e:
            logger.error(f"Barcode lookup error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to lookup barcode: {str(e)}"
            )
        
        # Check if product was found
        if not product_data:
            logger.warning(f"Product not found for barcode: {barcode}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product not found for barcode: {barcode}"
            )
        
        # Convert to BarcodeProduct schema
        product = BarcodeProduct(**product_data)
        
        # Format response
        response = {
            "found": True,
            "product": product
        }
        
        logger.info(f"Barcode scan successful. Product: {product.brand_name}, ID: {product.id}")
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in barcode scan endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.post("/scan/barcode/assess", tags=["Scan"])
async def scan_barcode_with_assessment(
    request: BarcodeLookupRequest,
    background_tasks: BackgroundTasks
) -> dict:
    """
    Scan barcode and generate personalized health risk assessment
    Combines product lookup with user sensitivities for comprehensive analysis
    
    Args:
        request: BarcodeLookupRequest containing:
            - barcode: Product barcode
            - user_id: User ID for fetching sensitivities and personalization
        
    Returns:
        JSON response with:
        - scan_id: Unique identifier for this scan
        - product: Product details
        - overall_risk_level: "Low Risk | Caution | High Risk"
        - risky_ingredients: List of concerning ingredients with explanations
        - explanation: 2-sentence personalized assessment
        - timestamp: ISO8601 timestamp
        
    Raises:
        HTTPException 400: Invalid barcode or missing user_id
        HTTPException 404: Product or user not found
        HTTPException 500: Assessment error
    """
    try:
        # Validate inputs
        if not request.barcode or not request.barcode.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Barcode cannot be empty"
            )
        
        if not request.user_id or not request.user_id.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="user_id is required for risk assessment"
            )
        
        barcode = request.barcode.strip()
        user_id = request.user_id.strip()
        
        logger.info(f"Starting barcode assessment: {barcode} for user: {user_id}")
        
        # Step 1: Lookup product by barcode
        try:
            product_data = await lookup_product_by_barcode(barcode)
        except BarcodeLookupError as e:
            logger.error(f"Barcode lookup error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to lookup barcode: {str(e)}"
            )
        
        if not product_data:
            logger.warning(f"Product not found for barcode: {barcode}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product not found for barcode: {barcode}"
            )
        
        product = BarcodeProduct(**product_data)
        
        # Step 2: Generate risk assessment based on product ingredients
        logger.debug("Step 1: Product lookup completed. Step 2: Generating risk assessment")
        try:
            assessment = await generate_risk_score_for_product(
                product_id=product.id,
                product_name=product.brand_name,
                ingredients=product.ingredients,
                user_id=user_id
            )
        except RiskScorerError as e:
            logger.error(f"Risk scoring error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Assessment failed: {str(e)}"
            )
        
        # Generate scan response
        scan_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Step 3: Hardcoded safer alternatives for Always pads barcode
        safer_alternatives = []
        if barcode == "037000561538":
            # Always pads - show organic alternatives with purchase links
            safer_alternatives = [
                {
                    "id": 29,
                    "brand_name": "Rael Organic Cotton Cover Pads",
                    "product_type": "pad",
                    "safety_label": "Safe",
                    "url": "https://www.getrael.com/collections/pads/products/petite-organic-cotton-pads?variant=51779702718829"
                },
                {
                    "id": 30,
                    "brand_name": "Cora Organic Ultra Thin Period Pads",
                    "product_type": "pad",
                    "safety_label": "Safe",
                    "url": "https://www.walmart.com/ip/Cora-Compact-Applicator-Tampons-100-Organic-Cotton-Regular-Super-32-Count/693365963"
                },
                {
                    "id": 31,
                    "brand_name": "Organyc Heavy Night Pads",
                    "product_type": "pad",
                    "safety_label": "Safe",
                    "url": "https://thehoneypot.co/products/organic-duo-pack-tampons?variant=32026105249885&country=US&currency=USD"
                }
            ]
        
        response = {
            "scan_id": scan_id,
            "user_id": user_id,
            "product": product,
            "overall_risk_level": assessment.get("risk_level", "Caution"),
            "risk_score": assessment.get("risk_score"),
            "risky_ingredients": assessment.get("risky_ingredients", []),
            "explanation": assessment.get("explanation", "Unable to generate assessment"),
            "safer_alternatives": safer_alternatives,
            "timestamp": timestamp
        }
        
        logger.info(f"Barcode assessment completed. Risk Level: {response['overall_risk_level']}")
        
        # Save scan to history in background (non-blocking for faster response)
        background_tasks.add_task(
            save_scan_to_history,
            scan_id=scan_id,
            user_id=user_id,
            product=product,
            risk_level=response['overall_risk_level'],
            risk_score=assessment.get("risk_score"),
            risky_ingredients=response['risky_ingredients'],
            explanation=response['explanation']
        )
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in barcode assessment endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/scan/history", tags=["Scan"])
async def get_scan_history(
    user_id: str = Query(..., description="User ID to fetch scan history for"),
    limit: int = Query(10, ge=1, le=50, description="Number of recent scans to return")
) -> dict:
    """
    Get user's recent scan history
    
    Args:
        user_id: User ID
        limit: Number of recent scans (default 10, max 50)
        
    Returns:
        JSON response with:
        - scans: List of recent scans with product details
        - count: Total number of scans returned
        
    Raises:
        HTTPException 400: Invalid user_id
        HTTPException 500: Database error
    """
    try:
        if not user_id or not user_id.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_id is required"
            )
        
        supabase = get_supabase_client()
        
        # Query scan_history joined with products
        result = supabase.table("scan_history") \
            .select("""
                id,
                scan_id,
                barcode,
                risk_level,
                risk_score,
                scanned_at,
                products:product_id (
                    id,
                    brand_name,
                    product_type
                )
            """) \
            .eq("user_id", user_id) \
            .order("scanned_at", desc=True) \
            .limit(limit) \
            .execute()
        
        if not result.data:
            return {
                "scans": [],
                "count": 0
            }
        
        # Format response
        scans = []
        for scan in result.data:
            product_data = scan.get("products")
            scans.append({
                "scan_id": scan["scan_id"],
                "barcode": scan["barcode"],
                "brand_name": product_data.get("brand_name") if product_data else "Unknown",
                "product_type": product_data.get("product_type") if product_data else "general",
                "risk_level": scan["risk_level"],
                "risk_score": scan.get("risk_score"),
                "scanned_at": scan["scanned_at"]
            })
        
        logger.info(f"Retrieved {len(scans)} scan history records for user {user_id}")
        
        return {
            "scans": scans,
            "count": len(scans)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching scan history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch scan history: {str(e)}"
        )


@router.get("/scan/barcode/health", tags=["Scan"], include_in_schema=False)
async def scan_health_check() -> dict:
    """
    Health check endpoint for barcode scan service
    """
    return {
        "status": "healthy",
        "service": "barcode-scan-router",
        "version": "0.2.0"
    }
