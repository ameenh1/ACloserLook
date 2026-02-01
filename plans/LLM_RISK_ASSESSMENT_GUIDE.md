# LLM Risk Assessment System - Deep Dive

## How the LLM Risk Assessment Works

### Architecture Overview

The risk assessment system uses a **multi-stage pipeline** that combines:
1. **Your curated ingredient database** (static, controlled data)
2. **Vector semantic search** (finds relevant ingredient information)
3. **User-specific sensitivities** (personalization)
4. **LLM analysis** (GPT-4o-mini for intelligent assessment)

```
User Scans Product
       ↓
Product Ingredients Identified
       ↓
┌──────────────────────────────────────────────────┐
│  Stage 1: Fetch User Profile                    │
│  - Query: SELECT sensitivities FROM profiles    │
│  - Returns: ["PCOS", "Sensitive Skin"]          │
└──────────────────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────────────┐
│  Stage 2: Vector Search (Semantic Context)      │
│  For each ingredient:                            │
│  - Generate embedding from ingredient name       │
│  - Search ingredients_library by similarity      │
│  - Retrieve top 3 matches with descriptions      │
│  - Includes: risk_level, description, research   │
└──────────────────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────────────┐
│  Stage 3: Construct LLM Prompt                   │
│  Combines:                                       │
│  - Product ingredients list                      │
│  - User sensitivities                            │
│  - Retrieved ingredient context from DB          │
└──────────────────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────────────┐
│  Stage 4: LLM Analysis (GPT-4o-mini)            │
│  System Prompt: Health expert in vaginal health │
│  Task: Analyze ingredients against sensitivities │
│  Output: Structured JSON with risk assessment    │
└──────────────────────────────────────────────────┘
       ↓
Final Risk Report Returned to User
```

---

## Critical Understanding: Knowledge Sources

### ❌ What the LLM Does NOT Have Access To:

**The LLM CANNOT access:**
- Real-time internet or new research papers
- PubMed database
- Recent studies published after its training cutoff
- Live medical databases
- External APIs during inference

**GPT-4o-mini training cutoff:** October 2023

This means the LLM's **built-in knowledge** is frozen at that date.

---

### ✅ What the LLM DOES Use for Assessment:

#### 1. **Your Curated Ingredient Database** (Primary Source)

**Location:** [`backend/data/ingredients.json`](../backend/data/ingredients.json)

This is your **controlled, expert-curated knowledge base**. Example:

```json
{
  "id": 1,
  "name": "Fragrance",
  "description": "Synthetic fragrance compounds used to mask odors in period products. May contain undisclosed chemicals that can trigger allergic reactions, skin irritation, and reproductive health concerns. Studies suggest fragrance additives increase risk of vulvovaginal irritation and bacterial imbalance.",
  "risk_level": "High"
}
```

**This is provided to the LLM in the prompt**, so it has access to:
- Your expert descriptions
- Risk level classifications (Low/Medium/High)
- Health impact information
- **Any research citations you include in the descriptions**

#### 2. **LLM's Pre-trained Knowledge** (Secondary Source)

The LLM has general knowledge about:
- Common chemicals and their properties
- Basic health/medical concepts
- Ingredient interactions
- General safety principles

**BUT:** This knowledge is static (frozen at October 2023) and may not include:
- Emerging research findings
- New ingredient discoveries
- Updated safety guidelines
- Recent studies

#### 3. **User Sensitivities** (Personalization)

From the `profiles` table:
```json
{
  "user_id": "user_123",
  "sensitivities": ["PCOS", "Sensitive Skin", "BV"]
}
```

The LLM uses this to **personalize** the assessment based on known conditions.

---

## How Risk Scores Are Generated

### The Prompt Structure

**System Prompt** (from [`backend/utils/prompts.py`](../backend/utils/prompts.py:7)):
```
You are a medical expert specializing in vaginal health and ingredient safety assessment.
Your role is to provide evidence-based health guidance...
```

**User Prompt Example:**
```
Based on the following information, assess the health risk level:

SCANNED INGREDIENTS:
Fragrance, Rayon, Polyester

USER SENSITIVITIES:
PCOS, Sensitive Skin

SIMILAR INGREDIENTS FROM KNOWLEDGE BASE:
- Fragrance: Synthetic fragrance compounds used to mask odors. 
  May trigger allergic reactions, skin irritation, and reproductive concerns. 
  (Risk Level: High)
- Rayon: Cellulose-based synthetic fiber. Can harbor bacteria and 
  reduce vaginal moisture. (Risk Level: High)
- Polyester: Petroleum-derived plastic polymer. Creates moisture-trapping 
  barrier, promotes yeast growth. (Risk Level: High)

ASSESSMENT TASK:
1. Evaluate each ingredient against user's sensitivities
2. Cross-reference with knowledge base
3. Consider synergistic effects
4. Provide overall risk level
```

