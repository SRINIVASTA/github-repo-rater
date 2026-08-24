import streamlit as st
import requests
import pandas as pd
from scorer import calculate_advanced_gitscore

st.set_page_config(page_title="GitScore Ultimate Platform", page_icon="🔢", layout="wide")

st.title("🔢 GitScore Profile Auditor & Analyzer")
st.write("Comprehensive metrics evaluation engine based on official performance parameters.")

# Tab configuration maps
tab1, tab2, tab3 = st.tabs(["📊 Profile Auditor", "⚔️ Head-to-Head Comparison", "🔥 AI Roast & Wrapped"])

# Setup authorization channels
headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "GitScore-Ultimate-App"}
if "GITHUB_TOKEN" in st.secrets and st.secrets["GITHUB_TOKEN"].strip() != "":
    st.sidebar.success("🔒 GitHub Authentication: ACTIVE")
    headers["Authorization"] = f"Bearer {st.secrets['GITHUB_TOKEN'].strip()}"
else:
    st.sidebar.warning("⚠️ Running via Anonymous Mode")

# ==========================================
# TAB 1: CORE PROFILE AUDITOR & BADGES
# ==========================================
with tab1:
    user_input = st.text_input("Enter GitHub Username to Audit", key="single_audit", placeholder="e.g., srinivasta")
    
    if st.button("Run Live Audit", type="primary"):
        if user_input:
            username = user_input.replace("https://github.com/", "").strip("/").split("/")[-1]
            
            with st.spinner(f"Requesting data streams for @{username}..."):
                res = requests.get(f"https://github.com{username}", headers=headers)
                rep_res = requests.get(f"https://github.com{username}/repos?per_page=100", headers=headers)
                
                if res.status_code == 200:
                    user_data = res.json()
                    repos_data = rep_res.json() if rep_res.status_code == 200 else []
                    results = calculate_advanced_gitscore(user_data, repos_data)
                    
                    st.success(f"🎯 Audit Complete for @{user_data.get('login')}!")
                    
                    # Highlight grade banner
                    st.markdown(
                        f"<div style='background-color:{results['color']}22; border-radius:10px; padding:20px; border:2px solid {results['color']}; text-align:center;'> "
                        f"<h1 style='color:{results['color']}; margin:0;'>{results['total_score']} / 100</h1>"
                        f"<h3 style='margin:10px 0 0 0; color:#333;'>{results['tier']}</h3>"
                        f"</div>", unsafe_allow_html=True
                    )
                    
                    st.markdown(f"### 👤 {user_data.get('name') or user_data.get('login')}")
                    st.write(f"📝 **Bio:** {user_data.get('bio') or '*No bio summary provided.*'}")
                    
                    # Performance breakdown tables
                    st.subheader("💡 Strategic Profile Performance Breakdown")
                    col_good, col_bad = st.columns(2)
                    with col_good:
                        st.markdown("#### ✅ What You Are Good At")
                        for item in results["good"]: st.markdown(f"- {item}")
                    with col_bad:
                        st.markdown("#### ⚠️ Where You Can Improve")
                        for item in results["bad"]: st.markdown(f"- {item}")
                    
                    # Fixed Layout: Metric weights allocation chart
                    st.subheader("📊 Category Weights Chart")
                    chart_df = pd.DataFrame(
                        list(results["breakdown"].items()), 
                        columns=["Evaluation Category", "Points Awarded"]
                    )
                    st.bar_chart(data=chart_df, x="Evaluation Category", y="Points Awarded", use_container_width=True)
                    
                    # Badges and progress layouts
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
                else:
                    st.error(f"❌ User Lookup Failed (Code {res.status_code}). Check spelling or token configuration settings.")

# ==========================================
# TAB 2: HEAD-TO-HEAD COMPARISON
# ==========================================
with tab2:
    st.subheader("⚔️ Head-to-Head Comparison Battle Arena")
    comp_col1, comp_col2 = st.columns(2)
    with comp_col1:
        user1 = st.text_input("First Developer Profile Username", placeholder="User A")
    with comp_col2:
        user2 = st.text_input("Second Developer Profile Username", placeholder="User B")
        
    if st.button("Run Comparison Simulation"):
        if user1 and user2:
            res1 = requests.get(f"https://github.com{user1}", headers=headers).json()
            res2 = requests.get(f"https://github.com{user2}", headers=headers).json()
            
            if "login" in res1 and "login" in res2:
                st.markdown("### 🏆 Comparison Winner Metrics Grid")
                c_block1, c_block2, c_block3 = st.columns(3)
                with c_block1:
                    st.metric(f"@{user1} Repos", f"{res1.get('public_repos')} repos")
                with c_block2:
                    st.metric(f"@{user2} Repos", f"{res2.get('public_repos')} repos")
                with c_block3:
                    winner = user1 if res1.get('followers', 0) > res2.get('followers', 0) else user2
                    st.success(f"🔥 Crown Leader: @{winner}")
            else:
                st.error("Could not compile search matrix paths.")

# ==========================================
# TAB 3: ROAST & ANNUAL WRAPPED
# ==========================================
with tab3:
    st.subheader("🔥 AI Roast Mode & Year-End Wrapped Dashboard")
    roast_target = st.text_input("Target Account to Roast/Wrap", placeholder="e.g., srinivasta")
    
    if st.button("Generate Roast & Story Card"):
        if roast_target:
            res = requests.get(f"https://github.com{roast_target}", headers=headers).json()
            if "login" in res:
                st.markdown("#### 💀 Profile Roast Script Engine")
                st.error(
                    f"Dear @{res.get('login')}: Your profile says you are working on advanced architectures, "
                    f"yet your public repository metrics show a different story. "
                    f"You spend all this time setting up token layouts but haven't pinned your best code. "
                    f"Add crisp Markdown documentation before you launch your next audit! 😂"
                )
                
                st.markdown("#### 🎁 Your Annual Code Wrapped Story Card")
                st.info(
                    f"✨ Active account footprint since year {res.get('created_at')[:4]}.\n"
                    f"📦 Your workspace contains a total portfolio size of {res.get('public_repos')} active public repos."
                )
                st.download_button("📥 Download Wrapped Profile SVG Badge", data=f"<svg height='100' width='300'><text y='20'>@{res.get('login')} GitScore Certified</text></svg>", file_name="gitscore-badge.svg", mime="image/svg+xml")
