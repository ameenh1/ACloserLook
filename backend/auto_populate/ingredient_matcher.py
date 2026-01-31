"""
Match scraped ingredients to existing ingredient library using vector similarity
"""

import json
import logging
from typing import List, Dict, Tuple
from openai import OpenAI

logger = logging.getLogger(__name__)


class IngredientMatcher:
    """Match new ingredients to existing library using embeddings"""
    
    def __init__(self, openai_api_key: str, existing_ingredients: List[Dict]):
        self.client = OpenAI(api_key=openai_api_key)
        self.existing_ingredients = existing_ingredients
        self.model = "text-embedding-3-small"
        self._cache_embeddings()
    
    def _cache_embeddings(self):
        """Pre-compute embeddings for all existing ingredients"""
        logger.info(f"Caching embeddings for {len(self.existing_ingredients)} ingredients...")
        
        self.ingredient_embeddings = {}
        for ing in self.existing_ingredients:
            # Handle both dict and string formats
            if isinstance(ing, str):
                ing_name = ing
            else:
                ing_name = ing.get('name', '')
            
            # Get embedding for ingredient NAME (not description) for better short-text matching
            response = self.client.embeddings.create(
                input=ing_name,
                model=self.model
            )
            self.ingredient_embeddings[ing_name] = response.data[0].embedding
    
    def match_ingredient(self, scraped_ingredient: str, threshold: float = 0.50) -> Tuple[Dict, float]:
        """
        Match a scraped ingredient to existing library
        
        Returns:
            (matched_ingredient_dict, similarity_score)
        """
        # Get embedding for scraped ingredient
        response = self.client.embeddings.create(
            input=scraped_ingredient,
            model=self.model
        )
        scraped_embedding = response.data[0].embedding
        
        # Find closest match using cosine similarity
        best_match = None
        best_score = 0
        best_ing_name = None
        
        for ing_name, ing_embedding in self.ingredient_embeddings.items():
            similarity = self._cosine_similarity(scraped_embedding, ing_embedding)
            
            if similarity > best_score:
                best_score = similarity
                best_ing_name = ing_name
                # Try to find the full ingredient object
                for ing in self.existing_ingredients:
                    if isinstance(ing, dict) and ing.get('name') == ing_name:
                        best_match = ing
                        break
                    elif isinstance(ing, str) and ing == ing_name:
                        best_match = {"name": ing_name, "description": ing_name}
                        break
        
        # Return match if above threshold
        if best_score >= threshold:
            logger.info(f"✓ Matched '{scraped_ingredient}' → '{best_ing_name}' ({best_score:.2f})")
            return best_match, best_score
        else:
            logger.warning(f"No match found for '{scraped_ingredient}' (best: {best_score:.2f})")
            return None, best_score
    
    def match_ingredients_batch(self, scraped_ingredients: List[str], threshold: float = 0.7) -> Dict:
        """
        Match multiple ingredients
        
        Returns:
            {
                "matched": [(ingredient_dict, score), ...],
                "unmatched": [ingredient_name, ...],
                "coverage": 0.85
            }
        """
        matched = []
        unmatched = []
        
        for ingredient in scraped_ingredients:
            match, score = self.match_ingredient(ingredient, threshold)
            if match:
                matched.append((match, score))
                logger.info(f"✓ Matched '{ingredient}' → '{match['name']}' ({score:.2f})")
            else:
                unmatched.append(ingredient)
                logger.warning(f"✗ No match for '{ingredient}'")
        
        coverage = len(matched) / len(scraped_ingredients) if scraped_ingredients else 0
        
        return {
            "matched": matched,
            "unmatched": unmatched,
            "coverage": coverage
        }
    
    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        import math
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a ** 2 for a in vec1))
        magnitude2 = math.sqrt(sum(b ** 2 for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0
        
        return dot_product / (magnitude1 * magnitude2)


# Usage example
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Load existing ingredients
    with open("../../data/ingredients.json") as f:
        existing_ingredients = json.load(f)
    
    # Initialize matcher
    matcher = IngredientMatcher(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        existing_ingredients=existing_ingredients
    )
    
    # Test matching
    test_ingredients = [
        "Rayon fibers",
        "Cotton blend",
        "Fragrance compounds",
        "Sodium carboxymethyl cellulose"
    ]
    
    results = matcher.match_ingredients_batch(test_ingredients)
    print(json.dumps(results, indent=2, default=str))
