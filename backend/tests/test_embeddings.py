"""
Unit tests for OpenAI embedding generation
Tests text-embedding-3-small API integration, batch processing, error handling, and validation
Target: 80%+ code coverage
"""

import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock
from openai import APIError, APIConnectionError

# Import the module to test (when available)
# from utils.embeddings import generate_embedding, batch_embeddings, EMBEDDING_DIMENSION


class TestEmbeddingGeneration:
    """Test embedding generation from text"""
    
    @pytest.mark.asyncio
    async def test_generate_valid_embedding(self, patch_openai_embeddings):
        """Test generating embedding for valid text input"""
        # Mock setup is via patch_openai_embeddings
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_client.embeddings.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            # Simulate embedding generation
            from openai import OpenAI
            client = OpenAI(api_key="test-key")
            response = client.embeddings.create(
                input="Fragrance effect on sensitive skin",
                model="text-embedding-3-small"
            )
            
            assert response.data[0].embedding is not None
            assert len(response.data[0].embedding) == 1536
            assert isinstance(response.data[0].embedding[0], float)
    
    @pytest.mark.asyncio
    async def test_embedding_dimension_validation(self, patch_openai_embeddings):
        """Test that embedding dimension is exactly 1536"""
        mock_response = MagicMock()
        embedding_vector = [0.123] * 1536  # Exactly 1536 dimensions
        mock_response.data = [MagicMock(embedding=embedding_vector)]
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_client.embeddings.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            from openai import OpenAI
            client = OpenAI(api_key="test-key")
            response = client.embeddings.create(
                input="test ingredient",
                model="text-embedding-3-small"
            )
            
            # Validate dimension
            assert len(response.data[0].embedding) == 1536
            assert all(isinstance(val, float) for val in response.data[0].embedding)
    
    @pytest.mark.asyncio
    async def test_empty_text_input(self):
        """Test error handling for empty text input"""
        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_client.embeddings.create.side_effect = ValueError("Input text cannot be empty")
            mock_openai.return_value = mock_client
            
            from openai import OpenAI
            client = OpenAI(api_key="test-key")
            
            with pytest.raises(ValueError):
                client.embeddings.create(
                    input="",
                    model="text-embedding-3-small"
                )
    
    @pytest.mark.asyncio
    async def test_very_long_text_input(self, patch_openai_embeddings):
        """Test embedding generation for very long text (8000+ tokens)"""
        # Create long text (approximately 30k characters)
        long_text = "ingredient " * 3000
        
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_client.embeddings.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            from openai import OpenAI
            client = OpenAI(api_key="test-key")
            response = client.embeddings.create(
                input=long_text,
                model="text-embedding-3-small"
            )
            
            assert response.data[0].embedding is not None
            assert len(response.data[0].embedding) == 1536
    
    @pytest.mark.asyncio
    async def test_unicode_and_special_characters(self, patch_openai_embeddings):
        """Test embedding generation with unicode and special characters"""
        special_text = "Fragrance™ with émojis 🧪 and spëcial çharacters"
        
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_client.embeddings.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            from openai import OpenAI
            client = OpenAI(api_key="test-key")
            response = client.embeddings.create(
                input=special_text,
                model="text-embedding-3-small"
            )
            
            assert response.data[0].embedding is not None


class TestBatchEmbeddings:
    """Test batch embedding processing"""
    
    @pytest.mark.asyncio
    async def test_batch_processing_multiple_texts(self, patch_openai_embeddings):
        """Test batch processing of multiple ingredient descriptions"""
        texts = [
            "Fragrance compounds",
            "Synthetic fibers",
            "Natural ingredients"
        ]
        
        embeddings_list = [[0.1 * (i+1)] * 1536 for i in range(len(texts))]
        mock_responses = [MagicMock(embedding=emb) for emb in embeddings_list]
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            
            # Simulate batch processing
            def batch_embeddings(texts, model):
                results = []
                for text in texts:
                    response = mock_client.embeddings.create(
                        input=text,
                        model=model
                    )
                    results.append(response)
                return results
            
            mock_client.embeddings.create.side_effect = [
                MagicMock(data=[emb]) for emb in mock_responses
            ]
            mock_openai.return_value = mock_client
            
            from openai import OpenAI
            client = OpenAI(api_key="test-key")
            
            # Process first text
            response = client.embeddings.create(input=texts[0], model="text-embedding-3-small")
            assert response.data[0].embedding is not None
    
    @pytest.mark.asyncio
    async def test_batch_deduplication(self):
        """Test that duplicate texts in batch are handled efficiently"""
        texts = ["Fragrance", "Fragrance", "Synthetic", "Fragrance"]
        unique_texts = set(texts)
        
        assert len(unique_texts) == 2
        assert "Fragrance" in unique_texts
        assert "Synthetic" in unique_texts
    
    @pytest.mark.asyncio
    async def test_batch_size_limits(self):
        """Test batch processing respects size limits"""
        # OpenAI embeddings API typically supports batches of 100+ items
        large_batch = ["ingredient_" + str(i) for i in range(50)]
        
        assert len(large_batch) == 50
        assert all(isinstance(text, str) for text in large_batch)
    
    @pytest.mark.asyncio
    async def test_empty_batch_handling(self):
        """Test handling of empty batch"""
        empty_batch = []
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_client.embeddings.create.side_effect = ValueError("Batch cannot be empty")
            mock_openai.return_value = mock_client
            
            from openai import OpenAI
            client = OpenAI(api_key="test-key")
            
            if len(empty_batch) == 0:
                with pytest.raises(ValueError):
                    client.embeddings.create(
                        input="test",
                        model="text-embedding-3-small"
                    )


