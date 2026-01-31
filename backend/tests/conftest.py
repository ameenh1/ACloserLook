"""
Pytest configuration and fixtures for Lotus backend tests
Provides mocked Supabase client, test data, and FastAPI test client setup
"""

import pytest
import asyncio
import json
from datetime import datetime
from typing import Generator, AsyncGenerator
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from io import BytesIO
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from main import app
from models.schemas import UserProfile, ScanResult, IngredientData


# ============================================================================
# Event Loop Configuration
# ============================================================================

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """
    Create event loop for async tests
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# FastAPI Test Client
# ============================================================================

@pytest.fixture
def async_client() -> TestClient:
    """
    FastAPI TestClient for integration tests
    Provides synchronous interface to async endpoints
    """
    return TestClient(app)


# ============================================================================
# Supabase Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_supabase_client():
    """
    Fixture for mocked Supabase client
    Provides mock methods for table operations and RPC calls
    """
    mock_client = MagicMock()
    
    # Mock table operations
    mock_table = MagicMock()
    mock_client.table.return_value = mock_table
    
    # Mock select chain
    mock_select = MagicMock()
    mock_table.select.return_value = mock_select
    
    # Mock eq chain
    mock_eq = MagicMock()
    mock_select.eq.return_value = mock_eq
    mock_eq.eq.return_value = mock_eq
    
    # Mock execute
    mock_response = MagicMock()
    mock_response.data = []
    mock_eq.execute.return_value = mock_response
    mock_select.execute.return_value = mock_response
    
    # Mock RPC calls
    mock_rpc = MagicMock()
    mock_client.rpc.return_value = mock_rpc
    mock_rpc.execute.return_value = mock_response
    
    # Mock order
    mock_order = MagicMock()
    mock_select.order.return_value = mock_order
    mock_order.limit.return_value = mock_order
    mock_order.execute.return_value = mock_response
    
    # Mock limit
    mock_limit = MagicMock()
    mock_select.limit.return_value = mock_limit
    mock_limit.execute.return_value = mock_response
    
    # Mock upsert
    mock_upsert = MagicMock()
    mock_table.upsert.return_value = mock_upsert
    mock_upsert.execute.return_value = mock_response
    
    return mock_client


@pytest.fixture
def supabase_with_profiles(mock_supabase_client):
    """
    Mock Supabase client with profile data
    """
    mock_table = mock_supabase_client.table.return_value
    
    # Setup profile response
    profile_data = {
        "user_id": "test_user_123",
        "sensitivities": ["PCOS", "Sensitive Skin"],
        "created_at": "2026-01-31T18:00:00Z",
        "updated_at": "2026-01-31T18:30:00Z"
    }
    
    mock_response = MagicMock()
    mock_response.data = [profile_data]
    
    mock_select = MagicMock()
    mock_table.select.return_value = mock_select
    
    mock_eq = MagicMock()
    mock_select.eq.return_value = mock_eq
    mock_eq.execute.return_value = mock_response
    
    return mock_supabase_client


@pytest.fixture
def supabase_with_ingredients(mock_supabase_client):
    """
    Mock Supabase client with ingredient library data
    """
    ingredients_data = [
        {
            "id": 1,
            "name": "Fragrance",
            "description": "Synthetic fragrance compounds",
            "risk_level": "High",
            "embedding": [0.1] * 1536
        },
        {
            "id": 2,
            "name": "Rayon",
            "description": "Semi-synthetic fiber",
            "risk_level": "Medium",
            "embedding": [0.2] * 1536
        },
        {
            "id": 3,
            "name": "Cotton",
            "description": "Natural fiber",
            "risk_level": "Low",
            "embedding": [0.3] * 1536
        }
    ]
    
    mock_table = mock_supabase_client.table.return_value
    mock_response = MagicMock()
    mock_response.data = ingredients_data
    
    mock_select = MagicMock()
    mock_table.select.return_value = mock_select
    mock_select.execute.return_value = mock_response
    mock_select.limit.return_value = mock_select
    
    return mock_supabase_client


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def test_user_profile() -> UserProfile:
    """
    Fixture with sample user profile data for testing
    """
    now = datetime.utcnow()
    return UserProfile(
        user_id="test_user_123",
        sensitivities=["PCOS", "Sensitive Skin"],
        created_at=now,
        updated_at=now
    )


@pytest.fixture
def test_ingredients_data() -> list:
    """
    Fixture with sample ingredient data
    """
    return [
        IngredientData(
            id=1,
            name="Fragrance",
            description="Synthetic fragrance compounds used to mask odors. May trigger allergic reactions.",
            risk_level="High",
            related_ingredients=["Phthalates", "BPA"]
        ),
        IngredientData(
            id=2,
            name="Rayon",
            description="Semi-synthetic fiber made from wood pulp. Generally safe but may irritate sensitive skin.",
            risk_level="Medium",
            related_ingredients=["Cellulose"]
        ),
        IngredientData(
            id=3,
            name="Cotton",
            description="Natural fiber. Safe for most skin types including sensitive skin.",
            risk_level="Low",
            related_ingredients=[]
        ),
        IngredientData(
            id=4,
            name="Phthalates",
            description="Plasticizers and fragrance carriers. Endocrine disruptors with known health risks.",
            risk_level="High",
            related_ingredients=["Fragrance", "BPA"]
        ),
        IngredientData(
            id=5,
            name="Aloe Vera",
            description="Natural plant extract with soothing properties. Safe for sensitive skin.",
            risk_level="Low",
            related_ingredients=[]
        )
    ]


@pytest.fixture
def test_scan_result() -> dict:
    """
    Fixture with sample scan result data
    """
    return {
        "scan_id": "550e8400-e29b-41d4-a716-446655440000",
        "user_id": "test_user_123",
        "overall_risk_level": "Caution",
        "ingredients_found": ["Fragrance", "Rayon", "Polyester"],
        "risky_ingredients": [
            {
                "name": "Fragrance",
                "risk_level": "High Risk",
                "reason": "May trigger allergic reactions and skin irritation"
            }
        ],
        "explanation": "This product contains fragrance which may irritate your sensitive skin. Consider fragrance-free alternatives.",
        "timestamp": "2026-01-31T18:30:00Z"
    }


# ============================================================================
# Mock Image Fixtures
# ============================================================================

@pytest.fixture
def test_image_file() -> bytes:
    """
    Fixture with mock JPEG image for OCR testing
    Creates minimal valid JPEG header (1x1 pixel)
    """
    # Minimal valid JPEG: SOI marker + EOI marker
    # FFD8 = Start of Image
    # FFD9 = End of Image
    jpeg_data = bytes.fromhex(
        'FFD8FFE000104A46494600010100000100010000'
        'FFDB004300080606070605080707070909080A0C140D0C0B0B0C1912130F141D1A1F1E1D1A1C1C20242E2720222C231C1C28372029'
        'FFC00011080001000103012200110201031101'
        'FFC4001F00000105010101010101000000000000000102030405060708090A0B'
        'FFDA00080101000000003F00D5FFD9'
    )
    return jpeg_data


@pytest.fixture
def test_image_png() -> bytes:
    """
    Fixture with mock PNG image
    Creates minimal valid PNG (1x1 red pixel)
    """
    import struct
    import zlib
    
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


@pytest.fixture
def mock_image_with_text() -> bytes:
    """
    Fixture with mock image containing known ingredient text
    For testing OCR extraction with known inputs
    """
    # Use test JPEG as base
    return (
        bytes.fromhex('FFD8FFE000104A46494600010100000100010000'
                      'FFDB004300080606070605080707070909080A0C140D0C0B0B0C1912130F141D1A1F1E1D1A1C1C20242E2720222C231C1C28372029'
                      'FFC00011080001000103012200110201031101'
                      'FFC4001F00000105010101010101000000000000000102030405060708090A0B'
                      'FFDA00080101000000003F00D5FFD9')
    )


# ============================================================================
# OpenAI Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_openai_embedding():
    """
    Mock OpenAI embedding response
    """
    mock = MagicMock()
    mock.data = [MagicMock(embedding=[0.1] * 1536)]
    return mock


@pytest.fixture
def mock_openai_vision_response():
    """
    Mock OpenAI vision API response for OCR
    """
    mock = MagicMock()
    mock.content = [MagicMock(text='["Fragrance", "Rayon", "Polyester"]')]
    return mock


@pytest.fixture
def mock_openai_chat_response():
    """
    Mock OpenAI chat API response for risk assessment
    """
    response_data = {
        "overall_risk_level": "Caution (Irritating)",
        "explanation": "Contains fragrance which may irritate sensitive skin.",
        "ingredient_details": [
            {
                "name": "Fragrance",
                "risk_level": "High Risk",
                "reason": "Known allergen"
            }
        ]
    }
    mock = MagicMock()
    mock.content = [MagicMock(text=json.dumps(response_data))]
    return mock


# ============================================================================
# Patched Supabase Client
# ============================================================================

@pytest.fixture
def patch_supabase_client(mock_supabase_client):
    """
    Patch get_supabase_client to return mock client
    """
    with patch('utils.supabase_client.get_supabase_client', return_value=mock_supabase_client):
        with patch('utils.vector_search.get_supabase_client', return_value=mock_supabase_client):
            with patch('utils.risk_scorer.get_supabase_client', return_value=mock_supabase_client):
                with patch('routers.profiles.get_supabase_client', return_value=mock_supabase_client):
                    with patch('routers.scan.get_supabase_client', return_value=mock_supabase_client):
                        yield mock_supabase_client


@pytest.fixture
def patch_supabase_with_profiles(supabase_with_profiles):
    """
    Patch get_supabase_client with profile data
    """
    with patch('utils.supabase_client.get_supabase_client', return_value=supabase_with_profiles):
        with patch('utils.vector_search.get_supabase_client', return_value=supabase_with_profiles):
            with patch('utils.risk_scorer.get_supabase_client', return_value=supabase_with_profiles):
                with patch('routers.profiles.get_supabase_client', return_value=supabase_with_profiles):
                    with patch('routers.scan.get_supabase_client', return_value=supabase_with_profiles):
                        yield supabase_with_profiles


@pytest.fixture
def patch_supabase_with_ingredients(supabase_with_ingredients):
    """
    Patch get_supabase_client with ingredient data
    """
    with patch('utils.supabase_client.get_supabase_client', return_value=supabase_with_ingredients):
        with patch('utils.vector_search.get_supabase_client', return_value=supabase_with_ingredients):
            with patch('utils.risk_scorer.get_supabase_client', return_value=supabase_with_ingredients):
                with patch('routers.profiles.get_supabase_client', return_value=supabase_with_ingredients):
                    yield supabase_with_ingredients


# ============================================================================
# OpenAI API Mocks
# ============================================================================

@pytest.fixture
def patch_openai_embeddings(mock_openai_embedding):
    """
    Patch OpenAI embeddings API
    """
    with patch('openai.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_client.embeddings.create.return_value = mock_openai_embedding
        mock_openai.return_value = mock_client
        yield mock_client


@pytest.fixture
def patch_openai_vision(mock_openai_vision_response):
    """
    Patch OpenAI vision API for OCR
    """
    with patch('openai.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_openai_vision_response
        mock_openai.return_value = mock_client
        yield mock_client


@pytest.fixture
def patch_openai_chat(mock_openai_chat_response):
    """
    Patch OpenAI chat API for risk assessment
    """
    with patch('openai.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_openai_chat_response
        mock_openai.return_value = mock_client
        yield mock_client


@pytest.fixture
def patch_all_openai(mock_openai_embedding, mock_openai_vision_response, mock_openai_chat_response):
    """
    Patch all OpenAI APIs at once
    """
    with patch('openai.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_client.embeddings.create.return_value = mock_openai_embedding
        mock_client.messages.create.side_effect = [
            mock_openai_vision_response,
            mock_openai_chat_response
        ]
        mock_openai.return_value = mock_client
        yield mock_client


# ============================================================================
# Combined Patches
# ============================================================================

@pytest.fixture
def mock_environment(patch_supabase_client, patch_all_openai):
    """
    Fixture combining all mocked external dependencies
    Useful for end-to-end pipeline tests
    """
    return {
        'supabase': patch_supabase_client,
        'openai': patch_all_openai
    }


@pytest.fixture
def pytest_configure(config):
    """
    Configure pytest markers
    """
    config.addinivalue_line("markers", "asyncio: mark test as async")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "performance: mark test as performance test")
