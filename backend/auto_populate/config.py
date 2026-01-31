"""
Configuration for auto-population pipeline
Separate from main backend config to avoid conflicts
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# Supabase config
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Period product brands to scrape
TOP_BRANDS = [
    "Always Ultra Thin",
    "Always Maxi",
    "Tampax Pearl Regular",
    "Tampax Pearl Super",
    "Kotex U Ultra Thin",
    "Kotex Security Regular",
    "Honey Pot Organic",
    "Natracare Organic",
    "Seventh Generation Free",
    "Cora Organic",
    "Rael Organic",
    "August Pads",
    "Veeda 100% Cotton",
    "Lola Organic",
    "The Honey Pot Company",
    "Organyc Organic",
    "Playtex Gentle Glide",
    "OB Tampons",
    "Carefree Panty Liners",
    "U by Kotex"
]

# PubMed API config
PUBMED_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
PUBMED_EMAIL = os.getenv("PUBMED_EMAIL", "research@lotus-health.app")

# Barcode API (for future: IronBarcode, BarcodeAPI)
BARCODE_API_KEY = os.getenv("BARCODE_API_KEY", "")

# Logging
LOG_LEVEL = "INFO"
