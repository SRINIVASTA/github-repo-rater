import streamlit as st
import requests
import pandas as pd
from scorer import calculate_user_rating

# Web layout configuration setup
st.set_page_config(page_title="GitHub User Auditor", page_icon="👤", layout="centered")

# --- UI Styling Hacks ---
st.markdown(""" 
 <style> 
 header[data-testid="stHeader"] { visibility: hidden !important; } 
 footer { visibility: hidden !important; } 
 [data-testid="stMainBlockContainer"] { padding-top: 1rem !important; }
 </style> 
 """, unsafe_allow_html=True) 

# --- API Configuration ---
if "GITHUB_TOKEN" in st.secrets and st.secrets["GITHUB_TOKEN"].strip() != "":
    st.success("🔒 GitHub Token Status: ACTIVE")
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {st.secrets['GITHUB_TOKEN'].strip()}"
    }
else:
    st.info("💡 Running via Public API (Rate Limited)")
    headers = {"Accept": "application/vnd.github.v3+json"}

st.title("👤 GitHub User Profile Auditor")

# Instant input processor
user_input = st.text_input("GitHub Username", value="SRINIVASTA")

if user_input:
    username = user_input.replace("https://github.com/", "").strip("/").split("/")[0]
    user_url = f"https://github.com{username}"
    repos_url = f"https://github.com{username}/repos?per_page=100"
    
    with st.spinner("Analyzing repository metrics..."):
        try:
            response = requests.get(user_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Fetch target repos metrics
                repos_resp = requests.get(repos_url, headers=headers, timeout=10)
                repos_data = repos_resp.json() if repos_resp.status_code == 200 else []
                
                # Compute integrated rating matrix vectors
                results = calculate_user_rating(user_data, repos_data)
                
                st.markdown(f"### 🎯 Audit Complete for @{user_data.get('login')}!")
                
                # Layout results
                col1, col2 = st.columns([1, 2])
                with col1:
                    if user_data.get("avatar_url"): st.image(user_data.get("avatar_url"), width=130)
                with col2:
                    st.subheader(user_data.get("name") or username)
                    st.write(user_data.get("bio") or "*No bio provided.*")
                
                st.divider()
                
                # Render calculated scores
                c1, c2 = st.columns(2)
                with c1: st.metric(label="Profile Grade Score", value=f"{results['total_score']} / 100")
                with c2: st.metric(label="Calculated Tier", value=results['grade'])
                
                # --- HORIZONTAL METRIC MATRIX DISTRIBUTION CHART ---
                st.subheader("📊 Footprint Metric Distribution")
                chart_df = pd.DataFrame({
                    "Score Segment": list(results["breakdown"].keys()),
                    "Score": list(results["breakdown"].values())
                })
                st.bar_chart(data=chart_df, x="Score", y="Score Segment", horizontal=True, use_container_width=True)
                
            else:
                st.error(f"❌ GitHub API Error: {response.status_code}")
                
        except Exception as e:
            st.error("Connection error. Please check credentials or API limits.")

