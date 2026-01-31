"""
Models package for Lotus backend
Exports Pydantic schemas for type validation and API documentation
"""

from .schemas import (
    ScanResult,
    UserProfile,
    Sensitivity,
    IngredientData,
    ProfileCreateRequest,
    ProfileResponse,
)

__all__ = [
    "ScanResult",
    "UserProfile",
    "Sensitivity",
    "IngredientData",
    "ProfileCreateRequest",
    "ProfileResponse",
]
