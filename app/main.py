import streamlit as st
import requests
import pandas as pd
import logging
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


# --- 2. 🧪 USER INTERACTIVE MODE TOGGLE (CHECKBOX TICK) ---
st.sidebar.markdown("### ⚙️ Application Mode")

# The user gives the tick manually here!
simulation_mode = st.sidebar.checkbox("🎯 Force Perfect Mock Simulation Profile")

if simulation_mode:
    st.sidebar.success("⚡ Mock Profile Mode Active (Bypassing Network Firewall)")
else:
    st.sidebar.info("🌐 Live API Mode Active")


# --- 3. 🔑 AUTOMATED ACCESS VERIFICATION CHECK ---
has_token = "GITHUB_TOKEN" in st.secrets and st.secrets["GITHUB_TOKEN"].strip() != ""

if has_token and not simulation_mode:
    st.sidebar.success("🔒 GitHub Token Status: ACTIVE (5,000 req/hr)")
elif not simulation_mode:
    st.sidebar.warning("💡 Running unauthenticated (60 req/hr Shared Limit)")


# --- 4. PROFILE AUDITOR LOGIC ---
# User input text forms - accepts clean username strings or full links
user_input = st.text_input("GitHub Username", placeholder="e.g., torvalds")

if st.button("Audit User Profile", type="primary"):
    if not user_input:
        st.warning("Please enter a username.")
    else:
        # Extract username cleanly even if the user pastes a full URL link string
        parsed_input = user_input.replace("https://github.com", "").strip("/").split("/")
        username = parsed_input if parsed_input else user_input.strip()
        
        # --- IF THE USER TICKS THE BOX: INJECT 100% PERFECT MOCK DATA IMMEDIATELY ---
        if simulation_mode:
            st.toast("Simulating an elite workspace evaluation sequence...", icon="🚀")
            
            # Constructing a perfect 100/100 profile payload locally
            user_data = {
                "login": username,
                "name": f"{username.capitalize()} (Simulation)",
                "avatar_url": "https://unsplash.com",
                "location": "Silicon Valley, CA",
                "bio": "Principal Open Source Architect | Specialized Framework Contributor | Systems Engineer",
                "blog": "https://portfolio-showcase.dev",
                "email": "contact@developer-profile.io",
                "company": "Enterprise Labs Inc.",
                "public_repos": 40,   # 40 * 1.5 = 60 pts -> Caps at 35 pts max
                "followers": 100,    # 100 followers -> Caps at 35 pts max
                "following": 2       # Small ratio multiplier boundary check
            }
            
            # Run the scoring calculation function locally
            results = calculate_user_rating(user_data)
            
            # Update values manually to match whatever absolute layout display you want
            results["total_score"] = 100.0
            results["grade"] = "A+"
            results["breakdown"] = {
                "Codebase Portfolio Scale": 35.0,
                "Network Influence Index": 35.0,
                "Profile Optimization": 30.0
            }
            
            # Use status code 200 simulation to trigger the visualization tree perfectly
            status_code = 200
            
        # --- IF THE USER LEAVES IT UNTICKED: TRY LIVE LIVE WEB API CALL ---
        else:
            api_url = f"https://github.com{username}"
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            if has_token:
                headers["Authorization"] = f"Bearer {st.secrets['GITHUB_TOKEN'].strip()}"
                
            with st.spinner(f"Fetching real-time data for @{username}..."):
                try:
                    response = requests.get(api_url, headers=headers, timeout=10)
                    status_code = response.status_code
                    if status_code == 200:
                        user_data = response.json()
                        results = calculate_user_rating(user_data)
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                    status_code = "CONNECTION_FAIL"
                    logger.error(f"API Connection Exception: {str(e)}")

        # --- 5. RENDER THE INTERFACE VISUALIZATIONS ---
        if status_code == 200:
            st.success(f"🎯 Audit Complete for @{user_data.get('login')}!")
            
            col1, col2 = st.columns([1, 3])
            with col1:
                if user_data.get("avatar_url"):
                    st.image(user_data.get("avatar_url"), width=150)
            with col2:
                st.subheader(user_data.get("name") or username)
                st.caption(f"📍 Location: {user_data.get('location') or 'Not Specified'}")
                st.write(user_data.get("bio") or "*No profile bio provided.*")
            
            st.divider()
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric(label="Profile Grade Score", value=f"{results['total_score']} / 100")
            with c2:
                st.metric(label="Calculated Tier", value=f"Grade {results['grade']}")
            
            st.subheader("📊 Footprint Metric Distribution")
            chart_df = pd.DataFrame({
                "Evaluation Module": list(results["breakdown"].keys()),
                "Score Segment": list(results["breakdown"].values())
              })
            st.bar_chart(data=chart_df, x="Evaluation Module", y="Score Segment", use_container_width=True)
            
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

        elif status_code == "CONNECTION_FAIL":
            st.error("🌐 Connection Failure: Unable to reach the GitHub API endpoints.")
            st.info("Please verify your internet connection or check the sidebar to tick the simulation profile mode layer.")
        else:
            st.error(f"❌ GitHub API Return Code: {status_code}")
            if status_code == 404:
                st.info("💡 The specified username does not match an active user account. Please check your spelling.")
