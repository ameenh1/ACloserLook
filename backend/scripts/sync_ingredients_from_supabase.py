"""
Sync ingredients from Supabase to local ingredients.json
Generates embeddings for any ingredients missing them
This ensures your local JSON stays in sync with Supabase database
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from utils.supabase_client import get_supabase_client
from openai import OpenAI, APIError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Constants
EMBEDDING_MODEL = "text-embedding-3-small"
INGREDIENTS_JSON_PATH = Path(__file__).parent.parent / 'data' / 'ingredients.json'


async def fetch_all_ingredients_from_supabase() -> List[Dict[str, Any]]:
    """
    Fetch ALL ingredients from Supabase ingredients_library table
    
    Returns:
        List of ingredient dictionaries with all fields
    """
    try:
        logger.info("Fetching all ingredients from Supabase...")
        supabase = get_supabase_client()
        
        response = supabase.table('ingredients_library').select(
            'id, name, description, risk_level, embedding, created_at'
        ).order('id').execute()
        
        if not response.data:
            logger.warning("No ingredients found in Supabase!")
            return []
        
        logger.info(f"Found {len(response.data)} ingredients in Supabase")
        return response.data
    
    except Exception as e:
        logger.error(f"Error fetching ingredients from Supabase: {e}")
        raise


def load_local_ingredients_json() -> Dict[str, Any]:
    """
    Load ingredients from local JSON file
    
    Returns:
        Dictionary with 'ingredients' key or empty structure
    """
    try:
        if INGREDIENTS_JSON_PATH.exists():
            logger.info(f"Loading local ingredients.json from {INGREDIENTS_JSON_PATH}")
            with open(INGREDIENTS_JSON_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Ensure correct structure
            if 'ingredients' not in data:
                data = {'ingredients': []}
            
            logger.info(f"Found {len(data['ingredients'])} ingredients in local JSON")
            return data
        else:
            logger.warning("ingredients.json not found, will create new file")
            return {'ingredients': []}
    
    except Exception as e:
        logger.error(f"Error loading ingredients.json: {e}")
        return {'ingredients': []}


def save_ingredients_to_json(ingredients: List[Dict[str, Any]]) -> None:
    """
    Save ingredients list to ingredients.json
    
    Args:
        ingredients: List of ingredient dictionaries
    """
    try:
        # Prepare clean data (remove embedding and created_at for JSON storage)
        clean_ingredients = []
        for ing in ingredients:
            clean_ing = {
                'id': ing.get('id'),
                'name': ing.get('name', 'Unknown'),
                'description': ing.get('description', ''),
                'risk_level': ing.get('risk_level', 'Medium')
            }
            clean_ingredients.append(clean_ing)
        
        data = {'ingredients': clean_ingredients}
        
        # Ensure directory exists
        INGREDIENTS_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Save with pretty printing
        with open(INGREDIENTS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Saved {len(clean_ingredients)} ingredients to {INGREDIENTS_JSON_PATH}")
    
    except Exception as e:
        logger.error(f"Error saving ingredients.json: {e}")
        raise


async def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for text using OpenAI API
    
    Args:
        text: Text to embed
        
    Returns:
        Embedding vector (1536 dimensions)
    """
    try:
        response = client.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL
        )
        return response.data[0].embedding
    
    except APIError as e:
        logger.error(f"OpenAI API error: {e}")
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error generating embedding: {e}")
        raise


async def update_missing_embeddings(ingredients: List[Dict[str, Any]]) -> int:
    """
    Check which ingredients are missing embeddings and generate them
    
    Args:
        ingredients: List of ingredient dictionaries from Supabase
        
    Returns:
        Number of embeddings generated
    """
    try:
        logger.info("Checking for ingredients with missing embeddings...")
        supabase = get_supabase_client()
        
        missing_embeddings = []
        for ing in ingredients:
            if not ing.get('embedding') or ing.get('embedding') is None:
                missing_embeddings.append(ing)
        
        if not missing_embeddings:
            logger.info("✅ All ingredients have embeddings!")
            return 0
        
        logger.warning(f"Found {len(missing_embeddings)} ingredients without embeddings")
        
        # Generate embeddings for missing ones
        updated_count = 0
        for i, ing in enumerate(missing_embeddings, 1):
            try:
                logger.info(f"Generating embedding {i}/{len(missing_embeddings)}: {ing['name']}")
                
                # Combine name and description for embedding
                text_to_embed = f"{ing['name']}: {ing.get('description', '')}"
                embedding = await generate_embedding(text_to_embed)
                
                # Update in Supabase
                supabase.table('ingredients_library').update({
                    'embedding': embedding
                }).eq('id', ing['id']).execute()
                
                logger.info(f"✅ Updated embedding for '{ing['name']}'")
                updated_count += 1
                
                # Small delay to avoid rate limits
                await asyncio.sleep(0.5)
            
            except Exception as e:
                logger.error(f"Failed to generate embedding for '{ing['name']}': {e}")
                continue
        
        logger.info(f"✅ Generated {updated_count} new embeddings")
        return updated_count
    
    except Exception as e:
        logger.error(f"Error updating embeddings: {e}")
        raise


