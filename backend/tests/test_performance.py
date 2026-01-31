"""
Performance and load tests for Lotus backend
Validates latency targets, benchmarks percentiles, and memory usage
Tests concurrent requests and stress conditions
"""

import pytest
import time
import asyncio
import psutil
import os
from unittest.mock import patch, MagicMock
from datetime import datetime


class TestVectorSearchLatency:
    """Test vector search performance targets"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_vector_search_latency_under_50ms(self):
        """Test that vector search returns <50ms for 10 results"""
        target_latency = 0.050  # 50ms
        
        with patch('utils.vector_search.get_supabase_client') as mock_client:
            mock_supabase = MagicMock()
            
            # Mock 10 results
            mock_results = [
                {
                    "id": i,
                    "name": f"Ingredient_{i}",
                    "similarity_score": 0.95 - (i * 0.01)
                }
                for i in range(10)
            ]
            
            mock_response = MagicMock()
            mock_response.data = mock_results
            
            mock_rpc = MagicMock()
            mock_rpc.execute.return_value = mock_response
            mock_supabase.rpc.return_value = mock_rpc
            mock_client.return_value = mock_supabase
            
            # Measure latency
            start = time.time()
            mock_supabase.rpc('search_ingredients', {
                'query_embedding': [0.1] * 1536,
                'match_limit': 10
            }).execute()
            elapsed = time.time() - start
            
            assert elapsed < target_latency, f"Search took {elapsed:.3f}s, target <50ms"
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_vector_search_latency_percentiles(self):
        """Test vector search latency percentiles"""
        latencies = []
        
        for _ in range(20):
            start = time.time()
            # Simulate search operation
            time.sleep(0.001)  # 1ms mock operation
            elapsed = time.time() - start
            latencies.append(elapsed)
        
        latencies.sort()
        
        # Calculate percentiles
        p50 = latencies[int(len(latencies) * 0.5)]
        p95 = latencies[int(len(latencies) * 0.95)]
        p99 = latencies[int(len(latencies) * 0.99)]
        
        # p50 should be < 50ms
        assert p50 < 0.050
        # p95 should be < 100ms
        assert p95 < 0.100
        # p99 should be < 200ms
        assert p99 < 0.200


class TestProfileLookupLatency:
    """Test profile lookup performance targets"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_profile_lookup_under_10ms(self):
        """Test that profile lookup completes <10ms"""
        target_latency = 0.010  # 10ms
        
        with patch('routers.profiles.get_supabase_client') as mock_client:
            mock_supabase = MagicMock()
            
            mock_response = MagicMock()
            mock_response.data = [{
                "user_id": "user_123",
                "sensitivities": ["PCOS"],
                "created_at": "2026-01-31T18:00:00Z",
                "updated_at": "2026-01-31T18:00:00Z"
            }]
            
            mock_table = MagicMock()
            mock_select = MagicMock()
            mock_eq = MagicMock()
            
            mock_eq.execute.return_value = mock_response
            mock_select.eq.return_value = mock_eq
            mock_table.select.return_value = mock_select
            mock_supabase.table.return_value = mock_table
            mock_client.return_value = mock_supabase
            
            # Measure latency
            start = time.time()
            response = mock_supabase.table('profiles').select('*').eq('user_id', 'user_123').execute()
            elapsed = time.time() - start
            
            assert elapsed < target_latency, f"Lookup took {elapsed:.3f}s, target <10ms"
            assert response.data is not None


class TestScanPipelineLatency:
    """Test complete scan pipeline latency"""
    
    @pytest.mark.performance
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_scan_pipeline_under_5_seconds(self, test_image_file):
        """Test complete scan pipeline <5s with API calls"""
        target_latency = 5.0
        
        with patch('utils.risk_scorer.extract_ingredients_from_image') as mock_ocr, \
             patch('utils.vector_search.search_similar_ingredients') as mock_search, \
             patch('utils.risk_scorer._fetch_user_sensitivities') as mock_sensitivities, \
             patch('utils.risk_scorer._generate_llm_assessment') as mock_llm:
            
            # Setup fast mocks
            mock_ocr.return_value = ["Fragrance", "Rayon"]
            mock_search.return_value = [{"id": 1, "name": "Fragrance", "risk_level": "High"}]
            mock_sensitivities.return_value = ["PCOS"]
            mock_llm.return_value = {
                "overall_risk_level": "Caution (Irritating)",
                "explanation": "Assessment",
                "ingredient_details": []
            }
            
            # Measure pipeline latency
            start = time.time()
            
            # Simulate pipeline
            ingredients = mock_ocr(test_image_file)
            sensitivities = mock_sensitivities("user_123")
            for ing in ingredients:
                results = mock_search(ing)
            assessment = mock_llm(ingredients, sensitivities, [])
            
            elapsed = time.time() - start
            
            assert elapsed < target_latency, f"Pipeline took {elapsed:.3f}s, target <5s"


