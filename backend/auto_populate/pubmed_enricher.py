"""
Automatically enrich ingredients with PubMed research data
"""

import json
import logging
import requests
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PubMedResearchEnricher:
    """Fetch and summarize research for ingredients"""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def __init__(self, email: str = "research@lotus-health.app"):
        self.email = email
    
    def search_studies(self, ingredient_name: str, max_results: int = 5) -> List[Dict]:
        """
        Search PubMed for studies related to ingredient and menstrual health
        
        Returns:
            [
                {
                    "title": "Study Title",
                    "authors": "Author List",
                    "pubmed_id": "12345678",
                    "url": "https://pubmed.ncbi.nlm.nih.gov/12345678/",
                    "year": 2023
                },
                ...
            ]
        """
        # Search query: ingredient + menstrual/vaginal/period product related
        query = f"({ingredient_name} OR \"{ingredient_name}\") AND (menstrual OR vaginal OR period OR dysmenorrhea OR endometriosis)"
        
        try:
            # Step 1: Search for matching papers
            search_url = f"{self.BASE_URL}/esearch.fcgi"
            search_params = {
                "db": "pubmed",
                "term": query,
                "retmax": max_results,
                "rettype": "json",
                "email": self.email
            }
            
            logger.info(f"Searching PubMed for: {ingredient_name}")
            search_response = requests.get(search_url, params=search_params, timeout=10)
            search_response.raise_for_status()
            
            search_data = search_response.json()
            pubmed_ids = search_data.get("esearchresult", {}).get("idlist", [])
            
            if not pubmed_ids:
                logger.warning(f"No PubMed results for {ingredient_name}")
                return []
            
            # Step 2: Fetch details for each result
            fetch_url = f"{self.BASE_URL}/efetch.fcgi"
            fetch_params = {
                "db": "pubmed",
                "id": ",".join(pubmed_ids),
                "rettype": "abstract",
                "retmode": "json",
                "email": self.email
            }
            
            fetch_response = requests.get(fetch_url, params=fetch_params, timeout=10)
            fetch_response.raise_for_status()
            
            fetch_data = fetch_response.json()
            articles = fetch_data.get("result", {}).get("uids", [])
            
            results = []
            for uid in articles:
                article = fetch_data["result"][uid]
                
                # Extract relevant info
                title = article.get("title", "")
                authors = article.get("authors", [])
                author_names = ", ".join([a.get("name", "") for a in authors[:3]])  # First 3 authors
                year = int(article.get("pubdate", "2000").split()[0][-4:]) if article.get("pubdate") else 2000
                
                results.append({
                    "title": title,
                    "authors": author_names,
                    "pubmed_id": uid,
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
                    "year": year
                })
                
                logger.info(f"✓ Found: {title[:60]}... ({year})")
            
            return results
        
        except requests.exceptions.RequestException as e:
            logger.error(f"PubMed API error: {str(e)}")
            return []
    
    def enrich_ingredient(self, ingredient: Dict) -> Dict:
        """
        Add PubMed research links to an ingredient
        
        Returns:
            ingredient dict with added 'research_studies' field
        """
        studies = self.search_studies(ingredient['name'], max_results=3)
        
        ingredient['research_studies'] = studies
        ingredient['research_count'] = len(studies)
        ingredient['last_enriched'] = datetime.now().isoformat()
        
        return ingredient
    
    def enrich_batch(self, ingredients: List[Dict]) -> List[Dict]:
        """Enrich multiple ingredients with research data"""
        enriched = []
        
        for idx, ingredient in enumerate(ingredients, 1):
            logger.info(f"[{idx}/{len(ingredients)}] Enriching {ingredient['name']}...")
            enriched_ing = self.enrich_ingredient(ingredient)
            enriched.append(enriched_ing)
        
        return enriched


# Usage example
if __name__ == "__main__":
    enricher = PubMedResearchEnricher()
    
    # Test with sample ingredients
    test_ingredients = [
        {
            "id": 1,
            "name": "Fragrance",
            "description": "Synthetic scent compounds",
            "risk_level": "High"
        },
        {
            "id": 2,
            "name": "Rayon",
            "description": "Viscose fiber from wood pulp",
            "risk_level": "Low"
        }
    ]
    
    enriched = enricher.enrich_batch(test_ingredients)
    print(json.dumps(enriched, indent=2))
