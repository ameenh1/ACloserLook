"""
Barcode lookup utility for product identification
Queries products table by barcode and retrieves ingredient information
"""

import logging
from typing import Optional, List, Dict, Any
from utils.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


class BarcodeLookupError(Exception):
    """Custom exception for barcode lookup operations"""
    pass


async def lookup_product_by_barcode(barcode: str) -> Optional[Dict[str, Any]]:
    """
    Look up a product by barcode in the products table
    Joins with ingredients_library to get ingredient names
    
    Args:
        barcode: Barcode string to lookup (e.g., "012345678901")
        
    Returns:
        Dict containing product details with ingredient names, or None if not found:
        {
            "id": int,
            "brand_name": str,
            "barcode": str,
            "ingredients": [str],  # List of ingredient names
            "product_type": str,
            "coverage_score": float,
            "research_count": int
        }
        
    Raises:
        BarcodeLookupError: If database query fails
    """
    try:
        if not barcode or not barcode.strip():
            logger.warning("Empty barcode provided")
            raise BarcodeLookupError("Barcode cannot be empty")
        
        barcode = barcode.strip()
        logger.info(f"Looking up barcode: {barcode}")
        
        supabase = get_supabase_client()
        
        # Query products table by barcode
        response = supabase.table('products').select(
            'id, brand_name, barcode, ingredients, product_type, coverage_score, research_count'
        ).eq('barcode', barcode).execute()
        
        if not response.data or len(response.data) == 0:
            logger.info(f"No product found for barcode: {barcode}")
            return None
        
        product = response.data[0]
        logger.debug(f"Found product: {product}")
        
        # Convert ingredient IDs to ingredient names
        ingredient_ids = product.get('ingredients', [])
        ingredient_names = []
        
        if ingredient_ids and len(ingredient_ids) > 0:
            try:
                ingredient_names = await _get_ingredient_names(ingredient_ids)
                logger.debug(f"Resolved {len(ingredient_names)} ingredients")
            except Exception as e:
                logger.warning(f"Failed to resolve ingredient names: {e}")
                # Continue without ingredient names rather than failing completely
        
        # Format response
        result = {
            "id": product.get('id'),
            "brand_name": product.get('brand_name', 'Unknown Brand'),
            "barcode": product.get('barcode'),
            "ingredients": ingredient_names,
            "product_type": product.get('product_type'),
            "coverage_score": product.get('coverage_score'),
            "research_count": product.get('research_count')
        }
        
        logger.info(f"Successfully resolved product: {result['brand_name']}")
        return result
    
    except BarcodeLookupError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in barcode lookup: {e}", exc_info=True)
        raise BarcodeLookupError(f"Failed to lookup barcode: {e}")


async def _get_ingredient_names(ingredient_ids: List[int]) -> List[str]:
    """
    Resolve ingredient IDs to ingredient names from ingredients_library
    
    Args:
        ingredient_ids: List of ingredient IDs
        
    Returns:
        List of ingredient names
        
    Raises:
        Exception: If database query fails
    """
    if not ingredient_ids:
        return []
    
    try:
        supabase = get_supabase_client()
        
        # Query ingredients_library for matching IDs
        response = supabase.table('ingredients_library').select(
            'id, name'
        ).in_('id', ingredient_ids).execute()
        
        if not response.data:
            logger.warning(f"No ingredients found for IDs: {ingredient_ids}")
            return []
        
        # Create ID to name mapping
        id_to_name = {ing['id']: ing['name'] for ing in response.data}
        
        # Return ingredient names in same order as input IDs
        ingredient_names = [id_to_name.get(ing_id, f"Unknown (ID: {ing_id})") for ing_id in ingredient_ids]
        
        return ingredient_names
    
    except Exception as e:
        logger.error(f"Error resolving ingredient names: {e}")
        raise


async def validate_barcode(barcode: str) -> bool:
    """
    Validate that a barcode exists in the database
    
    Args:
        barcode: Barcode to validate
        
    Returns:
        True if barcode exists, False otherwise
    """
    try:
        product = await lookup_product_by_barcode(barcode)
        return product is not None
    except BarcodeLookupError:
        return False