### LLM Response Format

The LLM returns structured JSON:

```json
{
  "overall_risk_level": "High Risk (Harmful)",
  "explanation": "This product contains three high-risk ingredients that can disrupt vaginal pH and increase infection risk. Given your PCOS and sensitive skin, fragrances may exacerbate hormonal imbalances and cause severe irritation.",
  "ingredient_details": [
    {
      "name": "Fragrance",
      "risk_level": "High",
      "reason": "Known allergen and irritant. Can trigger immune response in sensitive individuals. May contain phthalates that disrupt hormones, particularly concerning for PCOS."
    },
    {
      "name": "Rayon",
      "risk_level": "High",
      "reason": "Absorbs moisture and can harbor bacteria, increasing risk of bacterial vaginosis which you're sensitive to."
    },
    {
      "name": "Polyester",
      "risk_level": "High",
      "reason": "Non-breathable material traps moisture and heat, creating environment for yeast overgrowth."
    }
  ],
  "recommendations": "Consider switching to organic cotton products without synthetic fragrances. Look for products specifically labeled for sensitive skin."
}
```

---

## Testing the Risk Assessment Endpoint

### Method 1: Using cURL (Command Line)

**Prerequisites:**
- Backend running locally or deployed to Vercel
- Valid barcode in your database
- User profile created with sensitivities

**Step 1: Create a Test User Profile**

```bash
curl -X POST http://localhost:8000/api/profiles \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "sensitivities": ["PCOS", "Sensitive Skin", "BV"]
  }'
```

**Step 2: Call Risk Assessment Endpoint**

```bash
curl -X POST http://localhost:8000/api/scan/barcode/assess \
  -H "Content-Type: application/json" \
  -d '{
    "barcode": "012345678901",
    "user_id": "test_user_123"
  }'
```

**Expected Response:**
```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "test_user_123",
  "product": {
    "id": 1,
    "brand_name": "Always Infinity Pads",
    "barcode": "012345678901",
    "ingredients": ["Polyester", "Rayon", "Fragrance"],
    "product_type": "pad",
    "coverage_score": 0.75,
    "research_count": 8
  },
  "overall_risk_level": "High Risk",
  "risky_ingredients": [
    {
      "name": "Fragrance",
      "risk_level": "High Risk",
      "reason": "Known allergen that can trigger allergic reactions..."
    }
  ],
  "explanation": "This product contains several potentially harmful ingredients. Consider alternatives with organic materials.",
  "timestamp": "2026-01-31T23:30:00Z"
}
```

---

### Method 2: Using Postman or Thunder Client (VS Code)

**1. Create New Request:**
- Method: `POST`
- URL: `http://localhost:8000/api/scan/barcode/assess`
- Headers: `Content-Type: application/json`

**2. Body (raw JSON):**
```json
{
  "barcode": "012345678901",
  "user_id": "test_user_123"
}
```

**3. Send Request** and inspect response

---

### Method 3: Python Script for Testing

Create [`backend/tests/test_risk_assessment_manual.py`](../backend/tests/test_risk_assessment_manual.py):

```python
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
BARCODE = "012345678901"
USER_ID = "test_user_123"

def test_risk_assessment():
    """Test the risk assessment endpoint"""
    
    # Step 1: Create test user profile
    print("Creating test user profile...")
    profile_response = requests.post(
        f"{BASE_URL}/api/profiles",
        json={
            "user_id": USER_ID,
            "sensitivities": ["PCOS", "Sensitive Skin", "BV"]
        }
    )
    print(f"Profile created: {profile_response.status_code}")
    
    # Step 2: Call risk assessment endpoint
    print(f"\nTesting risk assessment for barcode: {BARCODE}")
    assessment_response = requests.post(
        f"{BASE_URL}/api/scan/barcode/assess",
        json={
            "barcode": BARCODE,
            "user_id": USER_ID
        }
    )
    
    if assessment_response.status_code == 200:
        data = assessment_response.json()
        print("\n✅ Risk Assessment Successful!")
        print(f"\nProduct: {data['product']['brand_name']}")
        print(f"Risk Level: {data['overall_risk_level']}")
        print(f"\nExplanation: {data['explanation']}")
        print(f"\nRisky Ingredients ({len(data['risky_ingredients'])}):")
        for ingredient in data['risky_ingredients']:
            print(f"  - {ingredient['name']}: {ingredient['risk_level']}")
            print(f"    Reason: {ingredient['reason']}\n")
    else:
        print(f"\n❌ Error: {assessment_response.status_code}")
        print(assessment_response.text)

if __name__ == "__main__":
    test_risk_assessment()
```

