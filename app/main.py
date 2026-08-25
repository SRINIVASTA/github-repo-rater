import streamlit as st
import requests
import pandas as pd
import re
import logging
from bs4 import BeautifulSoup
from scorer import calculate_user_rating

# Web layout configuration setup
st.set_page_config(page_title="GitHub User Auditor", page_icon="👤", layout="centered")

st.title("👤 GitHub User Profile Auditor")
st.write("Analyze and grade a developer's public GitHub footprint instantly from your browser.")

# --- Streamlit CSS Cleanup Layers ---
st.markdown(""" 
 <style> 
 header[data-testid="stHeader"] { visibility: hidden !important; display: none !important; } 
 div[data-testid="stToolbar"] { visibility: hidden !important; display: none !important; } 
 footer { visibility: hidden !important; } 
 [data-testid="stMainBlockContainer"] { padding-top: 1rem !important; }
 .main .block-container { padding-top: 1rem !important; }
 </style> 
 """, unsafe_allow_html=True) 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AUDITOR")

# Token Status Verification
has_token = "GITHUB_TOKEN" in st.secrets and st.secrets["GITHUB_TOKEN"].strip() != ""
if has_token:
    st.sidebar.success("🔒 GitHub Token Status: ACTIVE")
else:
    st.sidebar.info("💡 Running via Standard Public Optimization Channels")

user_input = st.text_input("GitHub Username", placeholder="e.g., srinivasta")

def render_ui_dashboard(profile_data, audit_results, engine_source="API"):
    """
    Unified dashboard layout rendering function to eliminate duplicated template markup blocks.
    """
    st.success(f"🎯 Audit Complete via {engine_source} for @{profile_data.get('login')}!")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        if profile_data.get("avatar_url"):
            st.image(profile_data.get("avatar_url"), width=150)
    with col2:
        st.subheader(profile_data.get("name") or profile_data.get("login"))
        st.caption(f"📍 Location: {profile_data.get('location') or 'Not Specified'}")
        st.write(profile_data.get("bio") or "*No profile bio provided.*")
    
    st.divider()
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric(label=f"Profile Grade Score ({engine_source})", value=f"{audit_results['total_score']} / 100")
    with c2:
        st.metric(label="Calculated Tier", value=audit_results['grade'])
    
    st.subheader("📊 Footprint Metric Distribution")
    chart_df = pd.DataFrame({
        "Evaluation Module": list(audit_results["breakdown"].keys()),
        "Score Segment": list(audit_results["breakdown"].values())
    })
    st.bar_chart(data=chart_df, x="Evaluation Module", y="Score Segment", use_container_width=True)
    
    st.subheader("💡 Optimization Recommendations")
    if not profile_data.get("bio"):
        st.error("❌ Missing Account Bio: Add a brief summary detailing your technical specialization stacks.")
    if not profile_data.get("blog"):
        st.warning("⚠️ Portfolio Link Missing: Connect a portfolio URL or LinkedIn page to your workspace profile.")
    if audit_results['total_score'] >= 75:
        st.info("🔥 Outstanding profile layout! This workspace projects clear authority, active maintenance, and solid personal branding.")
    else:
        st.info("📌 Tip: Increasing your public activity and filling out your profile fields will improve your score.")

