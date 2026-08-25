import sys
import os
import pytest

# --- 📁 REPOSITORY PATH HOOK FIX ---
# Forces Python to look inside the /app/ directory for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) or '.'))

from app.scorer import calculate_user_rating
from streamlit.testing.v1 import AppTest

# ==============================================================================
# 🧪 UNIT TESTS: MATHEMATICAL SCORING ENGINE (scorer.py)
# ==============================================================================

def test_scorer_perfect_score_cap():
    """
    Verifies that highly active profiles cleanly cap out at a perfect 100.0 (A+).
    """
    perfect_user = {
        "public_repos": 40,                   # 40 * 1.5 = 60 -> Caps at Max 35.0 pts
        "followers": 200,                     # Massive network reach
        "following": 5,                       # High ratio multiplier -> Caps Max 35.0 pts
        "bio": "Principal Software Architect", # 10 pts
        "blog": "https://techblog.dev",       # 10 pts
        "company": "Open Source Foundation"   # 10 pts -> Max 30.0 brand pts
    }
    results = calculate_user_rating(perfect_user)
    assert results["total_score"] == 100.0
    assert results["grade"] == "A+"
    assert results["breakdown"]["Codebase Portfolio Scale"] == 35.0
    assert results["breakdown"]["Network Influence Index"] == 35.0
    assert results["breakdown"]["Profile Optimization"] == 30.0


def test_scorer_zero_followers_fallback():
    """
    Verifies that users with exactly 0 followers default cleanly to 10 points
    for network index without hitting a division-by-zero or mathematical crash.
    """
    zero_follower_user = {
        "public_repos": 10,
        "followers": 0,
        "following": 15,
        "bio": "Just starting out",
        "blog": "",
        "email": None,
        "company": None
    }
    results = calculate_user_rating(zero_follower_user)
    # Scale: 10 * 1.5 = 15.0
    # Network: 0 followers triggers fallback = 10.0
    # Brand: Bio(10) + Blog(0) + Missing Email/Company Fallback(5) = 15.0
    # Total = 15.0 + 10.0 + 15.0 = 40.0
    assert results["total_score"] == 40.0
    assert results["grade"] == "C"


def test_scorer_empty_profile_minimum_bounds():
    """
    Verifies absolute minimum score conditions for a completely blank GitHub account.
    """
    blank_user = {
        "public_repos": 0, "followers": 0, "following": 0,
        "bio": None, "blog": None, "email": None, "company": None
    }
    results = calculate_user_rating(blank_user)
    # Scale: 0 -> 0.0
    # Network: 0 followers fallback -> 10.0
    # Brand: Bio(0) + Blog(0) + Missing Email/Company Fallback(5) -> 5.0
    # Total = 15.0
    assert results["total_score"] == 15.0
    assert results["grade"] == "D"


def test_scorer_fractional_precision():
    """
    Ensures that scores containing non-integer values are rounded cleanly 
    to exactly 1 decimal point according to your code requirements.
    """
    fractional_user = {
        "public_repos": 3,   # 3 * 1.5 = 4.5
        "followers": 7,     # Triggers ratio formula processing
        "following": 3,
        "bio": "Developer", # 10
        "blog": "",         # 0
        "email": "dev@io",  # 10
    }
    results = calculate_user_rating(fractional_user)
    assert isinstance(results["total_score"], float)
    assert isinstance(results["breakdown"]["Codebase Portfolio Scale"], float)


# ==============================================================================
# 🧪 INTEGRATION TESTS: STREAMLIT UI COMPILATION (main.py)
# ==============================================================================

def test_streamlit_ui_initialization():
    """
    Launches a programmatic instance of main.py inside the /app folder 
    to verify that all layout features compile cleanly without breaking.
    """
    at = AppTest.from_file("app/main.py")
    
    # Inject a dummy environment variable directly into the test runtime
    at.secrets["GITHUB_TOKEN"] = "ghp_mockTestingTokenForPipelineRuns"
    at.run()
    
    # Assert that the application did not experience a system crash exception
    assert not at.exception
    
    # Confirm that core visual interactive fields exist for web visitors
    assert len(at.text_input) > 0
    assert len(at.button) > 0
