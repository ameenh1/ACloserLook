"""
Database connection pooling and performance utilities for Supabase PostgreSQL.
Implements async connection pooling with health checks and benchmarking.
"""

import asyncio
import time
from typing import Optional, Dict, List, Any
from contextlib import asynccontextmanager
import logging

try:
    from postgrest import AsyncPostgrestClient
except ImportError:
    AsyncPostgrestClient = None

logger = logging.getLogger(__name__)

# Global connection pool
_connection_pool: Optional[Dict[str, Any]] = None
_pool_lock = asyncio.Lock()


class ConnectionPoolConfig:
    """Configuration for database connection pooling."""
    
    def __init__(
        self,
        min_size: int = 5,
        max_size: int = 20,
        max_idle_time: int = 300,  # 5 minutes
        connection_timeout: int = 10,
        health_check_interval: int = 60
    ):
        """
        Initialize pool configuration.
        
        Args:
            min_size: Minimum connections to maintain
            max_size: Maximum connections allowed
            max_idle_time: Seconds before idle connection is closed
            connection_timeout: Timeout for acquiring connection (seconds)
            health_check_interval: Health check frequency (seconds)
        """
        self.min_size = min_size
        self.max_size = max_size
        self.max_idle_time = max_idle_time
        self.connection_timeout = connection_timeout
        self.health_check_interval = health_check_interval


class PooledConnection:
    """Wrapper for pooled database connections with metrics."""
    
    def __init__(self, client, pool_instance):
        self.client = client
        self.pool = pool_instance
        self.created_at = time.time()
        self.last_used_at = time.time()
        self.query_count = 0
        self.total_latency_ms = 0
    
    def record_query(self, latency_ms: float):
        """Record query execution for metrics."""
        self.query_count += 1
        self.total_latency_ms += latency_ms
        self.last_used_at = time.time()
    
    def average_latency(self) -> float:
        """Calculate average query latency."""
        if self.query_count == 0:
            return 0.0
        return self.total_latency_ms / self.query_count
    
    def is_idle(self, idle_timeout: int) -> bool:
        """Check if connection has been idle too long."""
        return (time.time() - self.last_used_at) > idle_timeout
    
    def age_seconds(self) -> float:
        """Get connection age in seconds."""
        return time.time() - self.created_at


