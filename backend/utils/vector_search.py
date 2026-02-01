"""
Vector search utility for querying similar ingredients from Supabase
Implements semantic search using embeddings stored in vector database
"""

import logging
import sys
import threading
from functools import lru_cache
from pathlib import Path
from typing import List, Dict, Any, Optional
from openai import OpenAI, APIError
from cachetools import TTLCache

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from utils.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

# Initialize OpenAI client for query embeddings
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Constants
EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_SEARCH_LIMIT = 5
MAX_SEARCH_LIMIT = 20

# In-memory caches (no external service required)
# Embedding cache: permanent, LRU-based (embeddings never change)
_embedding_cache_lock = threading.Lock()

# Vector search cache: TTL-based, 1 hour expiry (recipe data rarely changes)
_vector_search_cache = TTLCache(maxsize=500, ttl=3600)
_vector_search_cache_lock = threading.Lock()


class VectorSearchError(Exception):
    """Custom exception for vector search operations"""
    pass


@lru_cache(maxsize=1000)
def _generate_embedding_cached(query: str) -> str:
    """
    Generate embedding for a single query and cache the result.
    Uses JSON serialization trick to cache in LRU cache (lists aren't hashable).
    
    Args:
        query: Search query string
        
    Returns:
        JSON string of embedding vector
        
    Note: This function is cached per query. Embeddings never change,
    so this cache persists for the lifetime of the application.
    """
    try:
        import json
        
        response = client.embeddings.create(
            input=query.strip(),
            model=EMBEDDING_MODEL
        )
        embedding = response.data[0].embedding
        
        # Return as JSON string for caching (since lists aren't hashable)
        return json.dumps(embedding)
    
    except Exception as e:
        logger.error(f"Error in cached embedding generation: {e}")
        raise


async def generate_query_embedding(query: str) -> List[float]:
    """
    Generate embedding for search query using OpenAI API with caching.
    Embeddings are cached since ingredient names don't change.
    
    Args:
        query: Search query string
        
    Returns:
        Embedding vector (1536 dimensions)
        
    Raises:
        VectorSearchError: If embedding generation fails
    """
    try:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        query = query.strip()
        
        # Check cache first
        with _embedding_cache_lock:
            try:
                import json
                cached_embedding_json = _generate_embedding_cached(query)
                embedding = json.loads(cached_embedding_json)
                logger.debug(f"Cache HIT for embedding: {query}")
                return embedding
            except KeyError:
                pass  # Not in cache, proceed with generation
        
        # If not in cache, generate and it will be cached by _generate_embedding_cached
        import json
        embedding_json = _generate_embedding_cached(query)
        embedding = json.loads(embedding_json)
        logger.debug(f"Cache MISS, generated embedding for: {query}")
        return embedding
    
    except ValueError as e:
        logger.error(f"Invalid query: {e}")
        raise VectorSearchError(f"Invalid query: {e}")
    
    except APIError as e:
        logger.error(f"OpenAI API error while generating query embedding: {e}")
        raise VectorSearchError(f"Failed to generate embedding: {e}")
    
    except Exception as e:
        logger.error(f"Unexpected error generating query embedding: {e}")
        raise VectorSearchError(f"Error generating embedding: {e}")


