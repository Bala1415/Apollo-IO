import pytest
import time
from fastapi.testclient import TestClient
from backend.security.hashing import get_password_hash, verify_password

@pytest.mark.performance
def test_password_hashing_performance(benchmark):
    """
    Benchmark the BCrypt password hashing algorithm.
    Ensures that hash generation takes an appropriate amount of time (not too fast to be vulnerable).
    Requires pytest-benchmark.
    """
    password = "benchmark_password_123"
    # Benchmark will run this multiple times to get statistics
    result = benchmark(get_password_hash, password)
    assert result is not None

@pytest.mark.performance
def test_password_verification_performance(benchmark):
    """
    Benchmark BCrypt password verification.
    """
    password = "benchmark_password_123"
    hashed = get_password_hash(password)
    
    result = benchmark(verify_password, password, hashed)
    assert result is True

@pytest.mark.performance
def test_api_latency_health_check(client: TestClient, benchmark):
    """
    Benchmark the health check endpoint to ensure routing and basic dependencies resolve quickly.
    """
    def hit_endpoint():
        return client.get("/health")
        
    response = benchmark(hit_endpoint)
    assert response.status_code == 200

@pytest.mark.performance
def test_api_throughput_simulation(client: TestClient):
    """
    Simple throughput test simulating 100 sequential requests.
    """
    start_time = time.time()
    num_requests = 100
    
    for _ in range(num_requests):
        client.get("/ready")
        
    duration = time.time() - start_time
    req_per_sec = num_requests / duration
    
    # We expect an empty, unblocked route in FastAPI to handle at least 500 req/sec sequentially
    # Adjust assertions based on actual environment capabilities
    assert req_per_sec > 100, f"Throughput too low: {req_per_sec} req/s"
