import pytest
from scorer import calculate_user_rating
from streamlit.testing.v1 import AppTest

# 🧪 Unit Test: Verifies your custom A+ threshold bounds math works
def test_scorer_perfection_cap():
    perfect_user = {
        "public_repos": 40,  # Caps max 35 scale score
        "followers": 100,    # Drives max network reach 
        "following": 5,      # Solid high ratio factor
        "bio": "Staff Architect", "blog": "https://dev.to", "company": "OS Corp"
    }
    results = calculate_user_rating(perfect_user)
    assert results["total_score"] == 100.0
    assert results["grade"] == "A+"

# 🧪 Unit Test: Verifies your empty profile fallbacks work without dividing by zero
def test_scorer_empty_network_fallback():
    empty_user = {
        "public_repos": 0, "followers": 0, "following": 0,
        "bio": None, "blog": None, "email": None, "company": None
    }
    results = calculate_user_rating(empty_user)
    # scale(0) + network_no_followers(10) + brand_incomplete(5) = 15.0
    assert results["total_score"] == 15.0
    assert results["grade"] == "D"

# 🧪 UI Test: Ensures Streamlit compiles cleanly with zero crash states
def test_streamlit_integration():
    at = AppTest.from_file("main.py")
    at.secrets["GITHUB_TOKEN"] = "mock_secret_key"
    at.run()
    assert not at.exception
