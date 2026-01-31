"""
API endpoint tests for Lotus backend
Tests all endpoints with valid/invalid inputs, error responses, and validation
"""

import pytest
import json
from datetime import datetime
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


class TestScanEndpoint:
    """Test /api/scan endpoint"""
    
    def test_scan_post_valid_image(self, async_client, test_image_file):
        """Test POST /api/scan with valid image and user_id"""
        with patch('routers.scan.generate_risk_score') as mock_risk:
            mock_risk.return_value = {
                "risk_level": "Caution",
                "explanation": "Contains fragrance",
                "ingredients_found": ["Fragrance"],
                "risky_ingredients": []
            }
            
            response = async_client.post(
                "/api/scan?user_id=test_user",
                files={"file": ("test.jpg", test_image_file, "image/jpeg")}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "scan_id" in data
            assert data["user_id"] == "test_user"
    
    def test_scan_missing_user_id(self, async_client, test_image_file):
        """Test POST /api/scan without user_id parameter"""
        response = async_client.post(
            "/api/scan",
            files={"file": ("test.jpg", test_image_file, "image/jpeg")}
        )
        
        # Should return 422 Unprocessable Entity
        assert response.status_code == 422
    
    def test_scan_empty_user_id(self, async_client, test_image_file):
        """Test POST /api/scan with empty user_id"""
        response = async_client.post(
            "/api/scan?user_id=",
            files={"file": ("test.jpg", test_image_file, "image/jpeg")}
        )
        
        assert response.status_code == 422
    
    def test_scan_invalid_image_type(self, async_client):
        """Test POST /api/scan with invalid image type"""
        invalid_file = b"not an image"
        
        response = async_client.post(
            "/api/scan?user_id=test_user",
            files={"file": ("test.txt", invalid_file, "text/plain")}
        )
        
        assert response.status_code == 400
        assert "Invalid file type" in response.text
    
    def test_scan_missing_file(self, async_client):
        """Test POST /api/scan without file upload"""
        response = async_client.post(
            "/api/scan?user_id=test_user"
        )
        
        assert response.status_code == 422
    
    def test_scan_empty_file(self, async_client):
        """Test POST /api/scan with empty file"""
        response = async_client.post(
            "/api/scan?user_id=test_user",
            files={"file": ("test.jpg", b"", "image/jpeg")}
        )
        
        assert response.status_code == 400
        assert "empty" in response.text.lower()
    
    def test_scan_oversized_file(self, async_client):
        """Test POST /api/scan with file exceeding size limit"""
        # Create 21MB file (exceeds 20MB limit)
        oversized = b"x" * (21 * 1024 * 1024)
        
        response = async_client.post(
            "/api/scan?user_id=test_user",
            files={"file": ("test.jpg", oversized, "image/jpeg")}
        )
        
        assert response.status_code == 400
        assert "exceeds" in response.text.lower()
    
    def test_scan_valid_response_format(self, async_client, test_image_file):
        """Test that scan response has correct format"""
        with patch('routers.scan.generate_risk_score') as mock_risk:
            mock_risk.return_value = {
                "risk_level": "Low Risk",
                "explanation": "Safe product",
                "ingredients_found": ["Cotton"],
                "risky_ingredients": []
            }
            
            response = async_client.post(
                "/api/scan?user_id=test_user",
                files={"file": ("test.jpg", test_image_file, "image/jpeg")}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify response schema
            required_fields = [
                "scan_id", "user_id", "overall_risk_level",
                "ingredients_found", "risky_ingredients", "explanation", "timestamp"
            ]
            assert all(field in data for field in required_fields)
    
    def test_scan_multiple_supported_formats(self, async_client, test_image_file, test_image_png):
        """Test scan accepts multiple image formats"""
        formats = [
            ("test.jpg", test_image_file, "image/jpeg"),
            ("test.png", test_image_png, "image/png"),
        ]
        
        with patch('routers.scan.generate_risk_score') as mock_risk:
            mock_risk.return_value = {
                "risk_level": "Low Risk",
                "explanation": "Test",
                "ingredients_found": [],
                "risky_ingredients": []
            }
            
            for filename, file_data, content_type in formats:
                response = async_client.post(
                    "/api/scan?user_id=test_user",
                    files={"file": (filename, file_data, content_type)}
                )
                
                assert response.status_code == 200


class TestProfileEndpoints:
    """Test /api/profiles endpoints"""
    
    def test_create_profile_valid(self, async_client):
        """Test POST /api/profiles with valid data"""
        profile_data = {
            "user_id": "user_123",
            "sensitivities": ["PCOS", "Sensitive Skin"]
        }
        
        with patch('routers.profiles.get_supabase_client') as mock_client:
            mock_supabase = MagicMock()
            mock_response = MagicMock()
            mock_response.data = [{
                "user_id": "user_123",
                "sensitivities": ["PCOS", "Sensitive Skin"],
                "created_at": "2026-01-31T18:00:00Z",
                "updated_at": "2026-01-31T18:00:00Z"
            }]
            
            mock_table = MagicMock()
            mock_table.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
            mock_table.upsert.return_value.execute.return_value = mock_response
            mock_supabase.table.return_value = mock_table
            mock_client.return_value = mock_supabase
            
            response = async_client.post("/api/profiles", json=profile_data)
            
            assert response.status_code == 201
    
    def test_create_profile_missing_user_id(self, async_client):
        """Test POST /api/profiles without user_id"""
        profile_data = {
            "sensitivities": ["PCOS"]
        }
        
        response = async_client.post("/api/profiles", json=profile_data)
        
        assert response.status_code == 422
    
    def test_create_profile_empty_user_id(self, async_client):
        """Test POST /api/profiles with empty user_id"""
        profile_data = {
            "user_id": "",
            "sensitivities": ["PCOS"]
        }
        
        response = async_client.post("/api/profiles", json=profile_data)
        
        assert response.status_code == 400
    
    def test_create_profile_empty_sensitivities_allowed(self, async_client):
        """Test POST /api/profiles with empty sensitivities list"""
        profile_data = {
            "user_id": "user_123",
            "sensitivities": []
        }
        
        with patch('routers.profiles.get_supabase_client') as mock_client:
            mock_supabase = MagicMock()
            mock_response = MagicMock()
            mock_response.data = [{
                "user_id": "user_123",
                "sensitivities": [],
                "created_at": "2026-01-31T18:00:00Z",
                "updated_at": "2026-01-31T18:00:00Z"
            }]
            
            mock_table = MagicMock()
            mock_table.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
            mock_table.upsert.return_value.execute.return_value = mock_response
            mock_supabase.table.return_value = mock_table
            mock_client.return_value = mock_supabase
            
            response = async_client.post("/api/profiles", json=profile_data)
            
            assert response.status_code == 201
    
    def test_get_profile_valid(self, async_client, test_user_profile):
        """Test GET /api/profiles/{user_id}"""
        user_id = "test_user_123"
        
        with patch('routers.profiles.get_supabase_client') as mock_client:
            mock_supabase = MagicMock()
            mock_response = MagicMock()
            mock_response.data = [{
                "user_id": user_id,
                "sensitivities": ["PCOS"],
                "created_at": "2026-01-31T18:00:00Z",
                "updated_at": "2026-01-31T18:00:00Z"
            }]
            
            mock_table = MagicMock()
            mock_table.select.return_value.eq.return_value.execute.return_value = mock_response
            mock_supabase.table.return_value = mock_table
            mock_client.return_value = mock_supabase
            
            response = async_client.get(f"/api/profiles/{user_id}")
            
            assert response.status_code == 200
    
    def test_get_profile_not_found(self, async_client):
        """Test GET /api/profiles/{user_id} with non-existent user"""
        user_id = "nonexistent_user"
        
        with patch('routers.profiles.get_supabase_client') as mock_client:
            mock_supabase = MagicMock()
            mock_response = MagicMock()
            mock_response.data = []
            
            mock_table = MagicMock()
            mock_table.select.return_value.eq.return_value.execute.return_value = mock_response
            mock_supabase.table.return_value = mock_table
            mock_client.return_value = mock_supabase
            
            response = async_client.get(f"/api/profiles/{user_id}")
            
            assert response.status_code == 404
    
    def test_get_profile_empty_user_id(self, async_client):
        """Test GET /api/profiles with empty user_id"""
        response = async_client.get("/api/profiles/ ")
        
        # Should still try to fetch, but database will return 404
        assert response.status_code in [400, 404]


class TestIngredientsEndpoints:
    """Test /api/ingredients endpoints"""
    
    def test_list_ingredients_default(self, async_client, test_ingredients_data):
        """Test GET /api/ingredients with default parameters"""
        with patch('routers.ingredients._load_ingredients') as mock_load:
            mock_load.return_value = [
                {
                    "id": ing.id,
                    "name": ing.name,
                    "description": ing.description,
                    "risk_level": ing.risk_level,
                    "related_ingredients": ing.related_ingredients
                }
                for ing in test_ingredients_data
            ]
            
            response = async_client.get("/api/ingredients")
            
            assert response.status_code == 200
            data = response.json()
            assert "total_count" in data
            assert "ingredients" in data
    
    def test_list_ingredients_with_limit(self, async_client):
        """Test GET /api/ingredients with limit parameter"""
        response = async_client.get("/api/ingredients?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["ingredients"]) <= 5
    
    def test_list_ingredients_with_offset(self, async_client):
        """Test GET /api/ingredients with offset parameter"""
        response = async_client.get("/api/ingredients?offset=10")
        
        assert response.status_code == 200
    
    def test_list_ingredients_filter_by_risk_level_high(self, async_client):
        """Test GET /api/ingredients with risk_level filter"""
        response = async_client.get("/api/ingredients?risk_level=High")
        
        assert response.status_code == 200
        data = response.json()
        
        # All ingredients should have High risk level
        for ingredient in data["ingredients"]:
            assert ingredient["risk_level"] == "High"
    
    def test_list_ingredients_invalid_risk_level(self, async_client):
        """Test GET /api/ingredients with invalid risk_level"""
        response = async_client.get("/api/ingredients?risk_level=Invalid")
        
        assert response.status_code == 400
    
    def test_list_ingredients_invalid_limit(self, async_client):
        """Test GET /api/ingredients with invalid limit"""
        response = async_client.get("/api/ingredients?limit=1000")
        
        # Should reject limit > 100
        assert response.status_code == 422
    
    def test_list_ingredients_negative_offset(self, async_client):
        """Test GET /api/ingredients with negative offset"""
        response = async_client.get("/api/ingredients?offset=-1")
        
        assert response.status_code == 422
    
    def test_get_ingredient_valid(self, async_client):
        """Test GET /api/ingredients/{ingredient_id}"""
        ingredient_id = 1
        
        with patch('routers.ingredients._load_ingredients') as mock_load:
            mock_load.return_value = [
                {
                    "id": 1,
                    "name": "Fragrance",
                    "description": "Synthetic fragrance",
                    "risk_level": "High",
                    "related_ingredients": []
                }
            ]
            
            response = async_client.get(f"/api/ingredients/{ingredient_id}")
            
            assert response.status_code == 200
    
    def test_get_ingredient_not_found(self, async_client):
        """Test GET /api/ingredients/{ingredient_id} with non-existent ID"""
        ingredient_id = 99999
        
        with patch('routers.ingredients._load_ingredients') as mock_load:
            mock_load.return_value = []
            
            response = async_client.get(f"/api/ingredients/{ingredient_id}")
            
            assert response.status_code == 404
    
    def test_get_ingredient_invalid_id(self, async_client):
        """Test GET /api/ingredients/{ingredient_id} with invalid ID"""
        response = async_client.get("/api/ingredients/invalid")
        
        assert response.status_code == 422
    
    def test_get_ingredient_negative_id(self, async_client):
        """Test GET /api/ingredients/{ingredient_id} with negative ID"""
        response = async_client.get("/api/ingredients/-1")
        
        assert response.status_code == 400


class TestHealthEndpoint:
    """Test health check endpoints"""
    
    def test_health_check(self, async_client):
        """Test GET /health endpoint"""
        response = async_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data
    
    def test_scan_health_check(self, async_client):
        """Test GET /api/scan/health endpoint"""
        response = async_client.get("/api/scan/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestErrorResponses:
    """Test error response formats"""
    
    def test_400_bad_request_format(self, async_client):
        """Test 400 Bad Request response format"""
        response = async_client.get("/api/ingredients?risk_level=Invalid")
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_404_not_found_format(self, async_client):
        """Test 404 Not Found response format"""
        with patch('routers.profiles.get_supabase_client') as mock_client:
            mock_supabase = MagicMock()
            mock_response = MagicMock()
            mock_response.data = []
            
            mock_table = MagicMock()
            mock_table.select.return_value.eq.return_value.execute.return_value = mock_response
            mock_supabase.table.return_value = mock_table
            mock_client.return_value = mock_supabase
            
            response = async_client.get("/api/profiles/nonexistent")
            
            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
    
    def test_422_validation_error_format(self, async_client):
        """Test 422 Unprocessable Entity response format"""
        response = async_client.post("/api/profiles", json={})
        
        assert response.status_code == 422


class TestInputValidation:
    """Test input validation across endpoints"""
    
    def test_user_id_whitespace_trimming(self, async_client):
        """Test that user_id is trimmed of whitespace"""
        profile_data = {
            "user_id": "  user_123  ",
            "sensitivities": []
        }
        
        with patch('routers.profiles.get_supabase_client') as mock_client:
            mock_supabase = MagicMock()
            mock_response = MagicMock()
            mock_response.data = [{
                "user_id": "user_123",
                "sensitivities": [],
                "created_at": "2026-01-31T18:00:00Z",
                "updated_at": "2026-01-31T18:00:00Z"
            }]
            
            mock_table = MagicMock()
            mock_table.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
            mock_table.upsert.return_value.execute.return_value = mock_response
            mock_supabase.table.return_value = mock_table
            mock_client.return_value = mock_supabase
            
            response = async_client.post("/api/profiles", json=profile_data)
            
            assert response.status_code == 201
    
    def test_sensitivities_list_validation(self, async_client):
        """Test that sensitivities must be a list"""
        profile_data = {
            "user_id": "user_123",
            "sensitivities": "PCOS"  # Should be list
        }
        
        response = async_client.post("/api/profiles", json=profile_data)
        
        assert response.status_code == 422
    
    def test_pagination_limit_boundaries(self, async_client):
        """Test pagination limit boundary values"""
        # Minimum valid limit
        response = async_client.get("/api/ingredients?limit=1")
        assert response.status_code == 200
        
        # Maximum valid limit
        response = async_client.get("/api/ingredients?limit=100")
        assert response.status_code == 200
        
        # Just over maximum
        response = async_client.get("/api/ingredients?limit=101")
        assert response.status_code == 422