async def generate_batch_embeddings(queries: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple queries in a single API call (batch processing)
    More efficient than calling generate_query_embedding() multiple times
    
    Args:
        queries: List of query strings to generate embeddings for
        
    Returns:
        List of embedding vectors (1536 dimensions each)
        
    Raises:
        VectorSearchError: If embedding generation fails
    """
    try:
        if not queries:
            return []
        
        # Filter out empty queries
        valid_queries = [q.strip() for q in queries if q and q.strip()]
        
        if not valid_queries:
            return []
        
        logger.debug(f"Generating batch embeddings for {len(valid_queries)} queries")
        
        # OpenAI API supports batch embedding generation
        response = client.embeddings.create(
            input=valid_queries,
            model=EMBEDDING_MODEL
        )
        
        # Extract embeddings in order
        embeddings = [data.embedding for data in response.data]
        
        logger.info(f"Successfully generated {len(embeddings)} embeddings in batch")
        return embeddings
    
    except APIError as e:
        logger.error(f"OpenAI API error while generating batch embeddings: {e}")
        raise VectorSearchError(f"Failed to generate batch embeddings: {e}")
    
    except Exception as e:
        logger.error(f"Unexpected error generating batch embeddings: {e}")
        raise VectorSearchError(f"Error generating batch embeddings: {e}")


async def search_similar_ingredients(
    query: str,
    limit: int = DEFAULT_SEARCH_LIMIT,
    risk_level_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search for similar ingredients using semantic vector similarity with caching.
    Results are cached for 1 hour since ingredient database rarely changes.
    
    Args:
        query: Search query string (e.g., "fragrance effects", "synthetic fibers")
        limit: Maximum number of results to return (1-20, default 5)
        risk_level_filter: Optional filter by risk level ('Low', 'Medium', 'High')
        
    Returns:
        List of matching ingredients sorted by similarity score (highest first)
        Each result includes: id, name, description, risk_level, similarity_score
        
    Raises:
        VectorSearchError: If search fails or no results found
    """
    try:
        # Validate inputs
        if not isinstance(limit, int) or limit < 1 or limit > MAX_SEARCH_LIMIT:
            limit = DEFAULT_SEARCH_LIMIT
            logger.warning(f"Invalid limit provided, using default: {limit}")
        
        if risk_level_filter and risk_level_filter not in ['Low', 'Medium', 'High']:
            logger.warning(f"Invalid risk_level_filter: {risk_level_filter}, ignoring filter")
            risk_level_filter = None
        
        # Create cache key for this search
        cache_key = f"{query}:{limit}:{risk_level_filter}"
        
        # Check vector search cache first
        with _vector_search_cache_lock:
            if cache_key in _vector_search_cache:
                logger.info(f"Vector search cache HIT for: '{query}'")
                return _vector_search_cache[cache_key]
        
        logger.info(f"Vector search cache MISS, searching: query='{query}', limit={limit}")
        
        # Generate embedding for query
        query_embedding = await generate_query_embedding(query)
        
        # Get Supabase client
        supabase = get_supabase_client()
        
        # Perform vector similarity search using Supabase RPC
        # Note: Requires 'search_ingredients' RPC function in Supabase
        try:
            response = supabase.rpc(
                'search_ingredients',
                {
                    'query_embedding': query_embedding,
                    'match_limit': limit,
                    'match_threshold': 0.1  # Minimum similarity threshold
                }
            ).execute()
            
            results = response.data if response.data else []
            
            # Apply risk level filter if specified
            if risk_level_filter:
                results = [
                    r for r in results
                    if r.get('risk_level') == risk_level_filter
                ]
                logger.info(f"Applied risk_level filter '{risk_level_filter}': {len(results)} results")
            
            if not results:
                logger.warning(f"No similar ingredients found for query: '{query}'")
                return []
            
            logger.info(f"Found {len(results)} similar ingredients for query: '{query}'")
            
            # Store results in cache for 1 hour
            with _vector_search_cache_lock:
                _vector_search_cache[cache_key] = results
            
            return results
        
        except Exception as rpc_error:
            logger.warning(f"RPC search failed, falling back to table scan: {rpc_error}")
            return await _fallback_search(query_embedding, limit, risk_level_filter)
    
    except VectorSearchError:
        raise
    
    except Exception as e:
        logger.error(f"Error during vector search: {e}")
        raise VectorSearchError(f"Vector search failed: {e}")


async def _fallback_search(
    query_embedding: List[float],
    limit: int,
    risk_level_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fallback search using direct table query when RPC is unavailable
    Implements similarity calculation in Python
    
    Args:
        query_embedding: Query embedding vector
        limit: Maximum results to return
        risk_level_filter: Optional risk level filter
        
    Returns:
        List of matching ingredients with similarity scores
    """
    try:
        logger.debug("Executing fallback table scan search")
        
        supabase = get_supabase_client()
        
        # Fetch all ingredients with embeddings
        response = supabase.table('ingredients_library').select(
            'id, name, description, risk_level, embedding'
        ).execute()
        
        ingredients = response.data if response.data else []
        
        if not ingredients:
            logger.warning("No ingredients found in database")
            return []
        
        # Calculate similarity scores using cosine similarity
        results_with_scores = []
        for ingredient in ingredients:
            if ingredient.get('embedding'):
                similarity = _cosine_similarity(query_embedding, ingredient['embedding'])
                
                # Apply risk level filter
                if risk_level_filter and ingredient.get('risk_level') != risk_level_filter:
                    continue
                
                results_with_scores.append({
                    'id': ingredient['id'],
                    'name': ingredient['name'],
                    'description': ingredient['description'],
                    'risk_level': ingredient['risk_level'],
                    'similarity_score': similarity
                })
        
        # Sort by similarity score and limit results
        results_with_scores.sort(key=lambda x: x['similarity_score'], reverse=True)
        return results_with_scores[:limit]
    
    except Exception as e:
        logger.error(f"Fallback search failed: {e}")
        raise VectorSearchError(f"Fallback search failed: {e}")


def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors
    
    Args:
        vec1: First vector (query embedding)
        vec2: Second vector (ingredient embedding)
        
    Returns:
        Cosine similarity score (0-1)
    """
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = sum(a ** 2 for a in vec1) ** 0.5
    magnitude2 = sum(b ** 2 for b in vec2) ** 0.5
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)


async def search_by_name(
    name_query: str,
    limit: int = DEFAULT_SEARCH_LIMIT
) -> List[Dict[str, Any]]:
    """
    Search for ingredients by exact or partial name match
    Faster alternative to vector search for name-based queries
    
    Args:
        name_query: Ingredient name or partial name to search
        limit: Maximum number of results
        
    Returns:
        List of matching ingredients
        
    Raises:
        VectorSearchError: If search fails
    """
    try:
        if not name_query or not name_query.strip():
            raise ValueError("Name query cannot be empty")
        
        logger.info(f"Searching by name: '{name_query}'")
        
        supabase = get_supabase_client()
        
        # Use Supabase text search
        response = supabase.table('ingredients_library').select(
            'id, name, description, risk_level'
        ).ilike('name', f'%{name_query}%').limit(limit).execute()
        
        results = response.data if response.data else []
        logger.info(f"Found {len(results)} ingredients matching name: '{name_query}'")
        
        return results
    
    except Exception as e:
        logger.error(f"Name search failed: {e}")
        raise VectorSearchError(f"Name search failed: {e}")


async def get_ingredient_by_id(ingredient_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific ingredient by ID
    
    Args:
        ingredient_id: Ingredient ID to retrieve
        
    Returns:
        Ingredient data if found, None otherwise
        
    Raises:
        VectorSearchError: If database query fails
    """
    try:
        if not isinstance(ingredient_id, int) or ingredient_id < 1:
            raise ValueError("Invalid ingredient ID")
        
        logger.debug(f"Fetching ingredient by ID: {ingredient_id}")
        
        supabase = get_supabase_client()
        
        response = supabase.table('ingredients_library').select(
            'id, name, description, risk_level'
        ).eq('id', ingredient_id).single().execute()
        
        return response.data if response.data else None
    
    except Exception as e:
        logger.error(f"Failed to fetch ingredient {ingredient_id}: {e}")
        raise VectorSearchError(f"Failed to fetch ingredient: {e}")


async def get_all_ingredients(
    limit: int = MAX_SEARCH_LIMIT,
    risk_level_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve all ingredients or filter by risk level
    
    Args:
        limit: Maximum number of results (default 20)
        risk_level_filter: Optional filter by 'Low', 'Medium', 'High'
        
    Returns:
        List of ingredients
        
    Raises:
        VectorSearchError: If database query fails
    """
    try:
        logger.info(f"Fetching all ingredients with limit={limit}, risk_level={risk_level_filter}")
        
        supabase = get_supabase_client()
        
        query = supabase.table('ingredients_library').select(
            'id, name, description, risk_level'
        )
        
        if risk_level_filter:
            if risk_level_filter not in ['Low', 'Medium', 'High']:
                raise ValueError(f"Invalid risk_level: {risk_level_filter}")
            query = query.eq('risk_level', risk_level_filter)
        
        response = query.limit(limit).execute()
        
        results = response.data if response.data else []
        logger.info(f"Retrieved {len(results)} ingredients")
        
        return results
    
    except Exception as e:
        logger.error(f"Failed to fetch ingredients: {e}")
        raise VectorSearchError(f"Failed to fetch ingredients: {e}")


# Async wrapper for synchronous context
def search_sync(
    query: str,
    limit: int = DEFAULT_SEARCH_LIMIT,
    risk_level_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Synchronous wrapper for search_similar_ingredients
    Use this for non-async contexts
    
    Args:
        query: Search query string
        limit: Maximum results
        risk_level_filter: Optional risk level filter
        
    Returns:
        List of matching ingredients
    """
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(
        search_similar_ingredients(query, limit, risk_level_filter)
    )
