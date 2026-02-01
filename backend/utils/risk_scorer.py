"""
Risk scoring utility for personalized health assessment
Orchestrates OCR, vector search, user sensitivities, and LLM analysis
"""

import logging
import json
from typing import Dict, List, Any, Optional
from uuid import uuid4
from datetime import datetime
from openai import OpenAI, APIError
from config import settings
from utils.ocr import extract_ingredients_from_image, OCRError
from utils.vector_search import search_similar_ingredients, VectorSearchError
from utils.supabase_client import get_supabase_client
from utils.prompts import format_risk_assessment_prompt, HEALTH_EXPERT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Constants
RISK_LEVEL_MAPPING = {
    "Low Risk (Safe)": "Low Risk",
    "Caution (Irritating)": "Caution",
    "High Risk (Harmful)": "High Risk"
}

class RiskScorerError(Exception):
    """Custom exception for risk scoring operations"""
    pass


async def generate_risk_score(
    image_file: bytes,
    user_id: str
) -> Dict[str, Any]:
    """
    Generate personalized health risk score for a product image
    Orchestrates complete pipeline: OCR → Vector Search → User Profile → LLM Analysis
    
    Args:
        image_file: Raw image bytes (JPEG, PNG, WebP)
        user_id: User identifier for fetching profile and sensitivities
        
    Returns:
        Dict containing:
        - risk_level: "Low Risk | Caution | High Risk"
        - explanation: 2-sentence assessment
        - ingredients_found: List of extracted ingredients
        - risky_ingredients: List of dicts with name, risk_level, reason
        
    Raises:
        RiskScorerError: If any step in pipeline fails
    """
    try:
        logger.info(f"Starting risk assessment for user: {user_id}")
        
        # Step 1: Extract ingredients from image
        logger.debug("Step 1: Extracting ingredients from image")
        try:
            scanned_ingredients = await extract_ingredients_from_image(image_file)
            if not scanned_ingredients:
                logger.warning("No ingredients extracted from image")
                scanned_ingredients = []
        except OCRError as e:
            logger.error(f"OCR extraction failed: {e}")
            raise RiskScorerError(f"Failed to extract ingredients from image: {e}")
        
        logger.info(f"Extracted {len(scanned_ingredients)} ingredients")
        
        # Step 2: Fetch user profile and sensitivities from Supabase
        logger.debug("Step 2: Fetching user profile and sensitivities")
        user_sensitivities = await _fetch_user_sensitivities(user_id)
        logger.debug(f"User sensitivities: {user_sensitivities}")
        
        # Step 3: Search for each ingredient in vector store
        logger.debug("Step 3: Searching vector store for ingredient context")
        retrieved_vector_data = await _search_all_ingredients(scanned_ingredients)
        logger.debug(f"Retrieved {len(retrieved_vector_data)} similar ingredients from vector store")
        
        # Step 4: Send to OpenAI LLM for risk assessment
        logger.debug("Step 4: Sending to LLM for risk assessment")
        risk_assessment = await _generate_llm_assessment(
            scanned_ingredients,
            user_sensitivities,
            retrieved_vector_data
        )
        
        logger.info(f"Risk assessment completed. Level: {risk_assessment.get('overall_risk_level')}")
        
        # Step 5: Format response
        response = {
            "risk_level": _normalize_risk_level(risk_assessment.get("overall_risk_level", "Caution")),
            "explanation": risk_assessment.get("explanation", "Unable to generate assessment"),
            "ingredients_found": scanned_ingredients,
            "risky_ingredients": _extract_risky_ingredients(risk_assessment.get("ingredient_details", []))
        }
        
        return response
    
    except RiskScorerError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in risk scoring pipeline: {e}")
        raise RiskScorerError(f"Risk scoring failed: {e}")