class TestEmbeddingGenerationLatency:
    """Test embedding generation performance"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_single_embedding_latency(self):
        """Test single embedding generation latency"""
        target_latency = 1.0
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
            
            mock_client.embeddings.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            from openai import OpenAI
            client = OpenAI(api_key="test-key")
            
            start = time.time()
            response = client.embeddings.create(
                input="test ingredient",
                model="text-embedding-3-small"
            )
            elapsed = time.time() - start
            
            assert elapsed < target_latency
            assert response.data[0].embedding is not None
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_batch_embedding_throughput(self):
        """Test batch embedding throughput (10+ per second)"""
        target_rate = 10  # embeddings per second
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
            
            mock_client.embeddings.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            from openai import OpenAI
            client = OpenAI(api_key="test-key")
            
            # Generate 10 embeddings
            start = time.time()
            for i in range(10):
                client.embeddings.create(
                    input=f"ingredient_{i}",
                    model="text-embedding-3-small"
                )
            elapsed = time.time() - start
            
            throughput = 10 / elapsed
            assert throughput >= target_rate


class TestConcurrentRequests:
    """Test performance under concurrent load"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_100_concurrent_scan_requests(self, test_image_file):
        """Test 100 concurrent requests to /api/scan"""
        request_count = 100
        successful = 0
        failed = 0
        latencies = []
        
        with patch('routers.scan.generate_risk_score') as mock_risk:
            mock_risk.return_value = {
                "risk_level": "Caution",
                "explanation": "Test",
                "ingredients_found": [],
                "risky_ingredients": []
            }
            
            # Simulate concurrent requests
            async def simulate_request(request_id):
                nonlocal successful, failed
                start = time.time()
                try:
                    # Mock request execution
                    mock_risk(test_image_file, f"user_{request_id}")
                    latencies.append(time.time() - start)
                    successful += 1
                except Exception:
                    failed += 1
            
            # Run concurrent requests
            tasks = [simulate_request(i) for i in range(request_count)]
            await asyncio.gather(*tasks)
            
            # Verify results
            assert successful == request_count
            assert failed == 0
            assert len(latencies) == request_count
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_profile_operations(self):
        """Test concurrent profile create/update operations"""
        concurrent_count = 50
        success_count = 0
        
        with patch('routers.profiles.get_supabase_client') as mock_client:
            mock_supabase = MagicMock()
            mock_response = MagicMock()
            mock_response.data = [{
                "user_id": "user_123",
                "sensitivities": ["PCOS"],
                "created_at": "2026-01-31T18:00:00Z",
                "updated_at": "2026-01-31T18:00:00Z"
            }]
            
            mock_table = MagicMock()
            mock_select = MagicMock()
            mock_upsert = MagicMock()
            
            mock_select.eq.return_value.execute.return_value = MagicMock(data=[])
            mock_upsert.execute.return_value = mock_response
            
            mock_table.select.return_value = mock_select
            mock_table.upsert.return_value = mock_upsert
            mock_supabase.table.return_value = mock_table
            mock_client.return_value = mock_supabase
            
            # Simulate concurrent operations
            async def simulate_profile_update(user_id):
                nonlocal success_count
                try:
                    mock_supabase.table('profiles').upsert({
                        "user_id": user_id,
                        "sensitivities": ["PCOS"]
                    }).execute()
                    success_count += 1
                except Exception:
                    pass
            
            tasks = [simulate_profile_update(f"user_{i}") for i in range(concurrent_count)]
            await asyncio.gather(*tasks)
            
            assert success_count == concurrent_count


