"""
Vercel Functions Entry Point - Serverless Handler for Lotus Backend
Wraps FastAPI app for Vercel's serverless environment
"""

import sys
from pathlib import Path

# Add parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app

# Export the FastAPI app directly for Vercel
# Vercel's Python runtime will automatically detect and use it
app = app
