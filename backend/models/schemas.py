"""
Pydantic models and schemas for Lotus backend API
Defines request/response schemas for type validation and API documentation
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class SensitivityEnum(str, Enum):
    """Valid sensitivity types for user profiles"""
    PCOS = "PCOS"
    BV = "BV"
    SENSITIVE_SKIN = "Sensitive Skin"
    ALLERGIES = "Allergies"
    DERMATITIS = "Dermatitis"
    ENDOMETRIOSIS = "Endometriosis"
    YEAST_INFECTIONS = "Yeast Infections"
    VULVODYNIA = "Vulvodynia"


class ScanResultIngredient(BaseModel):
    """Schema for risky ingredient in scan result"""
    name: str = Field(..., description="Ingredient name")
    risk_level: str = Field(..., description="Risk level: Low Risk, Caution, or High Risk")
    reason: str = Field(..., description="Explanation for the risk assessment")


class ScanResult(BaseModel):
    """Response schema for product scan endpoint"""
    scan_id: str = Field(..., description="Unique identifier for this scan")
    user_id: str = Field(..., description="User who performed the scan")
    overall_risk_level: str = Field(..., description="Overall risk assessment: Low Risk, Caution, or High Risk")
    ingredients_found: List[str] = Field(default_factory=list, description="List of detected ingredients")
    risky_ingredients: List[ScanResultIngredient] = Field(default_factory=list, description="Ingredients with health concerns")
    explanation: str = Field(..., description="2-sentence personalized assessment")
    timestamp: str = Field(..., description="ISO8601 timestamp of scan")

    class Config:
        json_schema_extra = {
            "example": {
                "scan_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user_123",
                "overall_risk_level": "Caution",
                "ingredients_found": ["Fragrance", "Rayon", "Polyester"],
                "risky_ingredients": [
                    {
                        "name": "Fragrance",
                        "risk_level": "High Risk",
                        "reason": "May trigger allergic reactions and skin irritation"
                    }
                ],
                "explanation": "This product contains several potentially harmful ingredients. Consider alternatives with organic materials.",
                "timestamp": "2026-01-31T18:30:00Z"
            }
        }


class Sensitivity(BaseModel):
    """User sensitivity profile"""
    value: SensitivityEnum = Field(..., description="Sensitivity type")

    class Config:
        json_schema_extra = {
            "example": {
                "value": "PCOS"
            }
        }


class UserProfile(BaseModel):
    """User profile with health sensitivities"""
    user_id: str = Field(..., description="Unique user identifier")
    sensitivities: List[str] = Field(default_factory=list, description="List of health sensitivities")
    created_at: datetime = Field(..., description="Timestamp when profile was created")
    updated_at: datetime = Field(..., description="Timestamp when profile was last updated")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "sensitivities": ["PCOS", "Sensitive Skin"],
                "created_at": "2026-01-31T18:30:00Z",
                "updated_at": "2026-01-31T18:30:00Z"
            }
        }


class IngredientData(BaseModel):
    """Single ingredient from the ingredient library"""
    id: int = Field(..., description="Unique ingredient identifier")
    name: str = Field(..., description="Ingredient name")
    description: str = Field(..., description="Detailed ingredient description and health impact")
    risk_level: str = Field(..., description="Risk level: Low, Medium, or High")
    related_ingredients: Optional[List[str]] = Field(default_factory=list, description="Similar or related ingredients")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Fragrance",
                "description": "Synthetic fragrance compounds used to mask odors. May trigger allergic reactions.",
                "risk_level": "High",
                "related_ingredients": ["Phthalates", "BPA"]
            }
        }


class ProfileCreateRequest(BaseModel):
    """Request body for creating or updating user profile"""
    user_id: str = Field(..., description="Unique user identifier", min_length=1)
    sensitivities: List[str] = Field(default_factory=list, description="List of health sensitivities")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "sensitivities": ["PCOS", "Sensitive Skin"]
            }
        }


class ProfileResponse(BaseModel):
    """Response schema for profile endpoints"""
    user_id: str = Field(..., description="Unique user identifier")
    sensitivities: List[str] = Field(default_factory=list, description="User's health sensitivities")
    created_at: datetime = Field(..., description="Profile creation timestamp")
    updated_at: datetime = Field(..., description="Last profile update timestamp")
    scan_history_count: Optional[int] = Field(default=0, description="Total number of scans performed")
    last_scan_date: Optional[datetime] = Field(default=None, description="Timestamp of most recent scan")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "sensitivities": ["PCOS", "Sensitive Skin"],
                "created_at": "2026-01-31T18:30:00Z",
                "updated_at": "2026-01-31T18:30:00Z",
                "scan_history_count": 5,
                "last_scan_date": "2026-01-31T18:15:00Z"
            }
        }


class IngredientsListResponse(BaseModel):
    """Response for ingredient library listing endpoint"""
    total_count: int = Field(..., description="Total ingredients in library")
    ingredients: List[IngredientData] = Field(default_factory=list, description="List of ingredients")

    class Config:
        json_schema_extra = {
            "example": {
                "total_count": 25,
                "ingredients": [
                    {
                        "id": 1,
                        "name": "Fragrance",
                        "description": "Synthetic fragrance compounds...",
                        "risk_level": "High",
                        "related_ingredients": []
                    }
                ]
            }
        }
