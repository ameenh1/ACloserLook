"""
Embedding script for populating Supabase vector store with ingredient data
Loads ingredients from JSON and generates OpenAI embeddings for batch upsert
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from utils.supabase_client import get_supabase_client
from openai import OpenAI, RateLimitError, APIError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('embedding_process.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Constants
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536
BATCH_SIZE = 20
RETRY_ATTEMPTS = 3
RETRY_DELAY = 2


class IngredientEmbedder:
    """
    Handles embedding generation and Supabase upsert for ingredient data
    """
    
    def __init__(self):
        """Initialize embedder with Supabase client"""
        self.supabase = get_supabase_client()
        self.embedded_count = 0
        self.failed_count = 0
        self.failed_ingredients = []
    
    def load_ingredients(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load ingredients from JSON file
        
        Args:
            file_path: Path to ingredients.json file
            
        Returns:
            List of ingredient dictionaries
            
        Raises:
            FileNotFoundError: If ingredients.json doesn't exist
            json.JSONDecodeError: If JSON is malformed
        """
        try:
            logger.info(f"Loading ingredients from {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            ingredients = data.get('ingredients', [])
            logger.info(f"Successfully loaded {len(ingredients)} ingredients")
            return ingredients
        
        except FileNotFoundError:
            logger.error(f"Ingredients file not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in ingredients file: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading ingredients: {e}")
            raise
    
    async def generate_embedding(self, text: str, retry_count: int = 0) -> List[float]:
        """
        Generate embedding for text using OpenAI API with retry logic
        
        Args:
            text: Text to embed
            retry_count: Current retry attempt number
            
        Returns:
            Embedding vector (1536 dimensions)
            
        Raises:
            APIError: If all retry attempts fail
        """
        try:
            response = client.embeddings.create(
                input=text,
                model=EMBEDDING_MODEL
            )
            return response.data[0].embedding
        
        except RateLimitError as e:
            if retry_count < RETRY_ATTEMPTS:
                wait_time = RETRY_DELAY * (2 ** retry_count)
                logger.warning(f"Rate limited. Retrying in {wait_time}s (attempt {retry_count + 1}/{RETRY_ATTEMPTS})")
                await asyncio.sleep(wait_time)
                return await self.generate_embedding(text, retry_count + 1)
            else:
                logger.error(f"Rate limit exceeded after {RETRY_ATTEMPTS} retries for text: {text[:50]}...")
                raise
        
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise
        
        except Exception as e:
            logger.error(f"Unexpected error generating embedding: {e}")
            raise
    
    async def embed_ingredients(self, ingredients: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for all ingredients
        
        Args:
            ingredients: List of ingredient dictionaries
            
        Returns:
            List of ingredients with embeddings added
        """
        logger.info(f"Generating embeddings for {len(ingredients)} ingredients")
        embedded_ingredients = []
        
        for i, ingredient in enumerate(ingredients, 1):
            try:
                # Use description as embedding text
                text_to_embed = f"{ingredient['name']}: {ingredient['description']}"
                
                logger.debug(f"Embedding {i}/{len(ingredients)}: {ingredient['name']}")
                embedding = await self.generate_embedding(text_to_embed)
                
                # Add embedding to ingredient data
                ingredient_with_embedding = {
                    **ingredient,
                    'embedding': embedding
                }
                embedded_ingredients.append(ingredient_with_embedding)
                self.embedded_count += 1
                
                # Log progress every 5 ingredients
                if i % 5 == 0:
                    logger.info(f"Progress: {i}/{len(ingredients)} embeddings generated")
            
            except Exception as e:
                logger.error(f"Failed to embed ingredient '{ingredient.get('name', 'Unknown')}': {e}")
                self.failed_count += 1
                self.failed_ingredients.append(ingredient.get('name', 'Unknown'))
        
        logger.info(f"Embedding generation complete: {self.embedded_count} successful, {self.failed_count} failed")
        return embedded_ingredients
    
    async def batch_upsert_to_supabase(self, ingredients: List[Dict[str, Any]]) -> bool:
        """
        Upsert embedded ingredients to Supabase in batches with error handling
        
        Args:
            ingredients: List of ingredients with embeddings
            
        Returns:
            True if successful, False otherwise
        """
        if not ingredients:
            logger.warning("No ingredients to upsert")
            return False
        
        try:
            logger.info(f"Upserting {len(ingredients)} ingredients to Supabase")
            
            # Process in batches
            for i in range(0, len(ingredients), BATCH_SIZE):
                batch = ingredients[i:i + BATCH_SIZE]
                batch_num = (i // BATCH_SIZE) + 1
                total_batches = (len(ingredients) + BATCH_SIZE - 1) // BATCH_SIZE
                
                try:
                    # Prepare records for upsert
                    records = []
                    for ingredient in batch:
                        records.append({
                            'id': ingredient['id'],
                            'name': ingredient['name'],
                            'description': ingredient['description'],
                            'risk_level': ingredient['risk_level'],
                            'embedding': ingredient['embedding']
                        })
                    
                    # Upsert batch to Supabase
                    response = self.supabase.table('ingredients_library').upsert(
                        records,
                        on_conflict='id'
                    ).execute()
                    
                    logger.info(f"Batch {batch_num}/{total_batches} upserted successfully ({len(records)} records)")
                    
                    # Small delay between batches to avoid overwhelming server
                    if batch_num < total_batches:
                        await asyncio.sleep(0.5)
                
                except Exception as e:
                    logger.error(f"Failed to upsert batch {batch_num}/{total_batches}: {e}")
                    raise
            
            logger.info("All ingredients successfully upserted to Supabase")
            return True
        
        except Exception as e:
            logger.error(f"Critical error during upsert process: {e}")
            return False
    
    async def run_embedding_pipeline(self, ingredients_file: str = None) -> bool:
        """
        Execute complete embedding pipeline: load -> embed -> upsert
        
        Args:
            ingredients_file: Path to ingredients.json (defaults to backend/data/ingredients.json)
            
        Returns:
            True if pipeline completed successfully
        """
        try:
            # Default file path
            if ingredients_file is None:
                script_dir = Path(__file__).parent.parent
                ingredients_file = script_dir / 'data' / 'ingredients.json'
            
            logger.info("=" * 60)
            logger.info("EMBEDDING PIPELINE STARTED")
            logger.info("=" * 60)
            
            # Load ingredients
            ingredients = self.load_ingredients(str(ingredients_file))
            
            # Generate embeddings
            embedded_ingredients = await self.embed_ingredients(ingredients)
            
            if not embedded_ingredients:
                logger.error("No ingredients were successfully embedded")
                return False
            
            # Upsert to Supabase
            success = await self.batch_upsert_to_supabase(embedded_ingredients)
            
            logger.info("=" * 60)
            logger.info("EMBEDDING PIPELINE COMPLETED")
            logger.info(f"Successfully embedded: {self.embedded_count}")
            logger.info(f"Failed: {self.failed_count}")
            if self.failed_ingredients:
                logger.info(f"Failed ingredients: {', '.join(self.failed_ingredients)}")
            logger.info("=" * 60)
            
            return success
        
        except Exception as e:
            logger.error(f"Pipeline failed with error: {e}")
            return False


async def main():
    """Main entry point for embedding script"""
    try:
        # Validate OpenAI API key
        if not settings.OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY not set in environment variables")
            sys.exit(1)
        
        # Initialize embedder and run pipeline
        embedder = IngredientEmbedder()
        success = await embedder.run_embedding_pipeline()
        
        sys.exit(0 if success else 1)
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
