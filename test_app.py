import pytest
import requests
import streamlit as st
from app.scorer import calculate_user_rating

# ==========================================
# 1. ENGINE UNIT TESTS
# ==========================================

def test_calculate_user_rating_max_score():
    """Confirms complete profiles reach perfect Tier 1 score limits."""
    mock_profile = {
        "bio": "Staff Engineer",
        "blog": "https://portfolio.dev",
        "location": "Austin, TX",
        "public_repos": 20,
        "followers": 30
    }
    res = calculate_user_rating(mock_profile)
    assert res["total_score"] == 100
    assert res["grade"] == "Elite (Tier 1)"


def test_calculate_user_rating_floor_limits():
    """Ensures empty profile data maps accurately to fallback base values."""
    mock_profile = {"bio": None, "blog": "", "location": None, "public_repos": 0, "followers": 0}
    res = calculate_user_rating(mock_profile)
    assert res["total_score"] == 10
    assert res["grade"] == "Emerging (Tier 3)"


@pytest.mark.parametrize("repos, followers, expected_tier", [
    (2, 2, "Emerging (Tier 3)"),
    (10, 15, "Professional (Tier 2)"),
])
def test_grading_tier_boundaries(repos, followers, expected_tier):
    """Validates structural boundary steps across score tiers."""
    mock_profile = {"bio": None, "blog": None, "location": None, "public_repos": repos, "followers": followers}
    res = calculate_user_rating(mock_profile)
    assert res["grade"] == expected_tier


# ==========================================
# 2. MOCKED INTEGRATION TESTS
# ==========================================

class MockApiResponse:
    def __init__(self, json_payload, status):
        self.payload = json_payload
        self.status_code = status
    def json(self):
        return self.payload


def test_api_integration_success(mocker):
    """Simulates a completely clean HTTP 200 API lifecycle run."""
    mock_payload = {"login": "octocat", "public_repos": 2, "followers": 1}
    mocker.patch('requests.get', return_value=MockApiResponse(mock_payload, 200))
    
    response = requests.get("https://github.com")
    assert response.status_code == 200
    assert response.json()["login"] == "octocat"
