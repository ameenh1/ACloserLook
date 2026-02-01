# Risk Score Circular Indicator Enhancement Plan

## Problem Statement

After scanning a barcode, the risk score display has several issues:
1. The score is invisible or hard to see
2. The score text color is hardcoded to yellow regardless of risk level
3. The circular indicator needs better visual design with color coding
4. No actual numeric score from backend (only categorical: Low/Caution/High)

## Current State Analysis

### Backend
- [`risk_scorer.py`](../backend/utils/risk_scorer.py) only returns categorical risk levels
- No numeric score (0-100) calculation exists
- Response includes: `risk_level`, `explanation`, `risky_ingredients`

### Frontend
- [`ProductResultScreen.tsx`](../frontend/src/components/ProductResultScreen.tsx:306-329) has hardcoded placeholder scores
  - Low Risk: 85
  - Caution: 55
  - High Risk: 25
- Score text hardcoded to `text-yellow-400` (line 313)
- Basic circle design without progress indicator

## Solution Architecture

### Score Calculation Logic

**LLM-Generated Score (Primary Approach)**

The LLM will calculate and provide a numeric score (0-100) in its JSON response, considering:
- Individual ingredient risk levels (High Risk: -8 points, Medium Risk: -4 points)
- Synergistic effects between ingredients
- User sensitivities and health profile
- Ingredient concentrations (when available)
- Overall product formulation safety

