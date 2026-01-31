"""
OCR utility for extracting ingredients from product images
Uses OpenAI's GPT-4o-mini vision model to read ingredient lists
"""

import logging
import json
from typing import List, Optional
from openai import OpenAI, APIError, BadRequestError
from config import settings

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Constants
VISION_MODEL = "gpt-4o-mini"
EXTRACTION_PROMPT = "Extract every word from this ingredient list and return it as a clean JSON list of strings. Return only valid JSON."
MAX_IMAGE_SIZE = 20 * 1024 * 1024  # 20MB limit


class OCRError(Exception):
    """Custom exception for OCR operations"""
    pass


async def extract_ingredients_from_image(image_data: bytes) -> List[str]:
    """
    Extract ingredients from a product image using GPT-4o-mini vision
    
    Args:
        image_data: Raw image bytes (JPG, PNG, GIF, WebP)
        
    Returns:
        List of ingredient names extracted from the image
        (e.g., ["Fragrance", "Rayon", "Polyester"])
        
    Raises:
        OCRError: If image processing or extraction fails
    """
    try:
        # Validate image data
        if not image_data:
            raise ValueError("Image data cannot be empty")
        
        if len(image_data) > MAX_IMAGE_SIZE:
            raise ValueError(f"Image size exceeds {MAX_IMAGE_SIZE} bytes limit")
        
        logger.info(f"Processing image for ingredient extraction (size: {len(image_data)} bytes)")
        
        # Encode image to base64 for OpenAI API
        import base64
        base64_image = base64.standard_b64encode(image_data).decode("utf-8")
        
        # Detect image format (infer from magic bytes if needed)
        # Default to jpeg if uncertain
        image_format = _detect_image_format(image_data)
        
        logger.debug(f"Detected image format: {image_format}")
        
        # Call OpenAI GPT-4o-mini with vision capability
        response = client.messages.create(
            model=VISION_MODEL,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": f"image/{image_format}",
                                "data": base64_image
                            }
                        },
                        {
                            "type": "text",
                            "text": EXTRACTION_PROMPT
                        }
                    ]
                }
            ]
        )
        
        # Extract response content
        response_text = response.content[0].text.strip()
        logger.debug(f"GPT-4o-mini response: {response_text}")
        
        # Parse JSON response
        try:
            ingredients = json.loads(response_text)
            
            # Validate and clean ingredients list
            if not isinstance(ingredients, list):
                raise ValueError("Response is not a list")
            
            # Filter out empty strings and normalize
            ingredients = [
                str(ing).strip()
                for ing in ingredients
                if ing and str(ing).strip()
            ]
            
            if not ingredients:
                logger.warning("No ingredients extracted from image")
                return []
            
            logger.info(f"Successfully extracted {len(ingredients)} ingredients from image")
            return ingredients
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {response_text}")
            raise OCRError(f"Invalid JSON in GPT response: {e}")
    
    except ValueError as e:
        logger.error(f"Invalid image data: {e}")
        raise OCRError(f"Invalid image: {e}")
    
    except BadRequestError as e:
        logger.error(f"Image processing error (may be invalid format): {e}")
        raise OCRError(f"Image processing failed: {e}")
    
    except APIError as e:
        logger.error(f"OpenAI API error during OCR: {e}")
        raise OCRError(f"OpenAI API error: {e}")
    
    except Exception as e:
        logger.error(f"Unexpected error during ingredient extraction: {e}")
        raise OCRError(f"Unexpected error: {e}")


def _detect_image_format(image_data: bytes) -> str:
    """
    Detect image format from magic bytes
    
    Args:
        image_data: Raw image bytes
        
    Returns:
        Image format string (jpeg, png, gif, webp)
    """
    # Magic byte signatures
    if image_data.startswith(b'\xFF\xD8\xFF'):
        return "jpeg"
    elif image_data.startswith(b'\x89PNG'):
        return "png"
    elif image_data.startswith(b'GIF8'):
        return "gif"
    elif image_data.startswith(b'RIFF') and b'WEBP' in image_data[:12]:
        return "webp"
    else:
        # Default to jpeg if unable to detect
        logger.warning("Could not detect image format, defaulting to jpeg")
        return "jpeg"