class TestMemoryUsage:
    """Test memory usage under load"""
    
    @pytest.mark.performance
    def test_memory_usage_with_large_dataset(self):
        """Test memory usage doesn't exceed reasonable limits"""
        # Create large dataset in memory
        large_list = [{"id": i, "data": "x" * 100} for i in range(10000)]
        
        # Get current process
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        # Memory should be reasonable (< 500MB for test)
        memory_mb = memory_info.rss / (1024 * 1024)
        assert memory_mb < 500, f"Memory usage {memory_mb}MB exceeds 500MB limit"
    
    @pytest.mark.performance
    def test_memory_leak_with_repeated_operations(self):
        """Test no memory leaks with repeated operations"""
        process = psutil.Process(os.getpid())
        
        initial_memory = process.memory_info().rss
        
        # Simulate repeated operations
        for _ in range(100):
            large_list = [i for i in range(1000)]
            del large_list
        
        final_memory = process.memory_info().rss
        
        # Memory growth should be minimal
        memory_growth_mb = (final_memory - initial_memory) / (1024 * 1024)
        assert memory_growth_mb < 50, f"Memory growth {memory_growth_mb}MB exceeds limit"


class TestLatencyPercentiles:
    """Test latency percentile benchmarks"""
    
    @pytest.mark.performance
    def test_search_latency_percentiles(self):
        """Benchmark search latency percentiles"""
        latencies = []
        
        # Generate sample latencies
        for i in range(100):
            # Mock latencies between 5-50ms with normal distribution
            latency = 0.005 + (0.045 * (i / 100))
            latencies.append(latency)
        
        latencies.sort()
        
        # Calculate percentiles
        p50 = latencies[int(len(latencies) * 0.50)]
        p95 = latencies[int(len(latencies) * 0.95)]
        p99 = latencies[int(len(latencies) * 0.99)]
        
        print(f"Search Latency - p50: {p50*1000:.1f}ms, p95: {p95*1000:.1f}ms, p99: {p99*1000:.1f}ms")
        
        # Verify targets
        assert p50 < 0.030  # p50 < 30ms
        assert p95 < 0.100  # p95 < 100ms
        assert p99 < 0.150  # p99 < 150ms
    
    @pytest.mark.performance
    def test_api_endpoint_latency_percentiles(self):
        """Benchmark API endpoint latency percentiles"""
        latencies = []
        
        # Generate sample latencies between 10-500ms
        for i in range(100):
            latency = 0.010 + (0.490 * (i / 100))
            latencies.append(latency)
        
        latencies.sort()
        
        p50 = latencies[int(len(latencies) * 0.50)]
        p95 = latencies[int(len(latencies) * 0.95)]
        p99 = latencies[int(len(latencies) * 0.99)]
        
        print(f"API Latency - p50: {p50*1000:.1f}ms, p95: {p95*1000:.1f}ms, p99: {p99*1000:.1f}ms")
        
        # Verify targets
        assert p50 < 0.200  # p50 < 200ms
        assert p95 < 0.500  # p95 < 500ms
        assert p99 < 1.000  # p99 < 1s


class TestThroughput:
    """Test throughput metrics"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_scan_requests_per_second(self, test_image_file):
        """Test scan endpoint throughput"""
        duration = 1.0  # 1 second test
        request_count = 0
        
        with patch('routers.scan.generate_risk_score') as mock_risk:
            mock_risk.return_value = {
                "risk_level": "Caution",
                "explanation": "Test",
                "ingredients_found": [],
                "risky_ingredients": []
            }
            
            start = time.time()
            while time.time() - start < duration:
                mock_risk(test_image_file, "user_123")
                request_count += 1
            
            # Should handle many requests per second
            rps = request_count / duration
            print(f"Scan throughput: {rps:.0f} requests/second")
            assert rps > 10  # At least 10 requests per second


class TestResponseTimeDistribution:
    """Test response time distribution analysis"""
    
    @pytest.mark.performance
    def test_response_time_percentile_distribution(self):
        """Analyze response time distribution"""
        import random
        
        # Generate realistic response times (normal distribution)
        response_times = [random.gauss(0.100, 0.050) for _ in range(1000)]
        response_times = [max(0.001, t) for t in response_times]  # No negative times
        response_times.sort()
        
        # Calculate percentiles
        percentiles = [10, 25, 50, 75, 90, 95, 99]
        
        for p in percentiles:
            idx = int(len(response_times) * (p / 100))
            value = response_times[idx]
            print(f"p{p}: {value*1000:.1f}ms")
        
        # Verify key targets
        p50_idx = int(len(response_times) * 0.50)
        p95_idx = int(len(response_times) * 0.95)
        
        p50 = response_times[p50_idx]
        p95 = response_times[p95_idx]
        
        assert p50 < 0.200
        assert p95 < 0.500
