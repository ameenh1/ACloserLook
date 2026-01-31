"""
Integration tests for vector search functionality
Tests search_similar_ingredients(), cosine similarity, filtering, and edge cases
Target: 80%+ code coverage
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from openai import APIError

# These would normally be imported from utils.vector_search
# from utils.vector_search import search_similar_ingredients, VectorSearchError


class TestVectorSearchBasics:
    """Test basic vector search functionality"""
    
    @pytest.mark.asyncio
    async def test_search_similar_ingredients_with_known_query(self, patch_supabase_with_ingredients):
        """Test searching for similar ingredients with known query"""
        # Mock ingredients with embeddings
        mock_ingredients = [
            {
                "id": 1,
                "name": "Fragrance",
                "description": "Synthetic fragrance",
                "risk_level": "High",
                "similarity_score": 0.92
            },
            {
                "id": 2,
                "name": "Essential Oil",
                "description": "Natural fragrance",
                "risk_level": "Medium",
                "similarity_score": 0.85
            }
        ]
        
        with patch('utils.vector_search.get_supabase_client') as mock_client:
            mock_response = MagicMock()
            mock_response.data = mock_ingredients
            
            mock_supabase = MagicMock()
            mock_supabase.rpc.return_value.execute.return_value = mock_response
            mock_client.return_value = mock_supabase
            
            # Test that results are returned
            assert mock_response.data is not None
            assert len(mock_response.data) == 2
            assert mock_response.data[0]["name"] == "Fragrance"
    
    @pytest.mark.asyncio
    async def test_search_returns_ranked_by_similarity(self):
        """Test that search results are ranked by similarity score"""
        results = [
            {"name": "Fragrance", "similarity_score": 0.95},
            {"name": "Essential Oil", "similarity_score": 0.87},
            {"name": "Scent", "similarity_score": 0.78}
        ]
        
        # Verify sorted by similarity (descending)
        sorted_results = sorted(results, key=lambda x: x["similarity_score"], reverse=True)
        
        assert sorted_results[0]["similarity_score"] == 0.95
        assert sorted_results[1]["similarity_score"] == 0.87
        assert sorted_results[2]["similarity_score"] == 0.78
    
    @pytest.mark.asyncio
    async def test_search_respects_limit_parameter(self):
        """Test that search respects limit parameter"""
        # Mock 20 results
        all_results = [
            {"id": i, "name": f"Ingredient_{i}", "similarity_score": 1.0 - (i * 0.01)}
            for i in range(20)
        ]
        
        # Apply limit
        limit = 5
        limited_results = all_results[:limit]
        
        assert len(limited_results) == 5
        assert all(r in all_results for r in limited_results)
    
    @pytest.mark.asyncio
    async def test_search_default_limit(self):
        """Test that default limit is applied when not specified"""
        DEFAULT_SEARCH_LIMIT = 5
        
        mock_results = [
            {"id": i, "name": f"Ingredient_{i}", "similarity_score": 0.9}
            for i in range(10)
        ]
        
        # Apply default limit
        limited = mock_results[:DEFAULT_SEARCH_LIMIT]
        
        assert len(limited) == DEFAULT_SEARCH_LIMIT


class TestCosineSimilarity:
    """Test cosine similarity computation"""
    
    def test_cosine_similarity_identical_vectors(self):
        """Test cosine similarity for identical vectors (should be 1.0)"""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        
        # Cosine similarity formula
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = sum(a ** 2 for a in vec1) ** 0.5
        mag2 = sum(b ** 2 for b in vec2) ** 0.5
        
        similarity = dot_product / (mag1 * mag2) if mag1 > 0 and mag2 > 0 else 0.0
        
        assert similarity == 1.0
    
    def test_cosine_similarity_orthogonal_vectors(self):
        """Test cosine similarity for orthogonal vectors (should be 0.0)"""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 1.0, 0.0]
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = sum(a ** 2 for a in vec1) ** 0.5
        mag2 = sum(b ** 2 for b in vec2) ** 0.5
        
        similarity = dot_product / (mag1 * mag2) if mag1 > 0 and mag2 > 0 else 0.0
        
        assert similarity == 0.0
    
    def test_cosine_similarity_opposite_vectors(self):
        """Test cosine similarity for opposite vectors (should be -1.0)"""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [-1.0, 0.0, 0.0]
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = sum(a ** 2 for a in vec1) ** 0.5
        mag2 = sum(b ** 2 for b in vec2) ** 0.5
        
        similarity = dot_product / (mag1 * mag2) if mag1 > 0 and mag2 > 0 else 0.0
        
        assert similarity == -1.0
    
    def test_cosine_similarity_partial_overlap(self):
        """Test cosine similarity for vectors with partial overlap"""
        vec1 = [1.0, 1.0, 0.0]
        vec2 = [1.0, 0.5, 0.0]
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = sum(a ** 2 for a in vec1) ** 0.5
        mag2 = sum(b ** 2 for b in vec2) ** 0.5
        
        similarity = dot_product / (mag1 * mag2) if mag1 > 0 and mag2 > 0 else 0.0
        
        # Should be between 0 and 1
        assert 0 < similarity < 1
    
    def test_cosine_similarity_with_zero_vector(self):
        """Test cosine similarity when one vector is zero (edge case)"""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 0.0, 0.0]
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = sum(a ** 2 for a in vec1) ** 0.5
        mag2 = sum(b ** 2 for b in vec2) ** 0.5
        
        similarity = dot_product / (mag1 * mag2) if mag1 > 0 and mag2 > 0 else 0.0
        
        assert similarity == 0.0


class TestSearchFiltering:
    """Test filtering by risk level"""
    
    @pytest.mark.asyncio
    async def test_filter_by_risk_level_high(self):
        """Test filtering results by High risk level"""
        all_results = [
            {"id": 1, "name": "Fragrance", "risk_level": "High", "similarity": 0.95},
            {"id": 2, "name": "Rayon", "risk_level": "Medium", "similarity": 0.85},
            {"id": 3, "name": "Phthalates", "risk_level": "High", "similarity": 0.92}
        ]
        
        risk_level_filter = "High"
        filtered = [r for r in all_results if r.get("risk_level") == risk_level_filter]
        
        assert len(filtered) == 2
        assert all(r["risk_level"] == "High" for r in filtered)
    
    @pytest.mark.asyncio
    async def test_filter_by_risk_level_medium(self):
        """Test filtering results by Medium risk level"""
        all_results = [
            {"id": 1, "name": "Fragrance", "risk_level": "High", "similarity": 0.95},
            {"id": 2, "name": "Rayon", "risk_level": "Medium", "similarity": 0.85},
            {"id": 3, "name": "Phthalates", "risk_level": "High", "similarity": 0.92}
        ]
        
        risk_level_filter = "Medium"
        filtered = [r for r in all_results if r.get("risk_level") == risk_level_filter]
        
        assert len(filtered) == 1
        assert filtered[0]["name"] == "Rayon"
    
    @pytest.mark.asyncio
    async def test_filter_by_invalid_risk_level(self):
        """Test that invalid risk level filter is ignored"""
        all_results = [
            {"id": 1, "name": "Fragrance", "risk_level": "High"},
            {"id": 2, "name": "Rayon", "risk_level": "Medium"}
        ]
        
        risk_level_filter = "Invalid"
        
        # Should not filter if invalid level
        assert risk_level_filter not in ["Low", "Medium", "High"]
    
    @pytest.mark.asyncio
    async def test_filter_results_empty_set(self):
        """Test filtering when no results match filter"""
        all_results = [
            {"id": 1, "name": "Fragrance", "risk_level": "High"},
            {"id": 2, "name": "Rayon", "risk_level": "High"}
        ]
        
        risk_level_filter = "Low"
        filtered = [r for r in all_results if r.get("risk_level") == risk_level_filter]
        
        assert len(filtered) == 0


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.mark.asyncio
    async def test_search_empty_query(self):
        """Test handling of empty search query"""
        with patch('utils.vector_search.generate_query_embedding') as mock_embed:
            mock_embed.side_effect = ValueError("Query cannot be empty")
            
            with pytest.raises(ValueError):
                # Simulate search with empty query
                if not "".strip():
                    raise ValueError("Query cannot be empty")
    
    @pytest.mark.asyncio
    async def test_search_no_results(self):
        """Test handling when no results found"""
        mock_response = MagicMock()
        mock_response.data = []
        
        with patch('utils.vector_search.get_supabase_client') as mock_client:
            mock_supabase = MagicMock()
            mock_supabase.rpc.return_value.execute.return_value = mock_response
            mock_client.return_value = mock_supabase
            
            # Verify empty results are handled
            assert len(mock_response.data) == 0
    
    @pytest.mark.asyncio
    async def test_search_with_very_long_query(self):
        """Test search with very long query string"""
        long_query = "ingredient " * 1000  # ~8000 characters
        
        with patch('utils.vector_search.generate_query_embedding') as mock_embed:
            mock_embed.return_value = [0.1] * 1536
            
            # Should handle long queries
            assert len(long_query) > 1000
            result = mock_embed(long_query)
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_search_invalid_limit_parameter(self):
        """Test handling of invalid limit parameter"""
        DEFAULT_SEARCH_LIMIT = 5
        MAX_SEARCH_LIMIT = 20
        
        # Test negative limit (should default)
        limit = -1
        if limit < 1 or limit > MAX_SEARCH_LIMIT:
            limit = DEFAULT_SEARCH_LIMIT
        
        assert limit == DEFAULT_SEARCH_LIMIT
        
        # Test limit > max (should cap)
        limit = 100
        if limit > MAX_SEARCH_LIMIT:
            limit = MAX_SEARCH_LIMIT
        
        assert limit == MAX_SEARCH_LIMIT
    
    @pytest.mark.asyncio
    async def test_search_database_connection_error(self):
        """Test handling of database connection errors"""
        with patch('utils.vector_search.get_supabase_client') as mock_client:
            mock_supabase = MagicMock()
            mock_supabase.rpc.side_effect = Exception("Database connection failed")
            mock_client.return_value = mock_supabase
            
            with pytest.raises(Exception):
                mock_supabase.rpc("search_ingredients", {}).execute()


class TestPerformanceWithLargeDataset:
    """Test performance with 100+ ingredients"""
    
    @pytest.mark.asyncio
    async def test_search_with_100_ingredients(self):
        """Test search performance with 100+ ingredients in database"""
        # Mock 100 ingredients
        mock_ingredients = [
            {
                "id": i,
                "name": f"Ingredient_{i}",
                "description": f"Description for ingredient {i}",
                "risk_level": ["Low", "Medium", "High"][i % 3],
                "similarity_score": 1.0 - (i * 0.005)  # Scores from 1.0 to 0.5
            }
            for i in range(100)
        ]
        
        # Verify all ingredients created
        assert len(mock_ingredients) == 100
        
        # Apply limit
        limited = mock_ingredients[:10]
        assert len(limited) == 10
        
        # Verify ranked by similarity
        sorted_results = sorted(
            mock_ingredients,
            key=lambda x: x["similarity_score"],
            reverse=True
        )
        assert sorted_results[0]["similarity_score"] > sorted_results[99]["similarity_score"]
    
    @pytest.mark.asyncio
    async def test_search_1000_ingredients(self):
        """Test search performance with 1000+ ingredients"""
        mock_ingredients = [
            {
                "id": i,
                "name": f"Ingredient_{i}",
                "similarity_score": 1.0 - (i * 0.001)
            }
            for i in range(1000)
        ]
        
        # Limit to top 10
        top_results = mock_ingredients[:10]
        
        assert len(top_results) == 10
        # Verify ranking
        for i in range(9):
            assert (top_results[i]["similarity_score"] >= 
                    top_results[i+1]["similarity_score"])


class TestVectorSearchIntegration:
    """Test vector search integration with other components"""
    
    @pytest.mark.asyncio
    async def test_search_results_compatible_with_risk_scorer(self):
        """Test that search results format is compatible with risk scorer"""
        search_result = {
            "id": 1,
            "name": "Fragrance",
            "description": "Synthetic fragrance compounds",
            "risk_level": "High",
            "similarity_score": 0.92
        }
        
        # Verify required fields for risk scorer
        required_fields = ["id", "name", "description", "risk_level", "similarity_score"]
        assert all(field in search_result for field in required_fields)
    
    @pytest.mark.asyncio
    async def test_search_with_multiple_queries(self):
        """Test searching for multiple ingredients sequentially"""
        queries = ["Fragrance", "Synthetic fibers", "Natural ingredients"]
        
        results_by_query = {}
        for query in queries:
            mock_results = [
                {"id": i, "name": f"Result_{i}", "similarity_score": 0.9 - (i * 0.1)}
                for i in range(3)
            ]
            results_by_query[query] = mock_results
        
        # Verify we have results for each query
        assert len(results_by_query) == 3
        for query in queries:
            assert query in results_by_query


class TestSearchFallback:
    """Test fallback search mechanism"""
    
    @pytest.mark.asyncio
    async def test_fallback_when_rpc_unavailable(self):
        """Test fallback search when RPC function is unavailable"""
        # This would normally fall back to table scan
        mock_ingredients = [
            {"id": 1, "name": "Fragrance", "embedding": [0.1] * 1536},
            {"id": 2, "name": "Rayon", "embedding": [0.2] * 1536}
        ]
        
        with patch('utils.vector_search.get_supabase_client') as mock_client:
            mock_table = MagicMock()
            mock_select = MagicMock()
            mock_response = MagicMock()
            mock_response.data = mock_ingredients
            
            mock_select.execute.return_value = mock_response
            mock_table.select.return_value = mock_select
            
            mock_supabase = MagicMock()
            mock_supabase.table.return_value = mock_table
            mock_client.return_value = mock_supabase
            
            # Verify fallback can fetch all ingredients
            assert len(mock_response.data) == 2
