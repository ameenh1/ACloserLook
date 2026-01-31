"""
FastAPI router for product scan endpoint
Handles image uploads and orchestrates risk assessment
"""

import logging
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, File, UploadFile, Query, HTTPException, status
from fastapi.responses import JSONResponse
from utils.risk_scorer import generate_risk_score, RiskScorerError

logger = logging.getLogger(__name__)

# Create router with /api prefix (will be included in main.py)
router = APIRouter()

# Allowed image types
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB limit


@router.post("/scan", tags=["Scan"])
async def scan_product(
    file: UploadFile = File(..., description="Product image file (JPEG, PNG, or WebP)"),
    user_id: str = Query(..., description="User identifier for personalized assessment")
) -> dict:
    """
    Scan a product image and generate personalized health risk assessment
    
    Args:
        file: Multipart file upload (image)
        user_id: User ID for fetching sensitivities and personalization
        
    Returns:
        JSON response with:
        - scan_id: Unique identifier for this scan
        - user_id: User who performed the scan
        - overall_risk_level: "Low Risk | Caution | High Risk"
        - ingredients_found: List of extracted ingredients
        - risky_ingredients: List of dicts with name, risk_level, reason
        - explanation: 2-sentence assessment
        - timestamp: ISO8601 timestamp
        
    Raises:
        HTTPException 400: Invalid file type or size
        HTTPException 422: Missing or invalid user_id
        HTTPException 500: Processing error
    """
    try:
        # Validate user_id
        if not user_id or not user_id.strip():
            logger.warning("Scan request missing user_id")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="user_id query parameter is required"
            )
        
        user_id = user_id.strip()
        logger.info(f"Received scan request from user: {user_id}")
        
        # Validate file type
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            logger.warning(f"Invalid file type: {file.content_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed types: JPEG, PNG, WebP. Received: {file.content_type}"
            )
        
        # Validate filename
        if not file.filename:
            logger.warning("File uploaded without filename")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must have a filename"
            )
        
        logger.debug(f"Processing file: {file.filename} (type: {file.content_type})")
        
        # Read file data
        file_data = await file.read()
        
        # Validate file size
        if len(file_data) > MAX_FILE_SIZE:
            logger.warning(f"File size exceeds limit: {len(file_data)} bytes")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds {MAX_FILE_SIZE} bytes limit"
            )
        
        if len(file_data) == 0:
            logger.warning("Empty file uploaded")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty"
            )
        
        logger.debug(f"File validated. Size: {len(file_data)} bytes")
        
        # Generate risk score
        logger.info(f"Starting risk assessment for user {user_id}")
        try:
            assessment = await generate_risk_score(file_data, user_id)
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
            "overall_risk_level": assessment.get("risk_level", "Caution"),
            "ingredients_found": assessment.get("ingredients_found", []),
            "risky_ingredients": assessment.get("risky_ingredients", []),
            "explanation": assessment.get("explanation", "Unable to generate assessment"),
            "timestamp": timestamp
        }
        
        logger.info(f"Scan completed. ID: {scan_id}, Risk Level: {response['overall_risk_level']}")
        logger.debug(f"Scan response: {response}")
        
        return response
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error in scan endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/scan/health", tags=["Scan"], include_in_schema=False)
async def scan_health_check() -> dict:
    """
    Health check endpoint for scan service
    """
    return {
        "status": "healthy",
        "service": "scan-router",
        "version": "0.1.0"
    }
