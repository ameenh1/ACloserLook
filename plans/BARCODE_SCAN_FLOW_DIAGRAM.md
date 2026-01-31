# Visual Barcode Scan Flow Diagram

## Complete End-to-End Flow

```mermaid
graph TB
    Start([User Opens App]) --> Scanner[BarcodeScannerScreen]
    Scanner --> Camera{Camera Access?}
    Camera -->|Denied| Error1[Show Permission Error]
    Camera -->|Granted| Scanning[Html5Qrcode Active]
    
    Scanning --> Detect{Barcode Detected?}
    Detect -->|Yes| Stop[Stop Scanner]
    Detect -->|No| Scanning
    
    Stop --> Navigate[Navigate to ProductResultScreen]
    Navigate --> Loading[Show Loading State]
    Loading --> API[POST /api/scan/barcode]
    
    API --> Backend[FastAPI Router]
    Backend --> Validate{Valid Barcode?}
    Validate -->|No| Error2[400 Bad Request]
    Validate -->|Yes| DBQuery[Query Products Table]
    
    DBQuery --> Found{Product Found?}
    Found -->|No| Error3[404 Not Found]
    Found -->|Yes| Resolve[Resolve Ingredient IDs]
    
    Resolve --> IngQuery[Query Ingredients Library]
    IngQuery --> MapNames[Map IDs to Names]
    MapNames --> Response[Return Product Data]
    
    Response --> Display[Display Product Details]
    Display --> ShowBrand[Show Brand Name]
    Display --> ShowType[Show Product Type]
    Display --> ShowIngredients[List All Ingredients]
    Display --> ShowResearch[Research Coverage]
    
    ShowResearch --> Action[Scan Another Button]
    Action --> Scanner
    
    Error1 --> Retry1[Try Again Button]
    Error2 --> Back1[Back to Home]
    Error3 --> Retry2[Try Another Barcode]
    
    Retry1 --> Scanner
    Back1 --> Start
    Retry2 --> Scanner
    
    style Start fill:#e1f5e1
    style Display fill:#e1f5e1
    style Error1 fill:#ffe1e1
    style Error2 fill:#ffe1e1
    style Error3 fill:#ffe1e1
    style API fill:#e1e5ff
    style Backend fill:#e1e5ff
```

## Risk Assessment Flow (Advanced Path)

```mermaid
graph TB
    Start([Barcode Scanned]) --> CheckUser{User Logged In?}
    CheckUser -->|No| Simple[Simple Lookup Path]
    CheckUser -->|Yes| Advanced[POST /api/scan/barcode/assess]
    
    Simple --> SimpleDB[Query Products Only]
    SimpleDB --> SimpleDisplay[Display Basic Info]
    
    Advanced --> Step1[Step 1: Lookup Product]
    Step1 --> Step2[Step 2: Fetch User Profile]
    Step2 --> GetSensitivities[Load User Sensitivities]
    GetSensitivities --> Step3[Step 3: Vector Search]
    
    Step3 --> Loop{For Each Ingredient}
    Loop -->|Next| Embed[Generate Query Embedding]
    Embed --> VectorSearch[Supabase Vector Similarity]
    VectorSearch --> Context[Collect Research Context]
    Context --> Loop
    Loop -->|Done| Step4[Step 4: LLM Risk Assessment]
    
    Step4 --> PrepPrompt[Prepare Comprehensive Prompt]
    PrepPrompt --> PromptContent[Ingredients + Sensitivities + Research]
    PromptContent --> CallLLM[OpenAI GPT-4o-mini]
    CallLLM --> ParseJSON[Parse JSON Response]
    
    ParseJSON --> Extract[Extract Risk Data]
    Extract --> RiskLevel[Overall Risk Level]
    Extract --> RiskyList[Risky Ingredients List]
    Extract --> Explanation[Personalized Explanation]
    
    RiskLevel --> Format[Step 5: Format Response]
    RiskyList --> Format
    Explanation --> Format
    
    Format --> Return[Return to Frontend]
    Return --> DisplayRisk[Display Risk Assessment]
    
    DisplayRisk --> ShowRiskBadge[Risk Level Badge]
    DisplayRisk --> ShowRiskyIngredients[Risky Ingredients Accordion]
    DisplayRisk --> ShowExplanation[Personalized Explanation]
    DisplayRisk --> ShowRecommendations[Health Recommendations]
    
    style Start fill:#e1f5e1
    style DisplayRisk fill:#e1f5e1
    style Simple fill:#fff4e1
    style Advanced fill:#e1e5ff
    style CallLLM fill:#ffe1f5
    style VectorSearch fill:#ffe1f5
```

## Data Ingestion Pipeline

```mermaid
graph LR
    JSON[ingredients.json<br/>185 ingredients] --> Load[Load JSON File]
    Load --> Parse[Parse Ingredients]
    Parse --> Loop{For Each Ingredient}
    
    Loop -->|Next| Combine[Combine Name + Description]
    Combine --> OpenAI[OpenAI API<br/>text-embedding-3-small]
    OpenAI --> Vector[1536-dim Vector]
    Vector --> Batch[Add to Batch]
    Batch --> Loop
    
    Loop -->|Done| Upsert[Batch Upsert to Supabase]
    Upsert --> DB[(Supabase<br/>ingredients_library)]
    
    DB --> Ready[Ready for Vector Search]
    
    style JSON fill:#fff4e1
    style OpenAI fill:#ffe1f5
    style DB fill:#e1e5ff
    style Ready fill:#e1f5e1
```

