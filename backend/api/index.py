"""
Vercel Functions Entry Point - Serverless Handler for Lotus Backend
Wraps FastAPI app for Vercel's serverless environment
"""

import sys
import os
from pathlib import Path

# Add parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app

# Export the FastAPI app as ASGI handler for Vercel
async def handler(scope, receive, send):
    """
    ASGI handler for Vercel Functions
    Routes all requests through FastAPI app
    """
    await app(scope, receive, send)