Run with:
```bash
cd backend
python tests/test_risk_assessment_manual.py
```

---

## Getting Recent Research Data

### The Problem

**Your current system relies on:**
1. Static ingredient descriptions in `ingredients.json`
2. LLM's pre-trained knowledge (cutoff: October 2023)

**This means:**
- ❌ No automatic updates with new research
- ❌ No real-time PubMed integration
- ❌ No access to studies published after Oct 2023

---

### Solution Options

#### Option 1: Manual Curation (Current Approach)

**Process:**
1. Researcher reviews new studies manually
2. Updates [`backend/data/ingredients.json`](../backend/data/ingredients.json) descriptions
3. Adds research citations to descriptions
4. Runs [`backend/scripts/embed_ingredients.py`](../backend/scripts/embed_ingredients.py) to regenerate embeddings

**Pros:**
- Full control over quality
- Expert-vetted information
- No API rate limits or costs
- Stable, predictable results

**Cons:**
- Labor-intensive
- Can become outdated
- Requires domain expertise

**Example of Rich Description with Citations:**
```json
{
  "id": 1,
  "name": "Fragrance",
  "description": "Synthetic fragrance compounds used to mask odors in period products. May contain undisclosed chemicals that can trigger allergic reactions, skin irritation, and reproductive health concerns. Studies suggest fragrance additives increase risk of vulvovaginal irritation and bacterial imbalance. [Source: Scranton et al., 2022, Environmental Health Perspectives; Kim et al., 2021, Journal of Women's Health]",
  "risk_level": "High"
}
```

---

#### Option 2: PubMed API Integration (Advanced)

**Your app has groundwork for this:**
- [`backend/auto_populate/pubmed_enricher.py`](../backend/auto_populate/pubmed_enricher.py) - PubMed query tool
- [`backend/auto_populate/ingredient_matcher.py`](../backend/auto_populate/ingredient_matcher.py) - Ingredient matching

**How it would work:**

```python
# Periodic enrichment process (run weekly/monthly)
from auto_populate.pubmed_enricher import PubMedEnricher

enricher = PubMedEnricher()

# For each ingredient
for ingredient in ingredients:
    # Search PubMed for recent studies
    studies = enricher.search_studies(
        query=f"{ingredient.name} vaginal health safety",
        max_results=5,
        date_range="2023-2026"  # Recent studies only
    )
    
    # Extract key findings
    summaries = enricher.extract_summaries(studies)
    
    # Update ingredient description with citations
    ingredient.description += f"\n\nRecent Research: {summaries}"
    
    # Re-embed with updated information
    embedding = generate_embedding(ingredient.description)
    
    # Update database
    supabase.table('ingredients_library').update({
        'description': ingredient.description,
        'embedding': embedding,
        'last_updated': now()
    }).eq('id', ingredient.id).execute()
```

**Implementation Steps:**
1. Set up PubMed API access (free, requires registration)
2. Create scheduled job (cron/GitHub Actions)
3. Query PubMed for each ingredient
4. Use LLM to summarize findings
5. Update ingredient descriptions
6. Regenerate embeddings
7. Store update timestamp

**Pros:**
- Automated updates
- Access to latest research
- Scalable

**Cons:**
- PubMed API rate limits
- Requires NLP/summarization
- Quality control needed
- Additional LLM costs for summarization

---

#### Option 3: RAG with Live PubMed Search (Real-time)

**Most advanced approach - true Retrieval-Augmented Generation:**

```python
async def generate_risk_assessment_with_live_research(
    product_ingredients: list,
    user_sensitivities: list
):
    # Step 1: Vector search in your DB (fast)
    local_context = await search_similar_ingredients(product_ingredients)
    
    # Step 2: Query PubMed for each risky ingredient (slower)
    pubmed_context = []
    for ingredient in product_ingredients:
        recent_studies = await query_pubmed_api(
            query=f"{ingredient} vaginal health toxicity",
            max_results=3,
            date_from="2023-01-01"
        )
        pubmed_context.extend(recent_studies)
    
    # Step 3: Combine all context + user data
    comprehensive_prompt = f"""
    Assess these ingredients: {product_ingredients}
    User sensitivities: {user_sensitivities}
    
    Your ingredient database context:
    {local_context}
    
    Recent PubMed research (2023-2026):
    {pubmed_context}
    
    Provide risk assessment based on both sources.
    """
    
    # Step 4: LLM analysis with ALL context
    assessment = await call_llm(comprehensive_prompt)
    
    return assessment
```

**Pros:**
- Always uses latest research
- Combines curated knowledge + new data
- Most comprehensive assessments

