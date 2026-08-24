def calculate_user_rating(data: dict) -> dict:
    """
    Evaluates global GitHub User Profile metrics to return a balanced score out of 100.
    """
    public_repos = data.get("public_repos", 0)
    followers = data.get("followers", 0)
    following = data.get("following", 0)
    
    # 1. Experience & Scale Index (Max 35 pts)
    # Rewards active development. Caps out at 35 public repositories.
    scale_score = min(35, public_repos * 1.5)

    # 2. Influence & Professional Network Reach (Max 35 pts)
    # Uses follower counts to weight network impact smoothly
    if followers == 0:
        network_score = 10
    else:
        # A positive followers-to-following ratio signals organic network value
        ratio = followers / max(1, following)
        network_score = min(35, 15 + (followers * 0.2) + (ratio * 2.0))

    # 3. Profile Completeness & Personal Brand (Max 30 pts)
    # Evaluates bio components, professional websites, and hireability state flags
    has_bio = 10 if data.get("bio") else 0
    has_blog = 10 if data.get("blog") else 0
    has_email_or_company = 10 if (data.get("email") or data.get("company")) else 5
    brand_score = has_bio + has_blog + has_email_or_company

    # Compile Weights
    total_score = round(scale_score + network_score + brand_score, 1)
    total_score = min(100.0, max(0.0, total_score))

    # Grade Threshold Mapping Boundaries
    if total_score >= 85: grade = "A+"
    elif total_score >= 70: grade = "A"
    elif total_score >= 55: grade = "B"
    elif total_score >= 40: grade = "C"
    else: grade = "D"
    
    return {
        "total_score": total_score,
        "grade": grade,
        "breakdown": {
            "Codebase Portfolio Scale": round(scale_score, 1),
            "Network Influence Index": round(network_score, 1),
            "Profile Optimization": round(brand_score, 1)
        }
    }