async def sync_ingredients():
    """
    Main sync function:
    1. Fetch all ingredients from Supabase
    2. Generate embeddings for any missing ones
    3. Update local ingredients.json to match Supabase
    """
    try:
        logger.info("=" * 70)
        logger.info("INGREDIENT SYNC PROCESS STARTED")
        logger.info("=" * 70)
        
        # Step 1: Fetch from Supabase
        supabase_ingredients = await fetch_all_ingredients_from_supabase()
        
        if not supabase_ingredients:
            logger.error("No ingredients found in Supabase. Cannot sync.")
            return False
        
        # Step 2: Generate missing embeddings
        embeddings_generated = await update_missing_embeddings(supabase_ingredients)
        
        # Step 3: Fetch again to get updated embeddings
        if embeddings_generated > 0:
            logger.info("Re-fetching ingredients with updated embeddings...")
            supabase_ingredients = await fetch_all_ingredients_from_supabase()
        
        # Step 4: Save to local JSON
        save_ingredients_to_json(supabase_ingredients)
        
        # Step 5: Summary
        logger.info("=" * 70)
        logger.info("INGREDIENT SYNC COMPLETED")
        logger.info(f"Total ingredients in Supabase: {len(supabase_ingredients)}")
        logger.info(f"Embeddings generated: {embeddings_generated}")
        logger.info(f"Local JSON updated: {INGREDIENTS_JSON_PATH}")
        logger.info("=" * 70)
        
        # Check for missing embeddings
        missing = [ing for ing in supabase_ingredients if not ing.get('embedding')]
        if missing:
            logger.warning(f"⚠️ Warning: {len(missing)} ingredients still missing embeddings:")
            for ing in missing:
                logger.warning(f"  - {ing['name']} (ID: {ing['id']})")
        else:
            logger.info("✅ All ingredients have embeddings!")
        
        return True
    
    except Exception as e:
        logger.error(f"Sync failed with error: {e}")
        return False


async def export_for_manual_review():
    """
    Export ingredients to a separate file for manual review
    Useful for checking what's in Supabase vs local JSON
    """
    try:
        logger.info("Exporting ingredients for manual review...")
        
        supabase_ingredients = await fetch_all_ingredients_from_supabase()
        local_data = load_local_ingredients_json()
        
        export_path = Path(__file__).parent.parent / 'data' / 'ingredients_supabase_export.json'
        
        export_data = {
            'supabase_count': len(supabase_ingredients),
            'local_json_count': len(local_data.get('ingredients', [])),
            'supabase_ingredients': [
                {
                    'id': ing.get('id'),
                    'name': ing.get('name'),
                    'description': ing.get('description', ''),
                    'risk_level': ing.get('risk_level'),
                    'has_embedding': bool(ing.get('embedding'))
                }
                for ing in supabase_ingredients
            ]
        }
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Exported to {export_path}")
        logger.info(f"Supabase has {len(supabase_ingredients)} ingredients")
        logger.info(f"Local JSON has {len(local_data.get('ingredients', []))} ingredients")
    
    except Exception as e:
        logger.error(f"Export failed: {e}")


async def main():
    """Main entry point"""
    try:
        # Validate OpenAI API key
        if not settings.OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY not set in environment variables")
            sys.exit(1)
        
        # Run sync
        success = await sync_ingredients()
        
        # Optional: Export for review
        await export_for_manual_review()
        
        sys.exit(0 if success else 1)
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