# --- Processing Execution Core Loop ---
if st.button("Audit User Profile", type="primary"):
    if not user_input:
        st.warning("Please enter a username.")
    else:
        username = user_input.replace("https://github.com", "").strip("/").split("/")[0]
        api_url = f"https://github.com{username}"
        
        headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "Streamlit-User-Auditor-v1"}
        if has_token:
            headers["Authorization"] = f"Bearer {st.secrets['GITHUB_TOKEN'].strip()}"
            
        processed_successfully = False
        
        with st.spinner("Compiling developer profile data..."):
            try:
                # Execution Vector 1: Attempt standard API retrieval
                response = requests.get(api_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    user_data = response.json()
                    results = calculate_user_rating(user_data)
                    render_ui_dashboard(user_data, results, engine_source="API")
                    processed_successfully = True
                elif response.status_code == 404:
                    st.error("❌ The specified username does not match an active user account.")
                    processed_successfully = True
                else:
                    # Let the code cascade cleanly into web-scraping if rate limited (403)
                    logger.warning(f"GitHub API returned unexpected status code: {response.status_code}. Shifting to fallback.")
                    
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                logger.warning("API connection timed out. Redirecting context to scraping engine.")

        # Execution Vector 2: Dynamic Live Scraping Engine Fallback
        if not processed_successfully:
            st.info("🌐 API limit hit or timeout occurred. Parsing public markup profile structures dynamically...")
            try:
                scrape_url = f"https://github.com{username}"
                scrape_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                scrape_res = requests.get(scrape_url, headers=scrape_headers, timeout=10)
                
                if scrape_res.status_code == 200:
                    soup = BeautifulSoup(scrape_res.text, "html.parser")
                    
                    def parse_count(selector):
                        element = soup.select_one(selector)
                        if element:
                            val_text = element.text.strip().lower().replace(",", "")
                            if "k" in val_text:
                                return int(float(val_text.replace("k", "")) * 1000)
                            return int(re.sub(r"\D", "", val_text) or 0)
                        return 0

                    scraped_payload = {
                        "login": username,
                        "name": getattr(soup.select_one("span.p-name"), 'text', username.capitalize()).strip(),
                        "public_repos": parse_count("span.Counter[title]"),
                        "followers": parse_count("a[href*='tab=followers'] span.text-bold"),
                        "following": parse_count("a[href*='tab=following'] span.text-bold"),
                        "bio": getattr(soup.select_one("div.p-note"), 'text', "").strip() or None,
                        "blog": getattr(soup.select_one("li[itemprop='url'] a"), 'href', "").strip() or None,
                        "location": getattr(soup.select_one("li[itemprop='homeLocation'] span"), 'text', "").strip() or None,
                        "company": getattr(soup.select_one("li[itemprop='worksFor'] span"), 'text', "").strip() or None,
                        "avatar_url": getattr(soup.select_one("img.avatar-user"), 'src', None)
                    }
                    
                    results = calculate_user_rating(scraped_payload)
                    render_ui_dashboard(scraped_payload, results, engine_source="Live Web Scraping")
                    processed_successfully = True
            except Exception as e:
                logger.error(f"Live parsing engine failed: {str(e)}")

        # Execution Vector 3: Emergency Interactive User Input Form
        if not processed_successfully:
            st.warning("⚠️ Web-scraping was protected by anti-bot challenge vectors. Please verify your footprint parameters manually:")
            with st.form("emergency_manual_form"):
                f_name = st.text_input("Name", value=username.capitalize())
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    f_repos = st.number_input("Public Repositories Count", min_value=0, value=5)
                    f_followers = st.number_input("Followers Count", min_value=0, value=0)
                with col_m2:
                    f_following = st.number_input("Following Count", min_value=0, value=0)
                    f_loc = st.text_input("Location String", placeholder="e.g., Visakhapatnam, India")
                f_bio = st.text_area("Profile Bio Text")
                f_blog = st.text_input("Website URL Link")
                
                if st.form_submit_button("Calculate Interactive Grade"):
                    manual_payload = {
                        "login": username, "name": f_name, "public_repos": f_repos,
                        "followers": f_followers, "following": f_following,
                        "bio": f_bio if f_bio.strip() != "" else None,
                        "blog": f_blog if f_blog.strip() != "" else None,
                        "location": f_loc if f_loc.strip() != "" else None,
                        "avatar_url": "https://github.comidenticons/git.png"
                    }
                    results = calculate_user_rating(manual_payload)
                    render_ui_dashboard(manual_payload, results, engine_source="Manual Override Input")
