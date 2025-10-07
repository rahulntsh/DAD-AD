# app.py
import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta

st.set_page_config(page_title="AdEase — Self-Serve Campaign Tool", layout="centered")

# ---------- Helper functions ----------
def estimate_reach_and_cpm(budget, business_type, creative_type):
    """
    Simple heuristic estimates.
    Returns (min_reach, max_reach, est_cpm)
    """
    base_cpm = {
        "Default": 60,
        "Retail / Store": 55,
        "Restaurant / Cafe": 50,
        "Salon / Wellness": 58,
        "Education / Coaching": 65,
        "E-commerce": 62,
        "Services (local)": 59,
    }
    base = base_cpm.get(business_type, base_cpm["Default"])
    # creative type influences CPM slightly
    creative_factor = {"Text": 0.98, "Image": 1.0, "Short Video": 1.15}
    cpm = base * creative_factor.get(creative_type, 1.0)
    # reach estimation: budget (₹) / cpm * 1000, add some variability
    reach = budget / cpm * 1000
    min_reach = int(reach * 0.8)
    max_reach = int(reach * 1.2)
    return min_reach, max_reach, round(cpm, 2)

def generate_mock_metrics(days=14, base_impressions=5000):
    dates = [datetime.today() - timedelta(days=i) for i in reversed(range(days))]
    impressions = np.maximum(100, (np.random.normal(loc=base_impressions, scale=base_impressions*0.15, size=days)).astype(int))
    ctr = np.clip(np.random.normal(loc=0.02, scale=0.005, size=days), 0.005, 0.1)  # 0.5% - 10%
    clicks = (impressions * ctr).astype(int)
    spend = (impressions / 1000) * np.random.normal(loc=60, scale=5, size=days)
    df = pd.DataFrame({
        "date": [d.strftime("%Y-%m-%d") for d in dates],
        "impressions": impressions,
        "clicks": clicks,
        "ctr": (ctr * 100).round(2),
        "spend": spend.round(2)
    })
    df["cpm"] = ((df["spend"] / df["impressions"]) * 1000).round(2)
    return df

def small_note(text):
    st.markdown(f"<small style='color: #6c757d'>{text}</small>", unsafe_allow_html=True)

# ---------- UI ----------
st.title("AdEase — Launch a Campaign in 3 steps")
small_note("Simple. Transparent. Localized for Indian SMBs. No jargon.")

# --- Top: Campaign hierarchy visualization (simple)
with st.expander("Campaign Structure (info) — Ads → Ad Sets → Campaigns", expanded=True):
    st.write("Campaigns group ad sets that share a common goal. Each ad set can contain multiple ads (creative variants). This tool abstracts that structure into an easy flow.")

st.divider()

# ---------- Step 1: Goal & Basic Onboarding ----------
st.header("Step 1 — What is your goal?")
goal = st.selectbox("Choose a campaign goal", ["Increase Visits", "Get Leads", "Boost Awareness"])
st.write("Why this matters:", {
    "Increase Visits": "Drive people to your website or store page.",
    "Get Leads": "Collect phone numbers / enquiries.",
    "Boost Awareness": "Increase brand visibility in your area."
}[goal])

st.divider()

# ---------- Step 2: Business Profiling ----------
st.header("Step 2 — Tell us about your business")
col1, col2 = st.columns([2,1])
with col1:
    business_name = st.text_input("Business name (optional)", placeholder="e.g., Shyam's Cafe")
    business_type = st.selectbox("Business type", ["Retail / Store", "Restaurant / Cafe", "Salon / Wellness",
                                                  "Education / Coaching", "E-commerce", "Services (local)", "Other"])
    location = st.text_input("City / Locality", placeholder="e.g., Pune")
with col2:
    st.markdown("**Smart Targeting**")
    st.success("Smart targeting enabled based on business type and location.")
    small_note("We handle audience selection using preset psychographic templates tuned for your business type.")

st.divider()

# ---------- Step 3: Creative Type + Budget ----------
st.header("Step 3 — Creative & Budget")
creative_type = st.radio("Choose creative type", ["Text", "Image", "Short Video"], horizontal=True)
budget = st.slider("Set your campaign budget (₹)", 1000, 50000, 5000, step=500)
duration_days = st.selectbox("Campaign duration (days)", [7, 14, 30], index=0)
st.write("Estimated campaign duration:", f"{duration_days} days")

# Estimated reach & CPM
min_reach, max_reach, est_cpm = estimate_reach_and_cpm(budget, business_type, creative_type)
st.info(f"Potential Reach: **~{min_reach} – {max_reach} people**")
st.metric("Estimated CPM (₹)", f"{est_cpm}")
small_note("Reach is estimated using market benchmarks and creative type. This is a preview for planning.")

st.divider()

