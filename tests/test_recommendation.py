import pytest
import requests

BASE_URL = "http://localhost:8000"  # Change this if deployed elsewhere

def test_recommendations():
    """Test the /recommend/ endpoint on a running FastAPI server."""

    customer_id = 2726055  
    response = requests.get(f"{BASE_URL}/recommend/?customer_id={customer_id}&top_n=2")

    
    assert response.status_code == 200  # Ensure successful response
    
    data = response.json()
    
    assert "customer_id" in data
    assert "top_matches" in data
    assert "recall_count" in data
    assert isinstance(data["top_matches"], list)
    assert len(data["top_matches"]) <= 2
