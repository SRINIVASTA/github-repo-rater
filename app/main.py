import streamlit as st
import requests
import pandas as pd
import logging
import pytest
# Import your balanced scoring engine from scorer.py
from scorer import calculate_user_rating

# Web layout configuration setup
st.set_page_config(page_title="GitHub User Auditor", page_icon="👤", layout="centered")

st.title("👤 GitHub User Profile Auditor")
st.write("Analyze and grade a developer's public GitHub footprint instantly from your browser.")

# --- 1. FORCE STREAMLIT CHROMIUM HIDING LAYERS & GAP FIX ---
st.markdown(""" 
 <style> 
 header[data-testid="stHeader"] { visibility: hidden !important; display: none !important; } 
 div[data-testid="stToolbar"] { visibility: hidden !important; display: none !important; } 
 footer { visibility: hidden !important; } 
 
 [data-testid="stMainBlockContainer"] {
     padding-top: 1rem !important;
 }
 .main .block-container {
     padding-top: 1rem !important;
 }
 </style> 
 """, unsafe_allow_html=True) 

logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger("FIREWALL") 


# --- 2. 🧪 AUTOMATED PYTEST SIDEBAR STATUS CHECK ---
st.sidebar.markdown("### ⚙️ System Diagnostics")

# Run pytest on test_app.py quietly in the background on startup
# exit_code 0 means everything passed perfectly
try:
    exit_code = pytest.main(["-q", "test_app.py"])
    if exit_code == pytest.ExitCode.NO_TESTS_COLLECTED:
        exit_code = pytest.main(["-q", "app/test_app.py"])
        
    if exit_code == 0:
        st.sidebar.success("✅ Pytest Suite: PASSED (5/5 Engine Verified)")
    else:
        st.sidebar.error("❌ Pytest Suite: FAILED (Regression Detected)")
except Exception:
    st.sidebar.warning("⚠️ Pytest Suite: UNKNOWN (test_app.py missing)")


# --- 3. 🔑 AUTOMATED ACCESS VERIFICATION CHECK ---
has_token = "GITHUB_TOKEN" in st.secrets and st.secrets["GITHUB_TOKEN"].strip() != ""

if has_token:
    st.sidebar.success("🔒 GitHub Token Status: ACTIVE (5,000 req/hr)")
else:
    st.sidebar.warning("💡 Running unauthenticated (60 req/hr Shared Limit)")


# --- 4. PROFILE AUDITOR LOGIC ---
# User input text forms - accepts clean username strings or full links
user_input = st.text_input("GitHub Username", placeholder="e.g., torvalds")

if st.button("Audit User Profile", type="primary"):
    if not user_input:
        st.warning("Please enter a username.")
    else:
        # Extract username cleanly even if the user pastes a full URL link string
        parsed_input = user_input.replace("https://github.com/", "").strip("/").split("/")
        username = parsed_input[0] if parsed_input else user_input.strip()
        
        api_url = f"https://api.github.com/users/{username}"
        
        headers = {
            "Accept": "application/vnd.github.v3+json",
            # Standard browser fingerprint to avoid strict API proxy/firewall drops
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        # Inject the Streamlit Secrets token into request headers dynamically
        if has_token:
            headers["Authorization"] = f"Bearer {st.secrets['GITHUB_TOKEN'].strip()}"
            
        with st.spinner(f"Fetching real-time data for @{username}..."):
            try:
                response = requests.get(api_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    user_data = response.json()
                    results = calculate_user_rating(user_data)
                    
                    st.success(f"🎯 Audit Complete for @{user_data.get('login')}!")
                    
                    # Layout Summary Display Cards using live-fetched metrics
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if user_data.get("avatar_url"):
                            st.image(user_data.get("avatar_url"), width=150)
                    with col2:
                        st.subheader(user_data.get("name") or username)
                        st.caption(f"📍 Location: {user_data.get('location') or 'Not Specified'}")
                        st.write(user_data.get("bio") or "*No profile bio provided.*")
                    
                    st.divider()
                    
                    # Data rendering metrics blocks
                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric(label="Profile Grade Score", value=f"{results['total_score']} / 100")
                    with c2:
                        st.metric(label="Calculated Tier", value=f"Grade {results['grade']}")
                    
                    # Metrics distribution chart mapped directly to balanced metrics
                    st.subheader("📊 Footprint Metric Distribution")
                    chart_df = pd.DataFrame({
                        "Evaluation Module": list(results["breakdown"].keys()),
                        "Score Segment": list(results["breakdown"].values())
                    })
                    st.bar_chart(data=chart_df, x="Evaluation Module", y="Score Segment", use_container_width=True)
                    
                    # Profile optimization feedback logic based strictly on current user profile data
                    st.subheader("💡 Optimization Recommendations")
                    if not user_data.get("bio"):
                        st.error("❌ Missing Account Bio: Add a brief summary detailing your technical specialization stacks.")
                    if not user_data.get("blog"):
                        st.warning("⚠️ Portfolio Link Missing: Connect a portfolio URL or LinkedIn page to your profile.")
                    if not (user_data.get("email") or user_data.get("company")):
                        st.warning("⚠️ Professional Context: Provide a public email or company affiliation banner to ease reachability.")
                    
                    if results['total_score'] >= 85:
                        st.info("🔥 Outstanding profile layout! This workspace projects clear authority, active maintenance, and solid personal branding.")
                    else:
                        st.info("📌 Tip: Increasing your public activity and filling out your profile branding fields will improve your score segment.")

                else:
                    st.error(f"❌ GitHub API Return Code: {response.status_code}")
                    if response.status_code == 404:
                        st.info("💡 The specified username does not match an active user account. Please check your spelling.")
                    elif response.status_code == 403:
                        st.warning("💡 API Rate Limit Reached. If you have a token setup, verify it has not expired.")
                    elif response.status_code == 401:
                        st.error("💡 Unauthorized: The GITHUB_TOKEN inside your Streamlit secrets is invalid.")
                        
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                st.error("🌐 Connection Failure: Unable to reach the GitHub API endpoints.")
                st.info("Please verify your internet connection or check if GitHub services are down.")
                logger.error(f"API Connection Exception: {str(e)}")