**Score Ranges**:
- **71-100**: "Low Risk" (Green #4ade80)
- **41-70**: "Caution" (Yellow #facc15)
- **0-40**: "High Risk" (Red #f87171)

**Fallback Calculation** (if LLM doesn't provide score):
```
Base Score = 100

For each risky ingredient:
  - High Risk ingredient: -8 points
  - Medium/Caution ingredient: -4 points
  
Minimum Score = 0 (floor)
Maximum Score = 100 (ceiling)
```

### Visual Design Specification

**Circular Progress Indicator**:
- Outer diameter: 80px
- Border width: 6px  
- SVG-based circular progress bar
- Animated fill based on score percentage
- Score number centered (large, bold, colored)
- Label underneath the circle
- Smooth color transitions

**Color Coding**:
- Green (#4ade80): 71-100 points
- Yellow (#facc15): 41-70 points
- Red (#f87171): 0-40 points

## Implementation Steps

### 1. Backend: Add Numeric Risk Score to risk_scorer.py

**File**: `backend/utils/risk_scorer.py`

**Changes**:
- Add `_calculate_risk_score()` function after line 444
- Modify `generate_risk_score_for_product()` to include score in response
- Update response dict to include `risk_score` field

**Logic**:
```python
def _calculate_risk_score(risky_ingredients: List[Dict[str, str]]) -> int:
    """
    Calculate numeric risk score (0-100) based on risky ingredients
    FALLBACK ONLY - LLM should provide score in response
    
    Args:
        risky_ingredients: List of risky ingredients with risk_level
        
    Returns:
        Score from 0 (most risky) to 100 (safest)
    """
    base_score = 100
    
    for ingredient in risky_ingredients:
        risk_level = ingredient.get('risk_level', '').lower()
        
        if 'high' in risk_level:
            base_score -= 8
        elif 'medium' in risk_level or 'caution' in risk_level:
            base_score -= 4
    
    # Ensure score stays within bounds
    return max(0, min(100, base_score))
```

**Primary approach**: Extract `risk_score` from LLM response if available, fall back to calculation if not provided.

### 2. Backend: Update LLM Prompt to Request Score

**File**: `backend/utils/prompts.py`

**Changes**:
- Modify `RISK_ASSESSMENT_PROMPT` (line 28-65) to request `risk_score` field
- Add guidance for LLM on score calculation (-8 for High Risk, -4 for Medium/Caution)
- Provide clear instructions that score should be 0-100 (100 = safest)
- Update JSON response structure to include numeric score

**Updated JSON Structure**:
```json
{
    "overall_risk_level": "Low Risk (Safe)" | "Caution (Irritating)" | "High Risk (Harmful)",
    "risk_score": 85,
    "explanation": "Brief 2-sentence explanation",
    "ingredient_details": [
        {
            "name": "ingredient name",
            "risk_level": "Low" | "Medium" | "High",
            "reason": "Why this ingredient poses this risk level"
        }
    ],
    "recommendations": "Actionable advice"
}
```

**LLM Scoring Instructions to Add**:
```
RISK SCORE CALCULATION (0-100, where 100 is safest):
- Start with base score of 100
- Subtract 8 points for each High Risk ingredient
- Subtract 4 points for each Medium Risk ingredient
- Consider synergistic effects and user sensitivities
- Final score should align with overall_risk_level:
  * 71-100: Low Risk (Safe)
  * 41-70: Caution (Irritating)
  * 0-40: High Risk (Harmful)
```

### 3. Backend API: Update scan.py Response

**File**: `backend/routers/scan.py`

**Changes**:
- Modify `/scan/barcode/assess` endpoint (line 98-204)
- Add `risk_score` to response dict (line 183-192)

### 4. Frontend: Create Circular Progress Component

**New File**: `frontend/src/components/CircularRiskScore.tsx`

**Features**:
- Accepts `score` (0-100) and `isLoading` props
- SVG-based circular progress indicator
- Dynamic color based on score range
- Smooth animation on mount
- Displays score number and label

**Component Structure**:
```tsx
interface CircularRiskScoreProps {
  score: number;
  isLoading?: boolean;
}

export function CircularRiskScore({ score, isLoading }: CircularRiskScoreProps)
```

### 5. Frontend: Update ProductResultScreen.tsx

**File**: `frontend/src/components/ProductResultScreen.tsx`

**Changes**:
- Add `risk_score?: number` to `AssessmentData` interface (line 24)
- Update `getSafetyDisplay()` to accept score parameter (line 156)
- Remove hardcoded scores (lines 165, 174, 183)
- Use actual score from `assessmentData.risk_score`
- Update score text color to match risk level (line 313-318)
- Replace circle implementation (lines 306-329) with new component

### 6. Frontend: Add CSS Animations

**File**: `frontend/src/components/ProductResultScreen.css`

**New Styles**:
```css
@keyframes circular-progress {
  from {
    stroke-dashoffset: 282.6; /* circumference */
  }
  to {
    stroke-dashoffset: var(--progress-offset);
  }
}

.circular-progress-ring {
  transition: stroke 0.3s ease;
  animation: circular-progress 1s ease-out forwards;
}

@keyframes pulse-danger {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.risk-score-high {
  animation: pulse-danger 2s infinite;
}
```

### 7. TypeScript Type Updates

**Interface Updates**:
```typescript
interface AssessmentData {
  scan_id: string;
  user_id: string;
  product: ProductData;
  overall_risk_level: string;
  risk_score?: number; // NEW
  risky_ingredients: RiskyIngredient[];
  explanation: string;
  timestamp: string;
}
```

## Expected Behavior

### User Experience Flow

1. **Barcode Scan**: User scans a product barcode
2. **Initial Load**: Skeleton loader appears in circle position
3. **Basic Data**: Product name and basic info appear first
4. **Assessment Load**: Circle shows loading state
5. **Score Reveal**: 
   - Circle animates from 0 to actual score
   - Color transitions to red/yellow/green
   - Number becomes visible with proper contrast
6. **Final State**: Complete risk assessment with colored circular score

### Visual States

**Loading State**:
- Gray pulsing circle
- "Analyzing..." text

**Low Risk (71-100)**:
- Green circle (#4ade80)
- Green score text
- "Safe" label

**Caution (41-70)**:
- Yellow circle (#facc15)
- Yellow score text  
- "Caution" label

**High Risk (0-40)**:
- Red circle (#f87171)
- Red score text
- Pulsing animation
- "Unsafe" label

## Testing Checklist

- [ ] Backend calculates score correctly for different ingredient lists
- [ ] API returns risk_score in response
- [ ] Circle renders correctly with score 0
- [ ] Circle renders correctly with score 50
- [ ] Circle renders correctly with score 100
- [ ] Colors match specification (red/yellow/green)
- [ ] Loading state displays properly
- [ ] Animation plays smoothly
- [ ] Text remains readable on all backgrounds
- [ ] Works on different screen sizes

## Files to Modify

1. `backend/utils/prompts.py` - Update prompt to request risk_score from LLM
2. `backend/utils/risk_scorer.py` - Extract score from LLM response + add fallback calculation
3. `backend/routers/scan.py` - Include score in API response
4. `frontend/src/components/ProductResultScreen.tsx` - Use actual scores
5. `frontend/src/components/ProductResultScreen.css` - Add animations
6. `frontend/src/components/CircularRiskScore.tsx` - New component (optional)

## Accessibility Considerations

- Score number provides information independent of color
- Sufficient color contrast for text visibility
- Label text provides additional context
- Screen readers can announce score value
- Animation can be disabled via prefers-reduced-motion

## Next Steps

This plan is ready for implementation. Switch to **Code mode** to begin making these changes.
