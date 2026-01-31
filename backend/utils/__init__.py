"""
Utilities package for Lotus backend
"""

from .supabase_client import (
    initialize_supabase,
    get_supabase_client,
    test_connection,
    close_connection,
)

__all__ = [
    "initialize_supabase",
    "get_supabase_client",
    "test_connection",
    "close_connection",
]
