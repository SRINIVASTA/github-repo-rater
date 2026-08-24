from datetime import datetime

def calculate_user_rating(data: dict, repos_data: list = None) -> dict:
    """
    Evaluates global GitHub User Profile metrics to return a balanced score out of 100.
    Integrates direct repository payload monitoring vectors.
    """
    if repos_data is None:
        repos_data = []

    public_repos = data.get("public_repos", 0)
    followers = data.get("followers", 0)
    following = data.get("following", 0)
    
    # 1. Experience & Scale Index (Max 25 pts)
    # Extracts genuine ownership by filtering out unoriginal repo forks
    source_repos = [r for r in repos_data if not r.get("fork", False)]
    owned_count = len(source_repos) if repos_data else public_repos
    scale_score = min(25, owned_count * 2.5)

    # 2. Influence & Professional Network Reach (Max 25 pts)
    if followers == 0:
        network_score = 5
    else:
        ratio = followers / max(1, following)
        network_score = min(25, 10 + (followers * 0.1) + (ratio * 1.5))

    # 3. Profile Optimization & Branding (Max 25 pts)
    has_bio = 10 if data.get("bio") else 0
    has_blog = 10 if data.get("blog") else 0
    has_identity = 5 if (data.get("email") or data.get("company") or data.get("location")) else 0
    brand_score = has_bio + has_blog + has_identity

    # 4. Evaluation Module: Quality & Active Maintenance (Max 25 pts)
    quality_score = 0
    if repos_data:
        # Measure community social proof engagement metrics
        total_stars = sum(r.get("stargazers_count", 0) for r in repos_data)
        quality_score += min(15, total_stars * 3)
        
        # Monitor maintenance timelines over a strict 90-day window
        recent_updates = 0
        now = datetime.utcnow()
        for repo in repos_data:
            updated_at_str = repo.get("updated_at")
            if updated_at_str:
                try:
                    updated_at = datetime.strptime(updated_at_str, "%Y-%m-%dT%H:%M:%SZ")
                    if (now - updated_at).days <= 90:
                        recent_updates += 1
                except ValueError:
                    continue
        quality_score += min(10, recent_updates * 2)

    # Balance total calculations matrix spectrum bounds
    total_score = round(scale_score + network_score + brand_score + quality_score, 1)
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
            "Codebase Portfolio": round(scale_score, 1),
            "Network Influence": round(network_score, 1),
            "Profile Optimization": round(brand_score, 1),
            "Evaluation Module": round(quality_score, 1)
        }
    }
