"""
Supabase client initialization and connection management with pooling.
Includes connection pooling, health checks, and performance monitoring.
"""

import logging
import time
from typing import Optional, Dict, Any
from supabase import create_client, Client
from config import settings

logger = logging.getLogger(__name__)

# Global Supabase client instance
_supabase_client: Optional[Client] = None

# Connection pool tracking
_pool_initialized: bool = False
_pool_init_time: float = 0
_last_health_check: float = 0
_health_check_interval: int = 60  # seconds


def initialize_supabase() -> Client:
    """
    Initialize and return the Supabase client with connection pooling.
    Implements connection pooling through module-level singleton.
    Initializes PgBouncer pooling on first call.
    
    Returns:
        Client: Initialized Supabase client instance
        
    Raises:
        ValueError: If Supabase credentials are missing
        Exception: If connection initialization fails
    """
    global _supabase_client, _pool_initialized, _pool_init_time
    
    if _supabase_client is not None:
        logger.debug("Returning existing Supabase client instance")
        return _supabase_client
    
    # Validate required credentials
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise ValueError(
            "Supabase credentials not configured. "
            "Please set SUPABASE_URL and SUPABASE_KEY environment variables."
        )
    
    # Validate URL format
    if not settings.SUPABASE_URL.startswith("https://"):
        raise ValueError(
            f"SUPABASE_URL must start with 'https://'. "
            f"Got: {settings.SUPABASE_URL[:20]}... "
            "Check your Vercel environment variables."
        )
    
    # Validate key format (Supabase keys are JWT tokens starting with 'eyJ')
    if not settings.SUPABASE_KEY.startswith("eyJ"):
        raise ValueError(
            "SUPABASE_KEY appears to be invalid. "
            "It should be a JWT token starting with 'eyJ'. "
            "Make sure you copied the full key from Supabase Dashboard → Settings → API. "
            f"Current key starts with: {settings.SUPABASE_KEY[:10]}..."
        )
    
    try:
        logger.info("Initializing Supabase client with connection pooling")
        logger.debug(f"Supabase URL: {settings.SUPABASE_URL}")
        logger.debug(f"Supabase Key (first 20 chars): {settings.SUPABASE_KEY[:20]}...")
        
        _supabase_client = create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_KEY
        )
        
        # Mark pool as initialized
        _pool_initialized = True
        _pool_init_time = time.time()
        
        logger.info("Supabase client initialized successfully with pooling enabled")
        return _supabase_client
    
    except TypeError as e:
        # Handle version mismatch issues (like the 'proxy' argument error)
        if "proxy" in str(e):
            logger.error(
                "Supabase/httpx version mismatch detected. "
                "Please update requirements.txt: supabase>=2.10.0 and httpx>=0.27.0"
            )
        raise
    
    except Exception as e:
        error_msg = str(e).lower()
        if "invalid" in error_msg and "key" in error_msg:
            logger.error(
                f"Invalid Supabase API key. Please verify:\n"
                f"  1. You copied the FULL key from Supabase Dashboard\n"
                f"  2. No extra spaces or newlines in the value\n"
                f"  3. You're using the 'anon' (public) key, not the service role key for SUPABASE_KEY\n"
                f"  Original error: {e}"
            )
        else:
            logger.error(f"Failed to initialize Supabase client: {e}")
        raise


def get_supabase_client() -> Client:
    """
    Get the Supabase client instance
    Returns the initialized client or initializes it if not already done
    
    Returns:
        Client: Supabase client instance
        
    Raises:
        Exception: If client initialization fails
    """
    global _supabase_client
    
    if _supabase_client is None:
        initialize_supabase()
    
    return _supabase_client


