import streamlit as st
import requests
import pandas as pd
from scorer import calculate_advanced_gitscore

st.set_page_config(page_title="GitScore Core Engine", page_icon="🔢", layout="centered")

st.title("🔢 GitScore Profile Auditor & Analyzer")
st.write("Comprehensive metrics evaluation engine based on official performance parameters.")

# Token Status Indicator Sidebar
if "GITHUB_TOKEN" in st.secrets and st.secrets["GITHUB_TOKEN"].strip() != "":
    st.sidebar.success("🔒 GitHub Authentication: ACTIVE")
else:
    st.sidebar.warning("⚠️ Running via Anonymous Mode (No Token Loaded)")

user_input = st.text_input("GitHub Username", placeholder="e.g., srinivasta")

if st.button("Analyze Profile Metrics", type="primary"):
    if not user_input:
        st.warning("Please enter a username.")
    else:
        # Standardize username input string
        username = user_input.replace("https://github.com", "").strip("/").split("/")[-1]
        
        api_url = f"https://github.com{username}"
        repos_url = f"https://github.com{username}/repos?per_page=100"
        
        headers = {
            "Accept": "application/vnd.github.v3+json", 
            "User-Agent": "GitScore-Enterprise-v5"
        }
        if "GITHUB_TOKEN" in st.secrets and st.secrets["GITHUB_TOKEN"].strip() != "":
            headers["Authorization"] = f"Bearer {st.secrets['GITHUB_TOKEN'].strip()}"
            
        with st.spinner(f"Requesting data streams for @{username}..."):
            response = requests.get(api_url, headers=headers, timeout=10)
            repos_response = requests.get(repos_url, headers=headers, timeout=10)
            
            # --- STATUS CHECK CHANNELS ---
            if response.status_code == 200:
                user_data = response.json()
                repos_data = repos_response.json() if repos_response.status_code == 200 else []
                
                # Execute Advanced Scoring Formula Matrix
                results = calculate_advanced_gitscore(user_data, repos_data)
                
                st.success(f"🎯 Audit Complete for @{user_data.get('login')}!")
                
                # Big Tier Header Card Display
                st.markdown(
                    f"<div style='background-color:{results['color']}22; border-radius:10px; padding:20px; border:2px solid {results['color']}; text-align:center;'> "
                    f"<h1 style='color:{results['color']}; margin:0;'>{results['total_score']} / 100</h1>"
                    f"<h3 style='margin:10px 0 0 0; color:#333;'>{results['tier']}</h3>"
                    f"</div>", 
                    unsafe_allow_html=True
                )
                
                # Display Developer Basics Layout
                st.markdown(f"### 👤 {user_data.get('name') or user_data.get('login')}")
                st.write(f"📝 **Bio:** {user_data.get('bio') or '*None provided*'}")
                
                # Good VS Bad Audit Matrix
                st.subheader("💡 Strategic Profile Performance Breakdown")
                col_good, col_bad = st.columns(2)
                with col_good:
                    st.markdown("#### ✅ What You Are Good At")
                    for item in results["good"]:
                        st.markdown(f"- {item}")
                with col_bad:
                    st.markdown("#### ⚠️ Where You Can Improve")
                    for item in results["bad"]:
                        st.markdown(f"- {item}")

                # Technology Stack Bar
                st.subheader("🛠️ Core Technology Footprint Matrix")
                langs = {}
                for r in repos_data:
                    l = r.get("language")
                    if l: langs[l] = langs.get(l, 0) + 1
                if langs:
                    lang_df = pd.DataFrame(list(langs.items()), columns=["Language", "Repository Count"])
                    st.bar_chart(lang_df, x="Language", y="Repository Count", use_container_width=True)
                else:
                    st.info("No explicit languages declared in public repositories.")

                # Achievements System
                st.subheader("🏅 Unlockable Profile Achievements")
                b_col1, b_col2 = st.columns(2)
                for idx, b in enumerate(results["badges"]):
                    target_col = b_col1 if idx % 2 == 0 else b_col2
                    with target_col:
                        icon = "⭐" if b["unlocked"] else "🔒"
                        status_text = "**[UNLOCKED]**" if b["unlocked"] else "*[LOCKED]*"
                        st.markdown(f"**{icon} {b['name']}** {status_text}")
                        st.caption(f"{b['desc']} *(Status: {b['progress']})*")
                        st.divider()

            # --- DETAILED ERROR MESSAGES INSTEAD OF FALLBACKS ---
            elif response.status_code == 401:
                st.error("❌ Authentication Failed (Error 401)")
                st.info("Your `GITHUB_TOKEN` is invalid or has expired. Please create a new token on GitHub and update your Streamlit Secrets.")
            elif response.status_code == 403:
                st.error("🚫 Access Denied / Rate Limit Hit (Error 403)")
                st.info("Your token lacks permission scopes. Go to GitHub developer settings, edit your token, check the **public_repo** box, and click Save.")
            elif response.status_code == 404:
                st.error(f"🔍 User Not Found (Error 404)")
                st.info(f"The GitHub username `{username}` does not exist. Check your spelling and try again.")
            else:
                st.error(f"🌐 Infrastructure Connection Drop (Error {response.status_code})")
                st.info("Streamlit servers cannot reach GitHub's server nodes right now. Try again in a few seconds.")
