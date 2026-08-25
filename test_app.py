import sys
import os
import pytest

# Forces Python runtime to read inside the /app/ subfolder directory structure
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) or '.'))

from app.scorer import calculate_user_rating
from streamlit.testing.v1 import AppTest

# ==============================================================================
# 🧪 SCORER UNIT TESTS
# ==============================================================================

def test_scorer_perfect_score_cap():
    perfect_user = {
        "public_repos": 40, "followers": 200, "following": 5,
        "bio": "Staff Architect", "blog": "https://dev.to", "company": "OS Corp"
    }
    results = calculate_user_rating(perfect_user)
    assert results["total_score"] == 100.0
    assert results["grade"] == "A+"


def test_scorer_zero_followers_fallback():
    zero_follower_user = {
        "public_repos": 10, "followers": 0, "following": 15,
        "bio": "New Account", "blog": "", "email": None, "company": None
    }
    results = calculate_user_rating(zero_follower_user)
    assert results["total_score"] == 40.0
    assert results["grade"] == "C"


def test_scorer_empty_profile_minimum_bounds():
    blank_user = {
        "public_repos": 0, "followers": 0, "following": 0,
        "bio": None, "blog": None, "email": None, "company": None
    }
    results = calculate_user_rating(blank_user)
    assert results["total_score"] == 15.0
    assert results["grade"] == "D"


# ==============================================================================
# 🧪 INTEGRATION TEST: STREAMLIT FRAMEWORK COMPILE
# ==============================================================================

def test_streamlit_ui_initialization():
    at = AppTest.from_file("app/main.py")
    at.secrets["GITHUB_TOKEN"] = "mock_secret_key"
    at.run()
    assert not at.exception
    assert len(at.text_input) > 0
    assert len(at.button) > 0