**Cons:**
- Slow (multiple API calls per request)
- Expensive (PubMed queries + LLM tokens)
- Complex error handling
- Rate limit concerns
- May require caching

---

## Recommended Approach

### Hybrid Model (Best of Both Worlds)

**1. Foundation Layer: Curated Database (Current)**
- Maintain expert-curated ingredient descriptions
- Include well-established research citations
- Update quarterly with review of major studies
- This is your **reliable, fast baseline**

**2. Enhancement Layer: Periodic PubMed Enrichment**
- Run automated PubMed sync monthly
- Focus on high-risk ingredients
- LLM summarizes new findings
- Human reviews before merging
- Adds "Recent Research (2024-2026)" section to descriptions

**3. Cache Layer: Store Recent Assessments**
- Cache risk assessments per (product_id, user_sensitivity_hash)
- TTL: 30 days
- Reduces LLM calls and cost
- Still provides personalized results

**Implementation Priority:**
```
Phase 1 (Now): ✅ Use current curated database
Phase 2 (Next): Build PubMed enrichment pipeline
Phase 3 (Future): Add real-time RAG for edge cases
```

---

## Testing Checklist

Create [`plans/RISK_ASSESSMENT_TEST_PLAN.md`](../plans/RISK_ASSESSMENT_TEST_PLAN.md):

- [ ] **Test 1: Basic Assessment**
  - Product with low-risk ingredients
  - User with no sensitivities
  - Expected: Low Risk

- [ ] **Test 2: High-Risk Product**
  - Product with Fragrance, Phthalates, BPA
  - User with no sensitivities
  - Expected: High Risk

- [ ] **Test 3: Personalized Assessment**
  - Product with moderate-risk ingredients
  - User with PCOS, Sensitive Skin
  - Expected: Higher risk due to sensitivities

- [ ] **Test 4: Missing User Profile**
  - Valid product
  - Invalid user_id
  - Expected: Generic assessment or error

- [ ] **Test 5: Vector Search Validation**
  - Check that vector search returns relevant ingredients
  - Verify similarity scores are meaningful
  - Test with misspelled ingredient names

- [ ] **Test 6: LLM Response Parsing**
  - Verify JSON structure is valid
  - Check all required fields present
  - Test error handling for malformed responses

---

## Monitoring and Improvement

### Key Metrics to Track

**1. Assessment Quality:**
- User feedback on risk assessments
- False positive/negative rate
- Consistency across similar products

**2. Performance:**
- Average response time
- LLM token usage
- Vector search latency
- Cache hit rate

**3. Coverage:**
- % of ingredients with recent research
- Last update timestamp per ingredient
- Gaps in knowledge base

### Continuous Improvement Loop

```
User Scans Product
       ↓
Risk Assessment Generated
       ↓
User Provides Feedback (optional)
       ↓
Log Assessment + Feedback
       ↓
Weekly Analysis:
  - Which ingredients cause confusion?
  - Which assessments were disputed?
  - What research is missing?
       ↓
Update Ingredient Descriptions
       ↓
Re-train Embeddings
       ↓
Improved Future Assessments
```

---

## Summary

### How It Works Today:

1. **Data Source:** Your curated `ingredients.json` (185 ingredients with expert descriptions)
2. **Vector Search:** Finds similar ingredients using semantic embeddings
3. **LLM:** GPT-4o-mini analyzes based on provided context (NOT live research)
4. **Personalization:** Uses user sensitivities for tailored assessment
5. **Limitations:** LLM knowledge frozen at Oct 2023, no real-time PubMed access

### How to Test:

```bash
# 1. Start backend
cd backend
uvicorn main:app --reload

# 2. Create test profile
curl -X POST http://localhost:8000/api/profiles \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "sensitivities": ["PCOS"]}'

# 3. Test assessment
curl -X POST http://localhost:8000/api/scan/barcode/assess \
  -H "Content-Type: application/json" \
  -d '{"barcode": "012345678901", "user_id": "test_user"}'
```

### To Get Recent Research:

**Short-term:** Manually update ingredient descriptions with new citations

**Long-term:** Build PubMed enrichment pipeline using existing tools:
- [`backend/auto_populate/pubmed_enricher.py`](../backend/auto_populate/pubmed_enricher.py)
- [`backend/auto_populate/ingredient_matcher.py`](../backend/auto_populate/ingredient_matcher.py)

---

**Key Insight:** The LLM is **smart** but not **all-knowing**. Its power comes from:
1. Your curated, expert-vetted ingredient database (primary knowledge source)
2. Intelligent reasoning about ingredient interactions
3. Personalization based on user sensitivities

**It does NOT** have access to research published after October 2023 unless you explicitly provide it in the prompt via your database.

---

**Last Updated:** 2026-01-31
