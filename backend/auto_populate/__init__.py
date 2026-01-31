"""
Auto-population module for Lotus
Automates product data collection, ingredient matching, and research enrichment
"""

from .ingredient_matcher import IngredientMatcher
from .pubmed_enricher import PubMedResearchEnricher
from .populate_products import ProductPopulator

__all__ = [
    "IngredientMatcher",
    "PubMedResearchEnricher",
    "ProductPopulator"
]
