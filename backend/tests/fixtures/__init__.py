"""
Test fixtures package for Lotus backend tests
Provides mock data, sample images, and utility functions for testing
"""

from .sample_image import (
    create_minimal_jpeg,
    create_minimal_png,
    create_image_with_text,
    create_product_label_image,
    create_invalid_image_format,
    create_corrupted_image,
    create_image_variants,
    create_test_images_for_ingredients,
    TEST_IMAGE_SETS,
    get_test_image_for_risk_level,
    create_batch_test_images
)

__all__ = [
    "create_minimal_jpeg",
    "create_minimal_png",
    "create_image_with_text",
    "create_product_label_image",
    "create_invalid_image_format",
    "create_corrupted_image",
    "create_image_variants",
    "create_test_images_for_ingredients",
    "TEST_IMAGE_SETS",
    "get_test_image_for_risk_level",
    "create_batch_test_images"
]
