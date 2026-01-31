# Lotus Backend Implementation Plan

## 🎯 Project Overview
**Lotus** is a RAG-based vaginal health scanning app that uses Supabase vector search and LLM integration to analyze period product ingredients and provide personalized health insights.

**Tech Stack:** Python FastAPI + Supabase + OpenAI/Gemini

---

## 🛠️ Phase 1: Environment & Backend Setup

**Goal:** Get your database and AI keys ready to talk to each other.

- [ ] Initialize Supabase project and enable vector extension
- [ ] Create profiles table schema (id, user_id, sensitivities[], scan_history)
- [ ] Create ingredients_library table schema (id, name, description, risk_level, embedding vector(1536))
- [ ] Obtain OpenAI or Gemini API keys
- [ ] Initialize Python FastAPI project structure
- [ ] Install core dependencies (supabase-py, langchain, openai, python-dotenv, fastapi, uvicorn)
- [ ] Create .env file with API keys and database credentials
- [ ] Set up Supabase client initialization and connection pooling

---

## 📚 Phase 2: Data Ingestion & Embedding Pipeline

**Goal:** Feed the "Ingredient Encyclopedia" into your Vector DB.

- [ ] Source or create CSV/JSON of period product ingredients with descriptions
- [ ] Build embedding script that processes each ingredient through text-embedding-3-small
- [ ] Implement batch upsert logic to Supabase ingredients_library table
- [ ] Create vector search utility function for ingredient similarity queries
- [ ] Test retrieval with sample queries (e.g., "scent" should return "Fragrance")
- [ ] Document data format and embedding specifications

---

## 📸 Phase 3: Scan Pipeline Backend Logic

**Goal:** Turn a photo of a box into a personalized health report.

- [ ] Implement Vision OCR endpoint using Gemini 2.0 Flash for ingredient list extraction
- [ ] Create prompt engineering module for accurate ingredient extraction
- [ ] Build vector search loop to match extracted ingredients against library
- [ ] Implement personalization engine to fetch user profile and sensitivities
- [ ] Create LLM call module for risk score generation (Low/Caution/High Risk)
- [ ] Build system prompt template for health expert context
- [ ] Create unified scan endpoint that orchestrates OCR → Vector Search → Personalization → Risk Score

---

## 🔌 Phase 4: API Endpoints & Data Models

**Goal:** Build the backend API contract for frontend integration.

- [ ] Define Pydantic models for API requests/responses (ScanRequest, ScanResult, IngredientMatch)
- [ ] Create POST /api/scan endpoint for image uploads
- [ ] Create POST /api/profiles endpoint for user sensitivity setup
- [ ] Create GET /api/profiles/{user_id} endpoint for profile retrieval
- [ ] Create GET /api/ingredients endpoint for ingredient library queries
- [ ] Add error handling and input validation across all endpoints
- [ ] Implement request logging and monitoring

---

## 🗄️ Phase 5: Database Optimization & Functions

**Goal:** Optimize queries for production performance.

- [ ] Create Supabase RPC function for optimized vector similarity search
- [ ] Set up database indexes on frequently queried columns
- [ ] Implement connection pooling for Supabase queries
- [ ] Create stored procedures for batch ingredient operations
- [ ] Test query performance under load

---

## 🧪 Phase 6: Testing & Quality Assurance

**Goal:** Ensure reliability and performance.

- [ ] Write unit tests for embedding generation
- [ ] Write integration tests for vector search logic
- [ ] Write end-to-end tests for complete scan pipeline
- [ ] Test error handling for invalid inputs
- [ ] Performance test vector search latency
- [ ] Create test data fixtures for development

---

## 🚀 Phase 7: Deployment & Production Setup

**Goal:** Make it production-ready.

- [ ] Configure backend for Supabase Edge Functions or Render deployment
- [ ] Set up environment variables for production
- [ ] Configure CORS for frontend communication
- [ ] Set up logging and error tracking (e.g., Sentry)
- [ ] Create deployment documentation
- [ ] Deploy backend and verify all endpoints are working

---

## 📋 Key Implementation Details

### System Prompt Template
```
System Prompt: 
You are a vaginal health expert. Use the provided context from our 
medical research database to evaluate the scanned ingredients.

Context: {retrieved_vector_data}
User Profile: {user_sensitivities}
Scanned Ingredients: {ocr_results}

Task:
1. Identify any ingredients that conflict with the user's profile.
2. Provide a score: Low Risk (Safe), Caution (Irritating), or High Risk (Harmful).
3. Explain the "Why" in 2 sentences using empathetic, clear language.
```

### API Response Format Example
```json
{
  "scan_id": "uuid",
  "overall_risk_level": "🟡 Caution",
  "ingredients_found": ["Fragrance", "Rayon", "Polyester"],
  "risky_ingredients": [
    {
      "name": "Fragrance",
      "risk_level": "High Risk",
      "explanation": "Fragrance can irritate sensitive vaginal tissue..."
    }
  ],
  "safer_swaps": [
    {"brand": "Honey Pot", "reason": "100% organic cotton"},
    {"brand": "August", "reason": "Hypoallergenic formulation"}
  ]
}
```

---

## 🔗 Resources
- Supabase Vector Docs: https://supabase.com/docs/guides/ai/vector-columns
- LangChain Documentation: https://python.langchain.com/
- FastAPI: https://fastapi.tiangolo.com/
- Gemini API: https://ai.google.dev/

---

**Last Updated:** 2026-01-31
