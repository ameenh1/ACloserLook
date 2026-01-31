"""
FastAPI router for ingredient library browsing
Handles ingredient search, filtering, and detailed ingredient information
"""

import logging
import json
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, status
from models.schemas import IngredientData, IngredientsListResponse
from utils.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

# Create router (will be included in main.py with /api prefix)
router = APIRouter(tags=["Ingredients"])

# In-memory ingredient cache (loaded from JSON file)
_ingredient_cache: Optional[List[dict]] = None


def _load_ingredients() -> List[dict]:
    """
    Load ingredients from JSON file into memory
    
    Returns:
        List of ingredient dictionaries
    """
    global _ingredient_cache
    
    if _ingredient_cache is not None:
        return _ingredient_cache
    
    try:
        with open("backend/data/ingredients.json", "r") as f:
            data = json.load(f)
            _ingredient_cache = data.get("ingredients", [])
            logger.info(f"Loaded {len(_ingredient_cache)} ingredients from JSON file")
            return _ingredient_cache
    except FileNotFoundError:
        logger.error("Ingredients JSON file not found at backend/data/ingredients.json")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing ingredients JSON: {e}")
        return []


@router.get("/ingredients", response_model=IngredientsListResponse)
async def list_ingredients(
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    risk_level: str = Query("all", description="Filter by risk level: Low, Medium, High, or all")
) -> IngredientsListResponse:
    """
    Browse ingredient library with optional filtering
    
    Args:
        limit: Maximum number of ingredients to return (1-100, default 20)
        offset: Number of ingredients to skip for pagination (default 0)
        risk_level: Filter by risk level - "Low", "Medium", "High", or "all" (default "all")
        
    Returns:
        IngredientsListResponse with total count and paginated ingredients list
        
    Raises:
        HTTPException 400: Invalid query parameters
        HTTPException 500: Error loading ingredients
    """
    try:
        # Validate risk_level parameter
        valid_risk_levels = {"Low", "Medium", "High", "all"}
        if risk_level not in valid_risk_levels:
            logger.warning(f"Invalid risk_level filter: {risk_level}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid risk_level. Must be one of: {', '.join(valid_risk_levels)}"
            )
        
        logger.info(f"Listing ingredients with limit={limit}, offset={offset}, risk_level={risk_level}")
        
        # Load all ingredients
        all_ingredients = _load_ingredients()
        if not all_ingredients:
            logger.warning("No ingredients loaded from data source")
            return IngredientsListResponse(total_count=0, ingredients=[])
        
        # Apply risk level filter
        if risk_level != "all":
            filtered = [ing for ing in all_ingredients if ing.get("risk_level") == risk_level]
            logger.debug(f"Filtered {len(filtered)} ingredients by risk_level={risk_level}")
        else:
            filtered = all_ingredients
        
        total_count = len(filtered)
        
        # Apply pagination
        paginated = filtered[offset:offset + limit]
        logger.debug(f"Returning {len(paginated)} ingredients after pagination")
        
        # Convert to IngredientData models
        ingredients = []
        for ing in paginated:
            try:
                ingredient = IngredientData(
                    id=ing.get("id"),
                    name=ing.get("name"),
                    description=ing.get("description"),
                    risk_level=ing.get("risk_level"),
                    related_ingredients=ing.get("related_ingredients", [])
                )
                ingredients.append(ingredient)
            except Exception as e:
                logger.warning(f"Error converting ingredient {ing.get('id')}: {e}")
                continue
        
        response = IngredientsListResponse(
            total_count=total_count,
            ingredients=ingredients
        )
        
        logger.info(f"Successfully returned {len(ingredients)} ingredients")
        return response
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error in list_ingredients: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving ingredients: {str(e)}"
        )


@router.get("/ingredients/{ingredient_id}", response_model=IngredientData)
async def get_ingredient(ingredient_id: int) -> IngredientData:
    """
    Get detailed information about a specific ingredient
    
    Args:
        ingredient_id: Unique ingredient identifier
        
    Returns:
        IngredientData with full ingredient details
        
    Raises:
        HTTPException 400: Invalid ingredient_id format
        HTTPException 404: Ingredient not found
        HTTPException 500: Error loading ingredients
    """
    try:
        # Validate ingredient_id
        if ingredient_id < 1:
            logger.warning(f"Invalid ingredient_id: {ingredient_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ingredient_id must be a positive integer"
            )
        
        logger.info(f"Fetching ingredient details for id: {ingredient_id}")
        
        # Load all ingredients
        all_ingredients = _load_ingredients()
        if not all_ingredients:
            logger.warning("No ingredients loaded from data source")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingredient library is empty"
            )
        
        # Find ingredient by ID
        ingredient_data = None
        for ing in all_ingredients:
            if ing.get("id") == ingredient_id:
                ingredient_data = ing
                break
        
        # Check if ingredient exists
        if not ingredient_data:
            logger.warning(f"Ingredient not found with id: {ingredient_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ingredient with id {ingredient_id} not found"
            )
        
        # Convert to IngredientData model
        try:
            ingredient = IngredientData(
                id=ingredient_data.get("id"),
                name=ingredient_data.get("name"),
                description=ingredient_data.get("description"),
                risk_level=ingredient_data.get("risk_level"),
                related_ingredients=ingredient_data.get("related_ingredients", [])
            )
        except Exception as e:
            logger.error(f"Error converting ingredient {ingredient_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing ingredient data: {str(e)}"
            )
        
        logger.info(f"Successfully retrieved ingredient: {ingredient.name} (id: {ingredient_id})")
        return ingredient
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error in get_ingredient: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving ingredient: {str(e)}"
        )
