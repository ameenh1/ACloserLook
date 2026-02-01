"""
Vercel Functions Entry Point - Serverless Handler for Lotus Backend
Exports FastAPI app for Vercel's Python runtime
"""

import sys
from pathlib import Path

# Add parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import and re-export the FastAPI app
from main import app

# Vercel's Python runtime expects the app to be directly accessible
# No custom handler needed - just export the app object
__all__ = ['app']