async def _fetch_user_sensitivities(user_id: str) -> List[str]:
    """
    Fetch user's known sensitivities from Supabase profiles table
    Returns empty list for anonymous users
    
    Args:
        user_id: User identifier
        
    Returns:
        List of sensitivity strings
        
    Raises:
        RiskScorerError: If database query fails
    """
    try:
        # Skip query for anonymous or missing user_id
        if not user_id or user_id == "anonymous":
            logger.info("Anonymous user - no sensitivities to fetch")
            return []
        
        supabase = get_supabase_client()
        
        # Query profiles table for user sensitivities
        response = supabase.table('profiles').select(
            'sensitivities'
        ).eq('id', user_id).single().execute()
        
        if not response.data:
            logger.warning(f"No profile found for user: {user_id}")
            return []
        
        sensitivities = response.data.get('sensitivities', [])
        
        # Handle different data formats
        if isinstance(sensitivities, str):
            # If stored as comma-separated string
            sensitivities = [s.strip() for s in sensitivities.split(',') if s.strip()]
        elif isinstance(sensitivities, list):
            sensitivities = [str(s).strip() for s in sensitivities if s]
        else:
            sensitivities = []
        
        logger.debug(f"Fetched {len(sensitivities)} sensitivities for user {user_id}")
        return sensitivities
    
    except Exception as e:
        logger.warning(f"Failed to fetch user sensitivities: {e}")
        # Return empty list instead of failing entire pipeline
        return []


async def _search_all_ingredients(
    ingredient_names: List[str],
    max_results_per_ingredient: int = 3
) -> List[Dict[str, Any]]:
    """
    Search vector store for each ingredient to gather context
    
    Args:
        ingredient_names: List of ingredient names to search
        max_results_per_ingredient: Max results per ingredient query
        
    Returns:
        List of unique ingredients with their vector data
        
    Raises:
        RiskScorerError: If vector search fails critically
    """
    try:
        all_results = []
        seen_ids = set()
        
        for ingredient in ingredient_names:
            try:
                logger.debug(f"Searching vector store for: {ingredient}")
                results = await search_similar_ingredients(
                    query=ingredient,
                    limit=max_results_per_ingredient
                )
                
                # Deduplicate by ID
                for result in results:
                    if result.get('id') not in seen_ids:
                        all_results.append(result)
                        seen_ids.add(result.get('id'))
            
            except VectorSearchError as e:
                logger.warning(f"Vector search failed for ingredient '{ingredient}': {e}")
                # Continue with other ingredients instead of failing
                continue
        
        logger.debug(f"Retrieved {len(all_results)} unique ingredients from vector store")
        return all_results
    
    except Exception as e:
        logger.error(f"Error searching ingredients: {e}")
        # Return empty list to allow pipeline to continue with LLM
        return []


