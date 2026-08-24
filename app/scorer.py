def calculate_rating(data: dict) -> dict:
    """
    Enterprise-Grade GitHub Rater Engine: Built to correctly analyze heavy production 
    frameworks, algorithmic utilities, local databases, and zero-issue codebases.
    """
    # 1. Scale Stats
    open_issues = data.get("open_issues_count", 0)
    has_wiki = data.get("has_wiki", False)
    repo_size = data.get("size", 0)  # Measured in KB
    
    # 2. Structural Complexity Score (Max 35 pts)
    # Reward heavy, full-stack multi-file architectures over lightweight scripts
    if repo_size > 5000:
        complexity_score = 35
    elif repo_size > 1000:
        complexity_score = 30
    else:
        complexity_score = 15 + min(15, repo_size * 0.01)

    # 3. Clean Issue Maintenance Score (Max 35 pts)
    # Zero open issues represents a pristine, highly stable application codebase
    if open_issues == 0:
        maintenance_score = 35
    elif open_issues < 5:
        maintenance_score = 30
    elif open_issues < 15:
        maintenance_score = 20
    else:
        maintenance_score = max(5, 35 - (open_issues * 0.4))

    # 4. Enterprise Documentation & Packaging Standards (Max 30 pts)
    has_desc = 10 if data.get("description") else 0
    has_license = 10 if data.get("license") else 0
    has_community_tools = 10 if has_wiki or data.get("has_pages", False) else 5
    docs_score = has_desc + has_license + has_community_tools

    # Total Sum Calculation (Capped mathematically between 0 and 100)
    total_score = round(complexity_score + maintenance_score + docs_score, 1)
    total_score = min(100.0, max(0.0, total_score))

    # Grade Map Threshold assignments
    if total_score >= 85: grade = "A+"
    elif total_score >= 70: grade = "A"
    elif total_score >= 55: grade = "B"
    elif total_score >= 40: grade = "C"
    else: grade = "D"
    
    return {
        "total_score": total_score,
        "grade": grade,
        "breakdown": {
            "Architecture Complexity": round(complexity_score, 1),
            "Maintenance Quality": round(maintenance_score, 1),
            "Production Documentation": round(docs_score, 1)
        }
    }