## Database Schema Relationships

```mermaid
erDiagram
    PRODUCTS ||--o{ INGREDIENTS_LIBRARY : contains
    PROFILES ||--o{ SCAN_HISTORY : performs
    SCAN_HISTORY }o--|| PRODUCTS : scans
    
    PRODUCTS {
        int id PK
        text brand_name
        text barcode UK
        int_array ingredients FK
        text product_type
        float coverage_score
        int research_count
        timestamp created_at
    }
    
    INGREDIENTS_LIBRARY {
        int id PK
        text name
        text description
        text risk_level
        vector_1536 embedding
        timestamp created_at
    }
    
    PROFILES {
        text id PK
        text_array sensitivities
        timestamp created_at
        timestamp updated_at
    }
    
    SCAN_HISTORY {
        int id PK
        text user_id FK
        int product_id FK
        text risk_level
        json assessment
        timestamp scanned_at
    }
```

## Technology Stack Layers

```mermaid
graph TB
    subgraph Frontend Layer
        UI[React + TypeScript]
        Scanner[Html5Qrcode]
        State[State Management]
    end
    
    subgraph API Layer
        FastAPI[FastAPI Backend]
        Routes[API Routes]
        Middleware[CORS + Logging]
    end
    
    subgraph Business Logic
        BarcodeLogic[Barcode Lookup]
        RiskLogic[Risk Assessment]
        VectorLogic[Vector Search]
    end
    
    subgraph AI Services
        OpenAI[OpenAI API]
        Embeddings[text-embedding-3-small]
        LLM[GPT-4o-mini]
    end
    
    subgraph Data Layer
        Supabase[(Supabase PostgreSQL)]
        Vector[pgvector Extension]
    end
    
    UI --> FastAPI
    Scanner --> Routes
    Routes --> BarcodeLogic
    Routes --> RiskLogic
    BarcodeLogic --> Supabase
    RiskLogic --> VectorLogic
    VectorLogic --> Embeddings
    VectorLogic --> Vector
    RiskLogic --> LLM
    Embeddings --> OpenAI
    LLM --> OpenAI
    Vector --> Supabase
    
    style UI fill:#e1f5e1
    style FastAPI fill:#e1e5ff
    style OpenAI fill:#ffe1f5
    style Supabase fill:#fff4e1
```

## Request/Response Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant FastAPI
    participant Supabase
    participant OpenAI
    
    User->>Frontend: Scans Barcode
    Frontend->>Frontend: Html5Qrcode detects code
    Frontend->>FastAPI: POST /api/scan/barcode
    Note over Frontend,FastAPI: { barcode: "012345678901" }
    
    FastAPI->>FastAPI: Validate barcode
    FastAPI->>Supabase: Query products table
    Supabase-->>FastAPI: Product with ingredient IDs
    
    FastAPI->>Supabase: Query ingredients_library
    Supabase-->>FastAPI: Ingredient names
    
    FastAPI->>FastAPI: Map IDs to names
    FastAPI-->>Frontend: Product data
    Note over FastAPI,Frontend: { found: true, product: {...} }
    
    Frontend->>User: Display product details
    
    alt Risk Assessment Path
        User->>Frontend: Request risk assessment
        Frontend->>FastAPI: POST /api/scan/barcode/assess
        Note over Frontend,FastAPI: { barcode: "...", user_id: "..." }
        
        FastAPI->>Supabase: Fetch user sensitivities
        Supabase-->>FastAPI: User profile
        
        FastAPI->>OpenAI: Generate embeddings for ingredients
        OpenAI-->>FastAPI: Embedding vectors
        
        FastAPI->>Supabase: Vector similarity search
        Supabase-->>FastAPI: Research context
        
        FastAPI->>OpenAI: Risk assessment prompt
        Note over FastAPI,OpenAI: Ingredients + Context + Sensitivities
        OpenAI-->>FastAPI: Risk analysis JSON
        
        FastAPI-->>Frontend: Full risk assessment
        Frontend->>User: Display personalized risk report
    end
```

## Current vs Future State

```mermaid
graph LR
    subgraph Current Implementation
        C1[Barcode Scanner] --> C2[Simple Lookup]
        C2 --> C3[Display Product Info]
        C3 --> C4[Basic Ingredient List]
    end
    
    subgraph Future Implementation
        F1[Barcode Scanner] --> F2[User Authentication]
        F2 --> F3[Risk Assessment]
        F3 --> F4[Personalized Report]
        F4 --> F5[Risk Level Badge]
        F4 --> F6[Risky Ingredients]
        F4 --> F7[Health Recommendations]
        F4 --> F8[Alternative Products]
    end
    
    C4 -.Upgrade Path.-> F2
    
    style C1 fill:#fff4e1
    style C2 fill:#fff4e1
    style C3 fill:#fff4e1
    style C4 fill:#fff4e1
    style F1 fill:#e1f5e1
    style F2 fill:#e1f5e1
    style F3 fill:#e1f5e1
    style F4 fill:#e1f5e1
```

---

**Legend:**
- 🟢 Green: Start/Success states
- 🔵 Blue: API/Backend operations
- 🟡 Yellow: Simple path/Basic features
- 🔴 Red: Error states
- 🟣 Purple: AI/ML operations

**Last Updated:** 2026-01-31