async def _generate_llm_assessment(
    scanned_ingredients: List[str],
    user_sensitivities: List[str],
    retrieved_vector_data: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Send data to OpenAI LLM for personalized risk assessment
    
    Args:
        scanned_ingredients: Extracted ingredient list
        user_sensitivities: User's known sensitivities
        retrieved_vector_data: Similar ingredients from vector store
        
    Returns:
        Parsed LLM response with risk assessment
        
    Raises:
        RiskScorerError: If LLM call fails
    """
    try:
        # Format the prompt with actual data
        user_prompt = format_risk_assessment_prompt(
            scanned_ingredients,
            user_sensitivities,
            retrieved_vector_data
        )
        
        logger.debug("Calling OpenAI LLM for risk assessment")
        
        # Call OpenAI API with health expert system prompt
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=1024,
            temperature=0.7,
            messages=[
                {
                    "role": "system",
                    "content": HEALTH_EXPERT_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )
        
        # Extract response text
        response_text = response.choices[0].message.content.strip()
        logger.debug(f"LLM response: {response_text}")
        
        # Parse JSON response
        try:
            assessment = json.loads(response_text)
            
            # Validate response structure
            if "overall_risk_level" not in assessment:
                logger.warning("LLM response missing overall_risk_level, using default")
                assessment["overall_risk_level"] = "Caution (Irritating)"
            
            if "explanation" not in assessment:
                logger.warning("LLM response missing explanation, using default")
                assessment["explanation"] = "Unable to generate detailed explanation"
            
            if "ingredient_details" not in assessment:
                logger.warning("LLM response missing ingredient_details, using empty list")
                assessment["ingredient_details"] = []
            
            return assessment
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {response_text}")
            # Return structured error response
            return {
                "overall_risk_level": "Caution (Irritating)",
                "explanation": "Assessment requires manual review",
                "ingredient_details": []
            }
    
    except APIError as e:
        logger.error(f"OpenAI API error during risk assessment: {e}")
        raise RiskScorerError(f"LLM assessment failed: {e}")
    
    except Exception as e:
        logger.error(f"Unexpected error during LLM assessment: {e}")
        raise RiskScorerError(f"Risk assessment failed: {e}")


def _normalize_risk_level(llm_risk_level: str) -> str:
    """
    Normalize LLM risk level output to standardized format
    
    Args:
        llm_risk_level: Risk level from LLM (may contain descriptions)
        
    Returns:
        Standardized risk level: "Low Risk | Caution | High Risk"
    """
    if not llm_risk_level:
        return "Caution"
    
    llm_level_lower = llm_risk_level.lower()
    
    # Map various LLM outputs to standardized values
    if "low" in llm_level_lower and "safe" in llm_level_lower:
        return "Low Risk"
    elif "caution" in llm_level_lower or "irritat" in llm_level_lower:
        return "Caution"
    elif "high" in llm_level_lower or "harm" in llm_level_lower:
        return "High Risk"
    else:
        return "Caution"


def _extract_risky_ingredients(
    ingredient_details: List[Dict[str, Any]]
) -> List[Dict[str, str]]:
    """
    Extract only risky ingredients from LLM assessment details
    
    Args:
        ingredient_details: Full ingredient details from LLM
        
    Returns:
        List of dicts with name, risk_level, reason for risky ingredients
    """
    risky_items = []
    
    for item in ingredient_details:
        if not isinstance(item, dict):
            continue
        
        risk_level = item.get('risk_level', '').lower()
        
        # Include ingredients marked as Medium or High risk
        if 'medium' in risk_level or 'high' in risk_level:
            risky_items.append({
                'name': item.get('name', 'Unknown'),
                'risk_level': item.get('risk_level', 'Unknown'),
                'reason': item.get('reason', 'No details available')
            })
    
    return risky_items


async def generate_risk_score_for_product(
    product_id: int,
    product_name: str,
    ingredients: list,
    user_id: str
) -> dict:
    """
    Generate personalized health risk score for a product (barcode-based)
    Uses product ingredients directly (no OCR needed)
    Orchestrates: User Profile → Vector Search → LLM Analysis
    
    Args:
        product_id: Product ID from database
        product_name: Product brand name
        ingredients: List of ingredient names (already resolved from product record)
        user_id: User identifier for fetching profile and sensitivities
        
    Returns:
        Dict containing:
        - risk_level: "Low Risk | Caution | High Risk"
        - explanation: 2-sentence assessment
        - risky_ingredients: List of dicts with name, risk_level, reason
        
    Raises:
        RiskScorerError: If any step in pipeline fails
    """
    try:
        logger.info(f"Starting risk assessment for product: {product_name} (ID: {product_id})")
        
        # Step 1: Fetch user profile and sensitivities from Supabase
        logger.debug("Step 1: Fetching user profile and sensitivities")
        user_sensitivities = await _fetch_user_sensitivities(user_id)
        logger.debug(f"User sensitivities: {user_sensitivities}")
        
        # Step 2: Search for each ingredient in vector store
        logger.debug("Step 2: Searching vector store for ingredient context")
        retrieved_vector_data = await _search_all_ingredients(ingredients)
        logger.debug(f"Retrieved {len(retrieved_vector_data)} similar ingredients from vector store")
        
        # Step 3: Send to OpenAI LLM for risk assessment
        logger.debug("Step 3: Sending to LLM for risk assessment")
        risk_assessment = await _generate_llm_assessment(
            ingredients,
            user_sensitivities,
            retrieved_vector_data
        )
        
        logger.info(f"Risk assessment completed. Level: {risk_assessment.get('overall_risk_level')}")
        
        # Step 4: Format response
        response = {
            "risk_level": _normalize_risk_level(risk_assessment.get("overall_risk_level", "Caution")),
            "explanation": risk_assessment.get("explanation", "Unable to generate assessment"),
            "risky_ingredients": _extract_risky_ingredients(risk_assessment.get("ingredient_details", []))
        }
        
        return response
    
    except RiskScorerError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in risk scoring pipeline: {e}")
        raise RiskScorerError(f"Risk scoring failed: {e}")
