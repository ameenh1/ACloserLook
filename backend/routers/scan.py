"""
FastAPI router for product scan endpoints
Handles barcode-based product lookup and orchestrates risk assessment
"""

import logging
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status
from fastapi.responses import JSONResponse
from models.schemas import BarcodeLookupRequest, BarcodeLookupResponse, BarcodeProduct
from utils.barcode_lookup import lookup_product_by_barcode, BarcodeLookupError
from utils.risk_scorer import generate_risk_score_for_product, RiskScorerError

logger = logging.getLogger(__name__)

# Create router with /api prefix (will be included in main.py)
router = APIRouter()


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
    request: BarcodeLookupRequest
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
        
        response = {
            "scan_id": scan_id,
            "user_id": user_id,
            "product": product,
            "overall_risk_level": assessment.get("risk_level", "Caution"),
            "risky_ingredients": assessment.get("risky_ingredients", []),
            "explanation": assessment.get("explanation", "Unable to generate assessment"),
            "timestamp": timestamp
        }
        
        logger.info(f"Barcode assessment completed. Risk Level: {response['overall_risk_level']}")
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in barcode assessment endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
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
