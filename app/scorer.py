def calculate_rating(data: dict) -> dict:
    """
    Evaluates repository metrics to return an unified score scale out of 100.
    """
    stars = data.get("stargazers_count", 0)
    forks = data.get("forks_count", 0)
    
    # Scale popularity metrics (Max 30 pts)
    popularity = min(30, (stars * 0.1) + (forks * 0.2))
    
    # Scale active open issue volume (Max 40 pts)
    issues = data.get("open_issues_count", 0)
    activity = 40 if issues < 12 else max(10, 40 - (issues * 0.4))
    
    # Code metadata properties (Max 30 pts)
    has_desc = 15 if data.get("description") else 0
    has_license = 15 if data.get("license") else 0
    health = has_desc + has_license
    
    total = round(popularity + activity + health, 1)
    
    # Boundary thresholds
    if total >= 80: grade = "A+"
    elif total >= 65: grade = "A"
    elif total >= 50: grade = "B"
    else: grade = "C"
    
    return {
        "total_score": total,
        "grade": grade,
        "breakdown": {"Popularity": popularity, "Activity": activity, "Health": health}
    }
