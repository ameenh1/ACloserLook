# Lotus Ingredient Database Expansion Guide

## 📊 Overview

This guide helps you scale from 30 ingredients to 500+ for comprehensive product coverage. Your current infrastructure supports unlimited ingredients—this is purely a data acquisition problem.

---

## 🎯 Why Scaling Matters

**Current State:** 30 core ingredients (sufficient for MVP demo)
- Covers 80% of major brand products
- Vector embeddings handle semantic matching for unknowns

**Post-MVP Goal:** 200-500 ingredients
- Covers 95%+ of all period products on market
- Reduces "unknown ingredient" fallback scenarios
- Improves user trust and app accuracy

**Long-term:** 1000+ ingredients
- Industry-leading coverage
- Becomes a competitive moat
- Attracts B2B partnerships

---

## 📚 Data Sources (Ranked by Ease)

### Tier 1: Easy (No API Required)

#### 1. **SmartLabel by P&G** (90 ingredients)
**URL:** https://www.smartlabel.org/

**Coverage:** Procter & Gamble brands (Always, Tampax, Kotex - ~60% market share)

**How to Extract:**
```bash
# Manual for MVP, but scrapeable with Selenium
# SmartLabel UI: Search → Product → Ingredients
```

**Cost:** Free
**Time:** 3-4 hours (manual) | 30 mins (with scraper)

---

#### 2. **EWG Skin Deep Database** (300+ ingredients)
**URL:** https://www.ewg.org/skindeep/

**Coverage:** Personal care products (many ingredients overlap with period products)

**API Access:**
```python
# EWG API endpoint (if available)
# Check https://www.ewg.org/api/ for current availability
import requests

def fetch_ewg_ingredients():
    """Fetch from EWG database"""
    # Note: Verify current API status, may require scraping
    url = "https://www.ewg.org/api/ingredients"
    # Requires investigation for current access method
    pass
```

**Cost:** Free
**Time:** 2-3 hours

---

#### 3. **Women's Voices for the Earth Database**
**URL:** https://www.womensvoices.org/

**Coverage:** Curated femtech-specific ingredients with health impact data

**Data Format:** Often available as downloadable spreadsheets/PDFs

**Cost:** Free
**Time:** 1-2 hours (data cleaning)

---

### Tier 2: Medium (Web Scraping Required)

#### 4. **Retailer Specifications** (150-200 ingredients)

**Target Sites:**
- **Target.com** - Specifications tab
- **Walmart.com** - Product details
- **Amazon.com** - Ingredient lists

**Scraping Stub:**
```python
# backend/scripts/scrapers/retailer_scraper.py

import requests
from bs4 import BeautifulSoup
import json
from typing import List, Dict

class RetailerScraper:
    """Scrape ingredients from major retailers"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_walmart_ingredients(self, product_url: str) -> Dict:
        """
        Extract ingredients from Walmart product page
        
        Example URL: https://www.walmart.com/ip/Always-Ultra-Thin-Pads.../123456
        """
        try:
            response = requests.get(product_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find specifications section
            specs = soup.find('div', {'class': 'specifications'})
            if not specs:
                return {"error": "Specifications not found"}
            
            ingredients = []
            # Parse ingredient list from specs
            ingredient_text = specs.get_text()
            # Clean and split
            for item in ingredient_text.split(','):
                clean_item = item.strip()
                if clean_item:
                    ingredients.append(clean_item)
            
            return {
                "product_url": product_url,
                "ingredients": ingredients,
                "source": "walmart"
            }
        except Exception as e:
            print(f"Error scraping {product_url}: {str(e)}")
            return {"error": str(e)}
    
    def scrape_target_ingredients(self, product_id: str) -> Dict:
        """
        Extract ingredients from Target product page
        
        Target API is more accessible than Walmart
        """
        target_api_url = f"https://redsky.target.com/v2/pdp/tcin/{product_id}"
        
        try:
            response = requests.get(target_api_url, timeout=10)
            data = response.json()
            
            # Extract from product details
            product = data.get('product', {})
            ingredients = product.get('ingredients', [])
            
            return {
                "product_id": product_id,
                "ingredients": ingredients,
                "source": "target"
            }
        except Exception as e:
            print(f"Error scraping Target {product_id}: {str(e)}")
            return {"error": str(e)}
    
    def scrape_amazon_ingredients(self, asin: str) -> Dict:
        """
        Extract ingredients from Amazon product page (ASIN)
        
        ASIN format: B0000ABC12
        """
        amazon_url = f"https://www.amazon.com/dp/{asin}"
        
        try:
            # Amazon blocks basic requests; use with caution
            response = requests.get(amazon_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find ingredient information (location varies by product)
            details = soup.find('div', {'id': 'feature-bullets'})
            if not details:
                details = soup.find('div', {'id': 'a-expander-content'})
            
            if details:
                ingredients = details.get_text()
                return {
                    "asin": asin,
                    "ingredients": ingredients,
                    "source": "amazon"
                }
            
            return {"error": "Ingredients not found"}
        except Exception as e:
            print(f"Error scraping Amazon {asin}: {str(e)}")
            return {"error": str(e)}


# Usage
if __name__ == "__main__":
    scraper = RetailerScraper()
    
    # Example: Scrape Walmart Always Pads
    result = scraper.scrape_walmart_ingredients(
        "https://www.walmart.com/ip/Always-Ultra-Thin-Pads/123456"
    )
    print(json.dumps(result, indent=2))
```