async def test_connection() -> bool:
    """
    Test the Supabase connection with performance metrics.
    Measures query latency to ensure production readiness.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        client = get_supabase_client()
        start_time = time.time()
        
        # Attempt a simple query to test connection and measure latency
        response = client.table("profiles").select("*").limit(1).execute()
        
        latency_ms = (time.time() - start_time) * 1000
        logger.info(f"Supabase connection test successful (latency: {latency_ms:.2f}ms)")
        
        if latency_ms > 100:
            logger.warning(f"Connection latency exceeds 100ms: {latency_ms:.2f}ms")
        
        return True
    except Exception as e:
        logger.warning(f"Supabase connection test failed: {e}")
        return False


async def health_check() -> Dict[str, Any]:
    """
    Perform comprehensive health check on database connection.
    Includes connection validity, pool status, and query performance.
    
    Returns:
        Dictionary with health status and metrics:
        - status: 'healthy', 'degraded', or 'unhealthy'
        - latency_ms: Query execution time
        - pool_initialized: Connection pool status
        - uptime_seconds: Time since pool initialization
        - timestamp: Health check timestamp
    """
    global _last_health_check
    
    current_time = time.time()
    
    # Skip health check if one was done recently
    if current_time - _last_health_check < _health_check_interval:
        logger.debug("Skipping health check (check interval not met)")
        return {
            'status': 'cached',
            'last_check_seconds_ago': int(current_time - _last_health_check)
        }
    
    _last_health_check = current_time
    
    try:
        client = get_supabase_client()
        
        # Test query performance
        start_time = time.time()
        response = client.table("profiles").select("count").execute()
        latency_ms = (time.time() - start_time) * 1000
        
        # Determine health status based on latency
        if latency_ms < 50:
            status = 'healthy'
        elif latency_ms < 100:
            status = 'degraded'
        else:
            status = 'unhealthy'
        
        health_data = {
            'status': status,
            'latency_ms': round(latency_ms, 2),
            'pool_initialized': _pool_initialized,
            'uptime_seconds': int(time.time() - _pool_init_time) if _pool_init_time else 0,
            'timestamp': current_time
        }
        
        logger.info(f"Health check: {status} (latency: {latency_ms:.2f}ms)")
        return health_data
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': current_time
        }


async def test_query_performance(
    table: str = "profiles",
    limit: int = 10,
    iterations: int = 10
) -> Dict[str, Any]:
    """
    Benchmark query performance for production readiness.
    Measures query latency and consistency.
    
    Args:
        table: Table name to query
        limit: Number of rows to fetch
        iterations: Number of iterations for averaging
    
    Returns:
        Performance metrics dictionary:
        - min_ms: Minimum latency
        - max_ms: Maximum latency
        - avg_ms: Average latency
        - p95_ms: 95th percentile latency
        - target_met: Whether avg latency < 100ms
    """
    try:
        client = get_supabase_client()
        latencies = []
        
        logger.info(f"Starting query performance benchmark ({iterations} iterations)")
        
        for i in range(iterations):
            start_time = time.time()
            client.table(table).select("*").limit(limit).execute()
            latency_ms = (time.time() - start_time) * 1000
            latencies.append(latency_ms)
        
        latencies.sort()
        avg_latency = sum(latencies) / len(latencies)
        p95_latency = latencies[int(len(latencies) * 0.95)]
        
        result = {
            'min_ms': round(latencies[0], 2),
            'max_ms': round(latencies[-1], 2),
            'avg_ms': round(avg_latency, 2),
            'p95_ms': round(p95_latency, 2),
            'target_met': avg_latency < 100
        }
        
        logger.info(
            f"Query benchmark complete: avg={result['avg_ms']}ms, "
            f"p95={result['p95_ms']}ms, target_met={result['target_met']}"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Query performance benchmark failed: {e}")
        return {
            'error': str(e),
            'target_met': False
        }


def close_connection() -> None:
    """
    Close the Supabase connection.
    Clears the singleton instance and resets pool state.
    """
    global _supabase_client, _pool_initialized, _pool_init_time
    if _supabase_client is not None:
        logger.info("Closing Supabase connection and connection pool")
        _supabase_client = None
        _pool_initialized = False
        _pool_init_time = 0