# ---------- Campaign Preview and Confirm ----------
st.header("Preview & Launch")
st.subheader("Sample Ad Preview")
with st.container():
    st.markdown(f"**{business_name or 'Your Business'}** — {business_type} • {location or 'Your City'}")
    st.markdown(f"*Goal:* **{goal}**  •  *Creative type:* **{creative_type}**")
    st.write("---")
    # AI-like copy generation using template (no external API)
    if st.button("Generate suggested headline & caption"):
        # Use ChatGPT if you wish offline; here mock text
        suggested_headline = f"{business_name or 'Local Business'} — Special Offer"
        suggested_caption = f"Discover great deals at {business_name or 'your nearby store'}. Visit us today!"
        st.success("Suggested creative generated")
        st.markdown(f"**Headline:** {suggested_headline}")
        st.markdown(f"**Caption:** {suggested_caption}")
    else:
        st.markdown("_Click the button to generate a suggested headline and caption._")

st.write("") 
if st.button("Confirm & Create Campaign"):
    st.success("Campaign created (simulation).")
    st.balloons()
    # store minimal campaign metadata in session state
    if "campaigns" not in st.session_state:
        st.session_state["campaigns"] = []
    st.session_state["campaigns"].append({
        "name": business_name or "Sample Campaign",
        "type": business_type,
        "location": location,
        "goal": goal,
        "creative": creative_type,
        "budget": budget,
        "duration": duration_days,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    time.sleep(0.4)

st.divider()

# ---------- Dashboard (mock metrics) ----------
st.header("Dashboard — Campaign Performance (mock data)")
if "campaigns" not in st.session_state or len(st.session_state["campaigns"]) == 0:
    st.info("No campaigns yet. Create one above to see a dashboard simulation.")
else:
    # Pick last campaign
    camp = st.session_state["campaigns"][-1]
    st.subheader(camp["name"])
    st.markdown(f"**Goal:** {camp['goal']}  •  **Budget:** ₹{camp['budget']}  •  **Duration:** {camp['duration']} days")
    st.write(f"**Smart Targeting used:** Yes — {camp['type']} in {camp['location']}")
    small_note("Attribution and cross-channel metrics are advanced features planned in later phases.")
    # Generate mock metrics
    df = generate_mock_metrics(days=camp['duration'], base_impressions=int((camp['budget']/est_cpm)*1000))
    latest = df.iloc[-1]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("People reached", f"{int(df['impressions'].sum())}", delta=f"{int(df['impressions'].pct_change().iloc[-1]*100) if len(df)>1 else 0}%")
    col2.metric("Clicks", f"{int(df['clicks'].sum())}", delta=f"{int(df['clicks'].pct_change().iloc[-1]*100) if len(df)>1 else 0}%")
    col3.metric("Avg Click Rate", f"{round(df['ctr'].mean(),2)}%")
    col4.metric("Spend", f"₹{round(df['spend'].sum(),2)}")
    st.line_chart(df.set_index("date")[["impressions","clicks"]])
    st.bar_chart(df.set_index("date")[["ctr","cpm"]])

    # Estimated CPM reiterated
    st.write(f"**Estimated CPM (preview):** ₹{est_cpm}")
    small_note("CPM is a predicted value. Real CPM varies by channel and placement.")

st.divider()

# ---------- Micro-feedback (critical) ----------
st.header("Quick Feedback — help us improve")
with st.form("feedback_form"):
    rating = st.radio("How easy was it to create your campaign?", ["Very easy", "Somewhat easy", "Neutral", "Difficult"], horizontal=True)
    comment = st.text_area("If you have one suggestion, what is it?", placeholder="e.g., 'Make targeting simpler' or 'Add more creative templates'")
    submit_feedback = st.form_submit_button("Send feedback")
    if submit_feedback:
        # store feedback in session state
        if "feedback" not in st.session_state:
            st.session_state["feedback"] = []
        st.session_state["feedback"].append({"rating": rating, "comment": comment, "ts": datetime.now().isoformat()})
        st.success("Thanks — feedback recorded.")

if "feedback" in st.session_state and len(st.session_state["feedback"])>0:
    st.markdown("**Recent feedback (sample):**")
    for f in st.session_state["feedback"][-3:]:
        st.write(f"- {f['rating']} — {f['comment'][:120]}")

st.divider()

# ---------- Roadmap / Notes (A/B testing, Attribution, Privacy) ----------
st.header("Roadmap & Operational notes")
st.markdown("""
- **A/B Testing (Phase 2)**: Compare creatives by age/gender/region.  
- **Attribution**: Integrate MMPs (Branch / Appsflyer) for multi-channel conversion attribution.  
- **Privacy**: Tool emphasizes privacy-safe, in-app engagement tracking (no reliance on third-party pixels by default).  
""")
st.info("These are roadmap items. We show them to build credibility with SMBs and stakeholders.")

st.divider()

# ---------- Attribution & partner card (placeholder) ----------
st.header("Attribution partners (placeholder)")
st.markdown("""
We plan optional integrations with attribution partners to support multi-channel conversion measurement:
- Branch (placeholder)  
- AppsFlyer (placeholder)
""")
small_note("Integration requires partnership agreements and backend support. Marked for Phase 2.")

# ---------- Footer ----------
st.write("")
st.markdown("---")
st.markdown("AdEase — prototype. Designed for SMBs. Built for speed and trust.")
small_note("To deploy: upload this file + requirements.txt to a GitHub repo and use Streamlit Cloud (share.streamlit.io).")
