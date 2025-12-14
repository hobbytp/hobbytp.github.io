import requests
import pytest
import os

# Assuming the base URL is provided via environment variable or default to local dev
BASE_URL = os.getenv("BASE_URL", "http://localhost:8788")

def test_api_status():
    """
    Test the /api/status endpoint to ensure it returns the correct health information.
    """
    try:
        response = requests.get(f"{BASE_URL}/api/status")
    except requests.exceptions.ConnectionError:
        pytest.skip("Local server is not running. Skipping integration test.")

    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert "db_status" in data
    assert "ai_status" in data
    assert "timestamp" in data
    
    # Ideally, we expect the system to be healthy
    if data["status"] == "ok":
        assert data["db_status"] == "connected"
        assert data["ai_status"] == "connected"
