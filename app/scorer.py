import math
from datetime import datetime

def calculate_advanced_gitscore(user_data: dict, repos_data: list) -> dict:
    """
    Complete GitScore 100-Point Engine.
    Evaluates 6 Core Categories, unlocks 9 Badges, and compiles custom insights.
    """
    # 1. Base Profiles
    public_repos = user_data.get("public_repos", 0)
    followers = user_data.get("followers", 0)
    following = user_data.get("following", 0)
    created_at_str = user_data.get("created_at", "")
    
    total_stars = sum(r.get("stargazers_count", 0) for r in repos_data)
    total_forks = sum(r.get("forks_count", 0) for r in repos_data)
    total_size = sum(r.get("size", 0) for r in repos_data)
    
    # Extract language metrics
    languages = {}
    for r in repos_data:
        lang = r.get("language")
        if lang:
            languages[lang] = languages.get(lang, 0) + 1

    # -------------------------------------------------------------
    # 📑 CATEGORY CALCULATIONS (MAX 100 POINTS)
    # -------------------------------------------------------------
    # C1: Repository Quality (Max 25)
    c1_base = min(5.0, public_repos * 0.5)
    c1_stars = min(12.0, math.log1p(total_stars) * 2.5)
    c1_forks = min(8.0, total_forks * 1.0)
    cat_quality = round(c1_base + c1_stars + c1_forks, 1)

    # C2: Activity & Consistency (Max 20)
    total_issues = sum(r.get("open_issues_count", 0) for r in repos_data)
    cat_activity = min(20.0, 6.0 + (public_repos * 0.4) + (total_issues * 0.2))

    # C3: Community Impact (Max 25)
    has_traction = 1.5 if any(r.get("stargazers_count", 0) > 2 for r in repos_data) else 1.0
    cat_community = min(25.0, (total_stars * 1.5 + total_forks * 2.0) * has_traction)
    if cat_community == 0 and public_repos > 0:
        cat_community = 5.0  # Baseline active repository credit

    # C4: Social Influence (Max 15)
    follower_log = min(10.0, math.log1p(followers) * 2.5)
    ratio = followers / max(1, following)
    ratio_bonus = min(5.0, ratio * 0.5)
    cat_social = round(follower_log + ratio_bonus, 1)

    # C5: Language Diversity using Shannon Entropy approach (Max 10)
    cat_lang = 3.0
    if languages:
        total_lang_repos = sum(languages.values())
        entropy = 0.0
        for count in languages.values():
            p = count / total_lang_repos
            entropy -= p * math.log(p)
        cat_lang = min(10.0, 3.0 + (entropy * 4.0))

    # C6: Account Longevity (Max 5)
    cat_age = 1.0
    account_years = 0
    if created_at_str:
        try:
            created_year = datetime.strptime(created_at_str[:10], "%Y-%m-%d").year
            account_years = max(0, datetime.now().year - created_year)
            cat_age = min(5.0, 1.0 + (account_years * 0.5))
        except Exception:
            pass

    # Compile Absolute Total
    total_score = round(cat_quality + cat_activity + cat_community + cat_social + cat_lang + cat_age, 1)
    total_score = min(100.0, max(0.0, total_score))

    # Tier Assignments
    if total_score >= 90: tier, color = "S+ Tier (Elite Grandmaster)", "#FFD700"
    elif total_score >= 80: tier, color = "S Tier (Master Architect)", "#FF4500"
    elif total_score >= 65: tier, color = "A Tier (Advanced Maintainer)", "#1E90FF"
    elif total_score >= 50: tier, color = "B Tier (Active Contributor)", "#32CD32"
    elif total_score >= 35: tier, color = "C Tier (Rising Developer)", "#BA55D3"
    elif total_score >= 20: tier, color = "D Tier (Novice Footprint)", "#FFA500"
    else: tier, color = "F Tier (Blank Canvas)", "#FF0000"

    # -------------------------------------------------------------
    # 🏅 UNLOCKABLE BADGES & PROGRESS TRACKING (9 FEATURES)
    # -------------------------------------------------------------
    badges = [
        {"name": "Polyglot Ninja", "unlocked": len(languages) >= 3, "desc": "Write code across 3+ distinct programming languages.", "progress": f"{len(languages)}/3 languages"},
        {"name": "Code Heavyweight", "unlocked": total_size > 10000, "desc": "Exceed 10MB of collective source repositories.", "progress": f"{round(total_size/1024, 1)}/10 MB"},
        {"name": "Community Pillar", "unlocked": total_stars > 0 or total_forks > 0, "desc": "Earn appreciation through third-party stars or forks.", "progress": f"{total_stars} stars, {total_forks} forks"},
        {"name": "Platform Veteran", "unlocked": account_years >= 3, "desc": "Maintain an active profile account for 3+ years.", "progress": f"{account_years}/3 years old"},
        {"name": "Networking Titan", "unlocked": followers >= 20, "desc": "Amass a professional network of 20+ followers.", "progress": f"{followers}/20 followers"},
        {"name": "Pristine Maintainer", "unlocked": total_issues == 0 and public_repos > 0, "desc": "Maintain zero open backlog bugs across workspaces.", "progress": f"{total_issues} open issues"},
        {"name": "SaaS Architect", "unlocked": public_repos >= 10, "desc": "Publish 10+ open-source infrastructure projects.", "progress": f"{public_repos}/10 repos"},
        {"name": "Bio Optimizer", "unlocked": bool(user_data.get("bio")), "desc": "Fill your bio string with engineering stack tags.", "progress": "Complete" if user_data.get("bio") else "Empty"},
        {"name": "Global Connector", "unlocked": bool(user_data.get("blog") or user_data.get("company")), "desc": "Link personal portfolios or production companies.", "progress": "Linked" if (user_data.get("blog") or user_data.get("company")) else "Missing Link"}
    ]

    # -------------------------------------------------------------
    # 💡 DETAILED AUDIT INSIGHTS (WHAT YOU DO GOOD & BAD)
    # -------------------------------------------------------------
    good_points = []
    bad_points = []

    # Evaluate Strengths
    if user_data.get("bio"): good_points.append("Your profile bio is highly optimized with data, tools, and clear domain focuses.")
    if len(languages) >= 3: good_points.append(f"Strong language diversity profile! You build code across {len(languages)} tech stacks.")
    if public_repos >= 10: good_points.append(f"Excellent scale! Your project portfolio footprint contains {public_repos} public repos.")
    if account_years >= 4: good_points.append(f"Account longevity is a big plus. Your profile has {account_years} years of authority.")
    if total_issues == 0 and public_repos > 0: good_points.append("Perfect issue maintenance! Your codebase registry has no unresolved open backlogs.")

    # Evaluate Weaknesses / Areas for Improvement
    if not user_data.get("blog"): bad_points.append("Missing Website Link: Your profile doesn't showcase an external portfolio URL or LinkedIn channel.")
    if total_stars == 0: bad_points.append("Low External Traction: Your projects have 0 stars. Pin high-value repositories or add clear README markdown documentation to attract traffic.")
    if followers < 15: bad_points.append("Network Horizon: Your follower count is growing. Engage with communities or collaborate on public pull requests to scale social influence points.")
    if total_size < 2000: bad_points.append("Light Footprint: The combined footprint size of your public repositories is low. Push complete source code files rather than basic scripts.")

    return {
        "total_score": total_score,
        "tier": tier,
        "color": color,
        "breakdown": {
            "Repository Quality": cat_quality,
            "Activity & Consistency": cat_activity,
            "Community Impact": cat_community,
            "Social Influence": cat_social,
            "Language Diversity": cat_lang,
            "Account Longevity": cat_age
        },
        "badges": badges,
        "good": good_points if good_points else ["Baseline metrics are establishing safely."],
        "bad": bad_points if bad_points else ["Phenomenal work! Your configuration layout contains zero glaring defects."]
    }
