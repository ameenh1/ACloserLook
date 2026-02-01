# Ingredients Vertical Layout Implementation Plan

## Objective
Transform the ingredients display from a horizontal wrapped badge layout to a vertical single-column list with colored dot indicators and full-width line items.

## Current Implementation (Lines 542-557)
```javascript
<div className="px-5 pb-5 flex flex-row flex-wrap gap-2">
  {basicProduct.ingredients.map((ingredient, index) => {
    const isRisky = assessmentData?.risky_ingredients?.some(r => r.name.toLowerCase() === ingredient.toLowerCase());
    return (
      <span
        key={index}
        className={`px-3 py-1.5 rounded-full font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[11px] tracking-[-0.5px] break-words max-w-full ${
          isRisky ? "bg-red-500/20 text-red-400 border border-red-500/30" : "bg-white/10 text-white"
        }`}
        style={{ wordWrap: 'break-word', overflowWrap: 'break-word' }}
      >
        {ingredient}
      </span>
    );
  })}
</div>
```

## Proposed Changes

### 1. Container Transformation
**Change from:**
```javascript
className="px-5 pb-5 flex flex-row flex-wrap gap-2"
```

**Change to:**
```javascript
className="px-5 pb-5 flex flex-col gap-3"
```

### 2. Ingredient Item Restructuring
**Change from:** Simple badge span
**Change to:** Full-width line item with:
- Colored dot indicator on left (● character)
- Ingredient label on right
- Dynamic background color (risky = red, safe = transparent/subtle)
- Full width for scannability

**New structure:**
```javascript
<div
  key={index}
  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[11px] tracking-[-0.5px] ${
    isRisky ? "bg-red-500/20 text-red-400" : "bg-white/10 text-white"
  }`}
>
  {/* Colored dot indicator */}
  <span className={isRisky ? "text-red-400" : "text-white/60"}>●</span>
  
  {/* Ingredient label */}
  <span className="flex-1">{ingredient}</span>
</div>
```

### 3. Visual Changes

#### Before (Horizontal Badges)
```
Water  Cellulose  Titanium Dioxide
Sodium Lauryl  Fragrance  Alcohol
```

#### After (Vertical Line Items)
```
● Water
● Cellulose Gum
● Titanium Dioxide          [red background]
● Sodium Lauryl Sulfate     [red background]
● Fragrance
```

## Implementation Details

### Styling Considerations
- **Container**: `flex flex-col gap-3` for vertical stacking with 12px spacing
- **Items**: `flex items-center gap-3` for horizontal alignment of dot + label
- **Dot**: Simple `●` character (U+25CF), inherits text color
- **Label**: `flex-1` to take remaining width
- **Spacing**: `px-3 py-2.5` for horizontal/vertical padding
- **Background**: Risky ingredients keep `bg-red-500/20`, safe get `bg-white/10`

### No Changes Needed
- Risky ingredient detection logic (lines 544)
- Color scheme for risky vs safe
- Font family and sizing
- Collapsible container wrapper

## Files to Modify
1. **`frontend/src/components/ProductResultScreen.tsx`** (lines 542-557)
   - Update container className
   - Restructure ingredient rendering with new JSX

## Verification Steps
1. Ingredients display vertically in a single column
2. Each item is a full-width line
3. Colored dots appear on the left
4. Risky ingredients show red background
5. Safe ingredients show subtle white background
6. No wrapping or badge styling remains
7. Proper spacing (12px) between items

## Accessibility Notes
- Dot character (●) provides visual hierarchy
- Text contrast maintained (white on dark, red on dark-red)
- Line items remain readable at all font sizes

## Switch to Code Mode
Once approved, this plan will be implemented using the Code mode with the exact changes specified above.