**Cost:** Free (but may violate TOS)
**Time:** 4-6 hours (with manual review for quality)

**Note:** Web scraping may violate retailer terms of service. Consider contacting retailers directly for data access instead.

---

### Tier 3: Hard (API Access)

#### 5. **FoodData Central (USDA)** - For additives
**URL:** https://fdc.nal.usda.gov/

```python
# Many ingredients are food additives regulated by FDA
# Can cross-reference for ingredient safety data

import requests

def lookup_ingredient_safety(ingredient_name: str):
    """Look up ingredient in FDA/USDA databases"""
    fdc_api_url = "https://fdc.nal.usda.gov/api/foods/search"
    params = {
        "query": ingredient_name,
        "pageSize": 5
    }
    
    try:
        response = requests.get(fdc_api_url, params=params)
        return response.json()
    except Exception as e:
        print(f"Error querying FDC: {str(e)}")
        return None
```

---

## 🛠️ Implementation Roadmap

### Phase 1: Data Consolidation (Week 1)
1. Manually extract 50-75 ingredients from SmartLabel
2. Compile Women's Voices dataset
3. Review EWG database for overlaps
4. Create master CSV with format matching `backend/data/ingredients.json`

### Phase 2: Automation (Week 2-3)
1. Build retailer scraper (Tier 2)
2. Deduplicate ingredients across sources
3. Standardize ingredient names (e.g., "sodium carboxymethyl cellulose" = "CMC")
4. Run embedding generation for new ingredients

### Phase 3: Validation (Week 3-4)
1. QA check: Ensure all 200+ ingredients have descriptions
2. Test vector search with new ingredients
3. Verify risk levels are accurate
4. Manual review of high-risk ingredients

### Phase 4: Deployment (Week 4)
1. Upsert new ingredients to Supabase
2. Update frontend ingredient browsing UI
3. Monitor vector search performance
4. Gather user feedback

---

## 📋 Data Format

Your expansion data should follow this JSON structure:

```json
[
  {
    "id": 31,  // Continue from 30
    "name": "Sodium Carboxymethyl Cellulose",
    "description": "A synthetic polymer used as a thickening agent in period products. Generally recognized as safe but may cause irritation in sensitive individuals with prolonged contact.",
    "risk_level": "Low",
    "aliases": ["CMC", "Carboxymethyl cellulose sodium", "Cellulose gum"]
  },
  {
    "id": 32,
    "name": "Phthalates",
    "description": "Plasticizers used in fragrances. May disrupt hormonal balance and accumulate in body tissues with chronic exposure. Banned in EU products but still used in US.",
    "risk_level": "High",
    "aliases": ["Diethyl phthalate", "DBP", "DEP"]
  }
]
```

