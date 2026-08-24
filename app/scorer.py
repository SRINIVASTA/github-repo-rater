import math
from datetime import datetime

def calculate_gitscore_100(user_data: dict, repos_data: list) -> dict:
    """
    Replicates the GitScore Methodology compressed into an absolute 100-point scale.
    Weights are divided natively across all 6 core categories.
    """
    # Extract baseline user statistics
    public_repos = user_data.get("public_repos", 0)
    followers = user_data.get("followers", 0)
    following = user_data.get("following", 0)
    created_at_str = user_data.get("created_at", "")
    
    # Pre-calculate aggregate repository properties
    total_stars = sum(r.get("stargazers_count", 0) for r in repos_data)
    total_forks = sum(r.get("forks_count", 0) for r in repos_data)
    
    languages = set()
    for r in repos_data:
        lang = r.get("language")
        if lang:
            languages.add(lang)
            
    # -------------------------------------------------------------
    # 1. Repository Quality (Max 25 Points)
    # -------------------------------------------------------------
    repo_baseline = min(5.0, public_repos * 0.5)
    star_bonus = min(12.0, math.log1p(total_stars) * 2.5)
    fork_bonus = min(8.0, total_forks * 1.0)
    category_1 = round(repo_baseline + star_bonus + fork_bonus, 1)

    # -------------------------------------------------------------
    # 2. Activity & Consistency (Max 20 Points)
    # -------------------------------------------------------------
    total_issues = sum(r.get("open_issues_count", 0) for r in repos_data)
    # Base starting factor + increments based on active tracking lines
    category_2 = min(20.0, 6.0 + (public_repos * 0.4) + (total_issues * 0.2))

    # -------------------------------------------------------------
    # 3. Community Impact (Max 25 Points)
    # -------------------------------------------------------------
    viral_multiplier = 1.5 if len([r for r in repos_data if r.get("stargazers_count", 0) > 2]) > 0 else 1.0
    category_3 = min(25.0, (total_stars * 1.5 + total_forks * 2.0) * viral_multiplier)
    if category_3 == 0 and public_repos > 0:
        category_3 = 2.0  # Safe harbor cushion points for valid work codebases

    # -------------------------------------------------------------
    # 4. Social Influence (Max 15 Points)
    # -------------------------------------------------------------
    follower_log = min(10.0, math.log1p(followers) * 2.5)
    ratio = followers / max(1, following)
    ratio_bonus = min(5.0, ratio * 0.5)
    category_4 = round(follower_log + ratio_bonus, 1)

    # -------------------------------------------------------------
    # 5. Language Diversity (Max 10 Points)
    # -------------------------------------------------------------
    lang_count = len(languages)
    if lang_count <= 1:
        category_5 = 3.0
    elif lang_count == 2:
        category_5 = 6.0
    elif lang_count == 3:
        category_5 = 8.5
    else:
        category_5 = 10.0  # Max polyglot metric score tier

    # -------------------------------------------------------------
    # 6. Account Longevity (Max 5 Points)
    # -------------------------------------------------------------
    category_6 = 1.0
    if created_at_str:
        try:
            created_year = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%SZ").year
            current_year = datetime.now().year
            account_age = max(0, current_year - created_year)
            category_6 = min(5.0, 1.0 + (account_age * 0.5))
        except Exception:
            pass

    # Final Aggregation Summaries
    total_score = round(category_1 + category_2 + category_3 + category_4 + category_5 + category_6, 1)
    total_score = min(100.0, max(0.0, total_score))

    # Traditional Letter Grade Cutoffs
    if total_score >= 85: grade = "Elite Master (A+)"
    elif total_score >= 70: grade = "Advanced Maintainer (A)"
    elif total_score >= 50: grade = "Active Contributor (B)"
    elif total_score >= 30: grade = "Rising Developer (C)"
    else: grade = "Novice Footprint (D)"

    return {
        "total_score": total_score,
        "grade": grade,
        "breakdown": {
            "Repository Quality (Max 25)": round(category_1, 1),
            "Activity & Consistency (Max 20)": round(category_2, 1),
            "Community Impact (Max 25)": round(category_3, 1),
            "Social Influence (Max 15)": round(category_4, 1),
            "Language Diversity (Max 10)": round(category_5, 1),
            "Account Longevity (Max 5)": round(category_6, 1)
        }
    }