class ConnectionPool:
    """Async connection pool for Supabase PostgreSQL."""
    
    def __init__(self, config: ConnectionPoolConfig):
        self.config = config
        self.connections: List[PooledConnection] = []
        self.available_connections: asyncio.Queue = asyncio.Queue()
        self.in_use_count = 0
        self.total_queries = 0
        self.total_latency_ms = 0
        self.initialized = False
    
    async def initialize(self):
        """Initialize the connection pool."""
        async with _pool_lock:
            if self.initialized:
                return
            
            logger.info(f"Initializing connection pool (min={self.config.min_size}, max={self.config.max_size})")
            
            # Create minimum connections
            for _ in range(self.config.min_size):
                try:
                    conn = await self._create_connection()
                    self.connections.append(conn)
                    await self.available_connections.put(conn)
                except Exception as e:
                    logger.error(f"Failed to create pool connection: {e}")
            
            self.initialized = True
            logger.info(f"Connection pool initialized with {len(self.connections)} connections")
    
    async def _create_connection(self) -> PooledConnection:
        """Create a new pooled connection."""
        from backend.utils.supabase_client import get_supabase_client
        
        client = await get_supabase_client()
        return PooledConnection(client, self)
    
    @asynccontextmanager
    async def acquire(self, timeout: Optional[int] = None):
        """
        Acquire a connection from the pool.
        
        Usage:
            async with pool.acquire() as conn:
                result = await conn.query(...)
        """
        timeout = timeout or self.config.connection_timeout
        
        try:
            # Try to get available connection
            conn = self.available_connections.get_nowait()
        except asyncio.QueueEmpty:
            # Create new connection if below max
            if len(self.connections) < self.config.max_size:
                try:
                    conn = await self._create_connection()
                    self.connections.append(conn)
                except Exception as e:
                    logger.error(f"Failed to create new connection: {e}")
                    raise
            else:
                # Wait for available connection
                try:
                    conn = await asyncio.wait_for(
                        self.available_connections.get(),
                        timeout=timeout
                    )
                except asyncio.TimeoutError:
                    raise Exception(f"Failed to acquire connection within {timeout}s")
        
        self.in_use_count += 1
        
        try:
            yield conn
        finally:
            self.in_use_count -= 1
            # Return connection to pool if still valid
            if self._is_connection_valid(conn):
                await self.available_connections.put(conn)
            else:
                self.connections.remove(conn)
                logger.warning("Removed invalid connection from pool")
    
    def _is_connection_valid(self, conn: PooledConnection) -> bool:
        """Check if connection is still valid."""
        # Connection is valid if age < 1 hour
        return conn.age_seconds() < 3600
    
    async def execute_query(
        self,
        query_func,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute a query using a pooled connection with timing.
        
        Args:
            query_func: Async function to execute
            *args: Positional arguments for query function
            **kwargs: Keyword arguments for query function
        
        Returns:
            Query result
        """
        async with self.acquire() as conn:
            start_time = time.time()
            try:
                result = await query_func(conn, *args, **kwargs)
                latency_ms = (time.time() - start_time) * 1000
                
                conn.record_query(latency_ms)
                self.total_queries += 1
                self.total_latency_ms += latency_ms
                
                if latency_ms > 100:
                    logger.warning(f"Slow query detected: {latency_ms:.2f}ms")
                
                return result
            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on pool."""
        stats = {
            'status': 'healthy',
            'total_connections': len(self.connections),
            'in_use': self.in_use_count,
            'available': self.available_connections.qsize(),
            'total_queries': self.total_queries,
            'average_latency_ms': self._calculate_average_latency(),
            'connections': []
        }
        
        for conn in self.connections:
            conn_stats = {
                'age_seconds': conn.age_seconds(),
                'idle': conn.is_idle(self.config.max_idle_time),
                'query_count': conn.query_count,
                'average_latency_ms': conn.average_latency()
            }
            stats['connections'].append(conn_stats)
        
        return stats
    
    def _calculate_average_latency(self) -> float:
        """Calculate average latency across all queries."""
        if self.total_queries == 0:
            return 0.0
        return self.total_latency_ms / self.total_queries
    
    async def close(self):
        """Close all connections in the pool."""
        logger.info("Closing connection pool")
        
        while not self.available_connections.empty():
            try:
                self.available_connections.get_nowait()
            except asyncio.QueueEmpty:
                break
        
        self.connections.clear()
        self.initialized = False


async def setup_connection_pool(config: Optional[ConnectionPoolConfig] = None) -> ConnectionPool:
    """
    Initialize the global connection pool.
    
    Args:
        config: Optional ConnectionPoolConfig (uses defaults if None)
    
    Returns:
        Initialized ConnectionPool instance
    """
    global _connection_pool
    
    if _connection_pool is not None:
        return _connection_pool
    
    config = config or ConnectionPoolConfig()
    pool = ConnectionPool(config)
    await pool.initialize()
    
    _connection_pool = pool
    return pool


def get_connection_pool() -> ConnectionPool:
    """Get the global connection pool."""
    if _connection_pool is None:
        raise RuntimeError(
            "Connection pool not initialized. Call setup_connection_pool() first."
        )
    return _connection_pool


async def get_pooled_connection():
    """
    Get a connection from the pool.
    
    Usage:
        async with get_pooled_connection() as conn:
            result = await conn.query(...)
    """
    pool = get_connection_pool()
    return pool.acquire()


async def test_connection_performance(
    query_func,
    iterations: int = 100,
    *args,
    **kwargs
) -> Dict[str, float]:
    """
    Benchmark connection and query performance.
    
    Args:
        query_func: Async function to benchmark
        iterations: Number of iterations to run
        *args: Positional arguments for query function
        **kwargs: Keyword arguments for query function
    
    Returns:
        Performance statistics dictionary with keys:
        - min_ms: Minimum latency
        - max_ms: Maximum latency
        - avg_ms: Average latency
        - p95_ms: 95th percentile latency
        - p99_ms: 99th percentile latency
        - total_time_s: Total benchmark time
    """
    pool = get_connection_pool()
    
    latencies: List[float] = []
    total_start = time.time()
    
    logger.info(f"Starting performance benchmark ({iterations} iterations)")
    
    for i in range(iterations):
        start = time.time()
        try:
            await query_func(*args, **kwargs)
            latency_ms = (time.time() - start) * 1000
            latencies.append(latency_ms)
            
            if (i + 1) % 25 == 0:
                logger.debug(f"Completed {i + 1}/{iterations} benchmark iterations")
        except Exception as e:
            logger.error(f"Benchmark iteration {i} failed: {e}")
    
    total_time = time.time() - total_start
    latencies.sort()
    
    stats = {
        'min_ms': latencies[0] if latencies else 0,
        'max_ms': latencies[-1] if latencies else 0,
        'avg_ms': sum(latencies) / len(latencies) if latencies else 0,
        'p95_ms': latencies[int(len(latencies) * 0.95)] if latencies else 0,
        'p99_ms': latencies[int(len(latencies) * 0.99)] if latencies else 0,
        'total_time_s': total_time,
        'iterations': len(latencies)
    }
    
    logger.info(
        f"Benchmark complete: avg={stats['avg_ms']:.2f}ms, "
        f"p95={stats['p95_ms']:.2f}ms, p99={stats['p99_ms']:.2f}ms"
    )
    
    return stats


async def get_pool_health() -> Dict[str, Any]:
    """Get health status of connection pool."""
    pool = get_connection_pool()
    return await pool.health_check()


async def close_connection_pool():
    """Close the global connection pool."""
    global _connection_pool
    
    if _connection_pool is not None:
        await _connection_pool.close()
        _connection_pool = None