**Required Fields:**
- `id` - Unique integer (increment from 30)
- `name` - Ingredient name (must be unique)
- `description` - 2-3 sentences about health impacts
- `risk_level` - "Low", "Medium", or "High"
- `aliases` - Alternative names for vector search matching (optional but recommended)

---

## 🔄 Embedding Generation for New Ingredients

Once you have 200+ ingredients, run:

```bash
cd backend
python scripts/embed_ingredients.py
```

This will:
1. Load `backend/data/ingredients.json`
2. Generate OpenAI embeddings for all descriptions
3. Upsert to Supabase `ingredients_library` table
4. **Cost:** ~$0.05-0.10 for 200 ingredients

---

## 📊 Deduplication Strategy

When combining data from multiple sources, use this logic:

```python
# backend/scripts/deduplicate_ingredients.py

from difflib import SequenceMatcher
import json

def are_duplicates(name1: str, name2: str, threshold: float = 0.85) -> bool:
    """
    Check if two ingredient names are likely duplicates
    Uses string similarity matching
    """
    ratio = SequenceMatcher(None, name1.lower(), name2.lower()).ratio()
    return ratio >= threshold

def merge_ingredient_sources(source1: list, source2: list) -> list:
    """
    Merge ingredients from two sources, removing duplicates
    """
    merged = source1.copy()
    
    for item2 in source2:
        is_duplicate = False
        
        for item1 in merged:
            if are_duplicates(item1['name'], item2['name']):
                # Merge: keep highest risk level
                if item2.get('risk_level') == 'High':
                    item1['risk_level'] = 'High'
                
                # Combine aliases
                if 'aliases' in item2:
                    if 'aliases' not in item1:
                        item1['aliases'] = []
                    item1['aliases'].extend(item2['aliases'])
                
                is_duplicate = True
                break
        
        if not is_duplicate:
            merged.append(item2)
    
    return merged


# Usage
with open('smartlabel_ingredients.json') as f:
    smartlabel = json.load(f)

with open('ewg_ingredients.json') as f:
    ewg = json.load(f)

merged = merge_ingredient_sources(smartlabel, ewg)

# Remove true duplicates
unique_ingredients = []
seen_names = set()

for ing in merged:
    if ing['name'].lower() not in seen_names:
        unique_ingredients.append(ing)
        seen_names.add(ing['name'].lower())

print(f"After dedup: {len(unique_ingredients)} unique ingredients")
```

---

## 🤝 Community/Partnership Approach

**Lower-effort alternative to scraping:**

1. **Contact manufacturers directly** - Most have transparency pages
2. **Reach out to Women's Voices** - They may share raw data
3. **Partner with universities** - Research institutions have ingredient databases
4. **Leverage GitHub community** - Create a public ingredient dataset contributors can submit to

---

## ⚠️ Important Considerations

### Data Accuracy
- **Verify all risk levels** - This is health data
- **Cross-reference with medical sources** - Don't rely solely on one database
- **Get legal review** - Health claims require compliance

### Rate Limiting
- Space out web requests to avoid IP blocking
- Use delays between requests (2-5 seconds)
- Rotate user agents

### Legal/Ethical
- Respect robots.txt and Terms of Service
- Consider asking retailers for data access permission first
- Don't republish proprietary ingredient lists without permission

---

## 📈 Success Metrics

After expansion, track:
- **Vector search accuracy:** Does "Polyethylene" match "Polyethylene glycol"?
- **Coverage:** What % of scanned products have known ingredients?
- **User satisfaction:** Do users find the ingredient database helpful?

---

## 🚀 Next Steps

1. **This week:** Manually collect 50 ingredients from SmartLabel
2. **Next week:** Build and test retailer scraper
3. **Week 3:** Deduplicate and standardize naming
4. **Week 4:** Generate embeddings and deploy

Your infrastructure is ready—this is purely execution on data gathering.

---

**Questions?** Check existing documentation:
- [`backend/EMBEDDING_GUIDE.md`](backend/EMBEDDING_GUIDE.md) - How embeddings work
- [`backend/database/README.md`](backend/database/README.md) - Database schema
- [`backend/scripts/embed_ingredients.py`](backend/scripts/embed_ingredients.py) - Embedding script