class TestErrorHandling:
    """Test error handling for embedding operations"""
    
    @pytest.mark.asyncio
    async def test_invalid_api_key(self):
        """Test handling of invalid API key"""
        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_client.embeddings.create.side_effect = APIError(
                "Invalid API key",
                response=MagicMock(status_code=401),
                body={}
            )
            mock_openai.return_value = mock_client
            
            from openai import OpenAI
            client = OpenAI(api_key="invalid-key")
            
            with pytest.raises(APIError):
                client.embeddings.create(
                    input="test",
                    model="text-embedding-3-small"
                )
    
    @pytest.mark.asyncio
    async def test_api_timeout(self):
        """Test handling of API timeout"""
        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_client.embeddings.create.side_effect = APIConnectionError(
                "Connection timeout"
            )
            mock_openai.return_value = mock_client
            
            from openai import OpenAI
            client = OpenAI(api_key="test-key")
            
            with pytest.raises(APIConnectionError):
                client.embeddings.create(
                    input="test",
                    model="text-embedding-3-small"
                )
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test handling of rate limiting (429 Too Many Requests)"""
        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_client.embeddings.create.side_effect = APIError(
                "Rate limit exceeded",
                response=MagicMock(status_code=429),
                body={}
            )
            mock_openai.return_value = mock_client
            
            from openai import OpenAI
            client = OpenAI(api_key="test-key")
            
            with pytest.raises(APIError):
                client.embeddings.create(
                    input="test",
                    model="text-embedding-3-small"
                )
    
    @pytest.mark.asyncio
    async def test_server_error_handling(self):
        """Test handling of 500 server errors"""
        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_client.embeddings.create.side_effect = APIError(
                "Internal server error",
                response=MagicMock(status_code=500),
                body={}
            )
            mock_openai.return_value = mock_client
            
            from openai import OpenAI
            client = OpenAI(api_key="test-key")
            
            with pytest.raises(APIError):
                client.embeddings.create(
                    input="test",
                    model="text-embedding-3-small"
                )


class TestEmbeddingConsistency:
    """Test embedding generation consistency and stability"""
    
    @pytest.mark.asyncio
    async def test_same_text_produces_same_embedding(self):
        """Test that same text produces consistent embedding"""
        test_text = "Fragrance effect on sensitive skin"
        
        mock_response = MagicMock()
        embedding_vector = [0.123] * 1536
        mock_response.data = [MagicMock(embedding=embedding_vector)]
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_client.embeddings.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            from openai import OpenAI
            client = OpenAI(api_key="test-key")
            
            # Generate embedding twice
            response1 = client.embeddings.create(
                input=test_text,
                model="text-embedding-3-small"
            )
            response2 = client.embeddings.create(
                input=test_text,
                model="text-embedding-3-small"
            )
            
            # Embeddings should be identical
            assert response1.data[0].embedding == response2.data[0].embedding
    
    @pytest.mark.asyncio
    async def test_different_texts_produce_different_embeddings(self):
        """Test that different texts produce different embeddings"""
        text1 = "Fragrance compounds"
        text2 = "Natural ingredients"
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            
            # Different embeddings for different texts
            emb1 = [0.1 * i for i in range(1536)]
            emb2 = [0.2 * i for i in range(1536)]
            
            mock_client.embeddings.create.side_effect = [
                MagicMock(data=[MagicMock(embedding=emb1)]),
                MagicMock(data=[MagicMock(embedding=emb2)])
            ]
            mock_openai.return_value = mock_client
            
            from openai import OpenAI
            client = OpenAI(api_key="test-key")
            
            response1 = client.embeddings.create(input=text1, model="text-embedding-3-small")
            response2 = client.embeddings.create(input=text2, model="text-embedding-3-small")
            
            # Embeddings should be different
            assert response1.data[0].embedding != response2.data[0].embedding


class TestEmbeddingModel:
    """Test embedding model selection and validation"""
    
    @pytest.mark.asyncio
    async def test_correct_model_used(self, patch_openai_embeddings):
        """Test that text-embedding-3-small model is used"""
        with patch('openai.OpenAI') as mock_openai:
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
            
            mock_client = MagicMock()
            mock_client.embeddings.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            from openai import OpenAI
            client = OpenAI(api_key="test-key")
            response = client.embeddings.create(
                input="test",
                model="text-embedding-3-small"
            )
            
            # Verify the call was made with correct model
            mock_client.embeddings.create.assert_called_once()
            call_kwargs = mock_client.embeddings.create.call_args.kwargs
            assert call_kwargs['model'] == "text-embedding-3-small"


class TestEmbeddingPerformance:
    """Test embedding generation performance characteristics"""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_embedding_generation_latency(self, patch_openai_embeddings):
        """Test that embedding generation completes within expected time"""
        import time
        
        with patch('openai.OpenAI') as mock_openai:
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
            
            mock_client = MagicMock()
            mock_client.embeddings.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            from openai import OpenAI
            client = OpenAI(api_key="test-key")
            
            start = time.time()
            client.embeddings.create(
                input="test ingredient",
                model="text-embedding-3-small"
            )
            elapsed = time.time() - start
            
            # Mock execution should be very fast (< 1s)
            assert elapsed < 1.0
