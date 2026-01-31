"""
LLM prompt templates for health assessment and risk scoring
Defines system prompts and prompt templates for vaginal health expertise
"""

# System prompt for health expert context
HEALTH_EXPERT_SYSTEM_PROMPT = """You are a medical expert specializing in vaginal health and ingredient safety assessment. 
Your role is to provide evidence-based health guidance about personal care product ingredients and their potential effects on vaginal health.

You have deep knowledge of:
- Ingredient chemistry and properties
- Common vaginal irritants and allergens
- Vulvovaginal conditions and sensitivities
- Scientific research on ingredient safety
- Individual variation in sensitivity profiles

When assessing ingredients, consider:
1. Direct chemical irritancy
2. pH disruption potential
3. Allergenic properties
4. Individual sensitivities provided by the user
5. Synergistic effects of multiple ingredients

Always provide balanced, evidence-based guidance."""


# Risk assessment prompt template
RISK_ASSESSMENT_PROMPT = """Based on the following information, assess the health risk level of this personal care product:

SCANNED INGREDIENTS:
{scanned_ingredients}

USER SENSITIVITIES:
{user_sensitivities}

SIMILAR INGREDIENTS FROM KNOWLEDGE BASE:
{retrieved_vector_data}

ASSESSMENT TASK:
1. Evaluate each ingredient against the user's known sensitivities
2. Cross-reference with similar ingredients in the knowledge base for risk patterns
3. Consider synergistic effects of multiple ingredients
4. Provide an overall risk level assessment

RESPONSE FORMAT:
You MUST respond with ONLY a valid JSON object (no markdown, no code blocks) with this structure:
{{
    "overall_risk_level": "Low Risk (Safe)" | "Caution (Irritating)" | "High Risk (Harmful)",
    "explanation": "Brief 2-sentence explanation of the risk assessment",
    "ingredient_details": [
        {{
            "name": "ingredient name",
            "risk_level": "Low" | "Medium" | "High",
            "reason": "Why this ingredient poses this risk level"
        }}
    ],
    "recommendations": "Actionable advice for the user"
}}

RISK LEVEL DEFINITIONS:
- Low Risk (Safe): Ingredient is generally safe for most people, unlikely to cause irritation
- Caution (Irritating): Ingredient may cause irritation for some users or in certain combinations
- High Risk (Harmful): Ingredient is known to cause problems for sensitive individuals or contains concerning substances

Ensure your response is ONLY valid JSON with no additional text."""


# Alternative prompt for basic assessment (simpler format)
RISK_ASSESSMENT_PROMPT_SIMPLE = """Assess the vaginal health risk of these ingredients:

Ingredients: {scanned_ingredients}
User Sensitivities: {user_sensitivities}

Respond with ONLY a JSON object:
{{
    "risk_level": "Low" | "Medium" | "High",
    "explanation": "brief explanation",
    "risky_ingredients": ["ingredient1", "ingredient2"]
}}"""


def format_risk_assessment_prompt(
    scanned_ingredients: list,
    user_sensitivities: list,
    retrieved_vector_data: list
) -> str:
    """
    Format the risk assessment prompt with actual data
    
    Args:
        scanned_ingredients: List of ingredients extracted from image
        user_sensitivities: List of user's known sensitivities
        retrieved_vector_data: List of similar ingredients from vector search
        
    Returns:
        Formatted prompt string ready for LLM
    """
    # Format ingredients
    ingredients_str = ", ".join(scanned_ingredients) if scanned_ingredients else "None"
    
    # Format user sensitivities
    if user_sensitivities:
        sensitivities_str = ", ".join(user_sensitivities)
    else:
        sensitivities_str = "No known sensitivities"
    
    # Format retrieved vector data
    if retrieved_vector_data:
        vector_data_str = "\n".join([
            f"- {item.get('name', 'Unknown')}: {item.get('description', 'N/A')} "
            f"(Risk Level: {item.get('risk_level', 'Unknown')})"
            for item in retrieved_vector_data
        ])
    else:
        vector_data_str = "No similar ingredients found in knowledge base"
    
    return RISK_ASSESSMENT_PROMPT.format(
        scanned_ingredients=ingredients_str,
        user_sensitivities=sensitivities_str,
        retrieved_vector_data=vector_data_str
    )


def format_risk_assessment_prompt_simple(
    scanned_ingredients: list,
    user_sensitivities: list
) -> str:
    """
    Format simplified risk assessment prompt
    
    Args:
        scanned_ingredients: List of ingredients extracted from image
        user_sensitivities: List of user's known sensitivities
        
    Returns:
        Formatted prompt string
    """
    ingredients_str = ", ".join(scanned_ingredients) if scanned_ingredients else "None"
    sensitivities_str = ", ".join(user_sensitivities) if user_sensitivities else "None"
    
    return RISK_ASSESSMENT_PROMPT_SIMPLE.format(
        scanned_ingredients=ingredients_str,
        user_sensitivities=sensitivities_str
    )
