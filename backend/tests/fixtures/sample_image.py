"""
Test fixture utilities for generating mock images and test data
Provides helper functions for creating test images with known ingredient lists
"""

import struct
import zlib
import io
from typing import Tuple
from PIL import Image, ImageDraw


def create_minimal_jpeg() -> bytes:
    """
    Create a minimal valid JPEG image (1x1 pixel)
    
    Returns:
        JPEG bytes with minimal valid structure
    """
    jpeg_data = bytes.fromhex(
        'FFD8FFE000104A46494600010100000100010000'
        'FFDB004300080606070605080707070909080A0C140D0C0B0B0C1912130F141D1A1F1E1D1A1C1C20242E2720222C231C1C28372029'
        'FFC00011080001000103012200110201031101'
        'FFC4001F00000105010101010101000000000000000102030405060708090A0B'
        'FFDA00080101000000003F00D5FFD9'
    )
    return jpeg_data


def create_minimal_png() -> bytes:
    """
    Create a minimal valid PNG image (1x1 red pixel)
    
    Returns:
        PNG bytes with valid structure
    """
    # PNG signature
    png_sig = bytes([137, 80, 78, 71, 13, 10, 26, 10])
    
    # IHDR chunk (image header): 1x1, 8-bit color
    ihdr_data = struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)
    ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff
    ihdr_chunk = struct.pack('>I', len(ihdr_data)) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
    
    # IDAT chunk (image data): red pixel
    raw_data = b'\x00\xFF\x00\x00'  # filter + RGB
    compressed = zlib.compress(raw_data)
    idat_crc = zlib.crc32(b'IDAT' + compressed) & 0xffffffff
    idat_chunk = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', idat_crc)
    
    # IEND chunk
    iend_crc = zlib.crc32(b'IEND') & 0xffffffff
    iend_chunk = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)
    
    return png_sig + ihdr_chunk + idat_chunk + iend_chunk


def create_image_with_text(text: str, format: str = "JPEG", width: int = 200, height: int = 200) -> bytes:
    """
    Create an image with text overlay using PIL
    Useful for OCR testing with known text content
    
    Args:
        text: Text to include in the image
        format: Image format (JPEG, PNG)
        width: Image width in pixels
        height: Image height in pixels
        
    Returns:
        Image bytes in specified format
    """
    try:
        # Create blank white image
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add text to image
        # Use default font (size varies by system)
        draw.text((10, 10), text, fill='black')
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format=format)
        img_bytes.seek(0)
        return img_bytes.read()
    except Exception:
        # Fallback to minimal image if PIL fails
        if format.upper() == "PNG":
            return create_minimal_png()
        else:
            return create_minimal_jpeg()


def create_product_label_image(ingredients: list, format: str = "JPEG") -> bytes:
    """
    Create a mock product label image with ingredient list
    Simulates a real product label for OCR testing
    
    Args:
        ingredients: List of ingredient names to include
        format: Image format (JPEG, PNG)
        
    Returns:
        Image bytes representing a product label
    """
    try:
        # Create larger image for ingredient list
        width, height = 400, 300
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add title
        draw.text((10, 10), "INGREDIENTS:", fill='black')
        
        # Add ingredient list
        y_pos = 40
        for ingredient in ingredients:
            draw.text((20, y_pos), f"• {ingredient}", fill='black')
            y_pos += 25
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format=format)
        img_bytes.seek(0)
        return img_bytes.read()
    except Exception:
        # Fallback to minimal image
        if format.upper() == "PNG":
            return create_minimal_png()
        else:
            return create_minimal_jpeg()


def create_invalid_image_format() -> bytes:
    """
    Create invalid image data for error testing
    
    Returns:
        Bytes that are not a valid image format
    """
    return b"This is not a valid image format"


def create_corrupted_image() -> bytes:
    """
    Create a corrupted image (valid header but corrupted data)
    
    Returns:
        Partially valid image that will fail processing
    """
    # Valid JPEG header but incomplete/corrupted data
    jpeg_header = bytes.fromhex('FFD8FFE0')
    corrupted_data = b"corrupted" * 100
    jpeg_footer = bytes.fromhex('FFD9')
    
    return jpeg_header + corrupted_data + jpeg_footer


def create_image_variants() -> dict:
    """
    Create multiple image variants for comprehensive testing
    
    Returns:
        Dictionary with various image formats and types
    """
    return {
        "valid_jpeg": create_minimal_jpeg(),
        "valid_png": create_minimal_png(),
        "invalid_format": create_invalid_image_format(),
        "corrupted": create_corrupted_image(),
        "with_text_fragrance": create_image_with_text("Ingredients: Fragrance, Rayon, Polyester"),
        "with_text_natural": create_image_with_text("100% Natural Cotton"),
    }


def create_test_images_for_ingredients(ingredient_lists: dict) -> dict:
    """
    Create test images for multiple ingredient combinations
    Useful for batch testing OCR with known results
    
    Args:
        ingredient_lists: Dict mapping test name to list of ingredients
        
    Returns:
        Dict mapping test name to image bytes
    """
    test_images = {}
    
    for test_name, ingredients in ingredient_lists.items():
        ingredient_text = "Ingredients: " + ", ".join(ingredients)
        test_images[test_name] = create_image_with_text(ingredient_text)
    
    return test_images


# Common test image sets
TEST_IMAGE_SETS = {
    "fragrance_heavy": {
        "name": "Fragrance Heavy Product",
        "ingredients": ["Fragrance", "Phthalates", "Synthetic Perfume"],
        "expected_risk": "High"
    },
    "natural_product": {
        "name": "Natural Product",
        "ingredients": ["Cotton", "Aloe Vera", "Organic Oil"],
        "expected_risk": "Low"
    },
    "mixed_product": {
        "name": "Mixed Risk Product",
        "ingredients": ["Fragrance", "Rayon", "Cotton"],
        "expected_risk": "Caution"
    },
    "unknown_ingredients": {
        "name": "Unknown Ingredients",
        "ingredients": ["XYZ Chemical", "Unknown Agent"],
        "expected_risk": "Caution"
    }
}


def get_test_image_for_risk_level(risk_level: str) -> Tuple[bytes, list]:
    """
    Get a test image matching expected risk level
    
    Args:
        risk_level: Expected risk level (Low, Caution, High)
        
    Returns:
        Tuple of (image_bytes, ingredient_list)
    """
    if risk_level.lower() == "high":
        test_set = TEST_IMAGE_SETS["fragrance_heavy"]
    elif risk_level.lower() == "low":
        test_set = TEST_IMAGE_SETS["natural_product"]
    else:  # Caution
        test_set = TEST_IMAGE_SETS["mixed_product"]
    
    ingredient_text = f"Ingredients: {', '.join(test_set['ingredients'])}"
    image = create_image_with_text(ingredient_text)
    
    return image, test_set["ingredients"]


def create_batch_test_images(count: int = 10) -> list:
    """
    Create a batch of test images for load testing
    
    Args:
        count: Number of test images to create
        
    Returns:
        List of image bytes
    """
    images = []
    
    for i in range(count):
        # Cycle through different ingredient combinations
        test_type = list(TEST_IMAGE_SETS.keys())[i % len(TEST_IMAGE_SETS)]
        test_set = TEST_IMAGE_SETS[test_type]
        
        ingredient_text = f"Ingredients: {', '.join(test_set['ingredients'])}"
        image = create_image_with_text(ingredient_text)
        images.append(image)
    
    return images
