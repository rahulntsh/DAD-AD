# app.py
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="AdEase – Campaign Creator", layout="centered")

# ----- Style -----
st.markdown("""
<style>
body {background-color: #000;}
div.stButton > button:first-child {background-color: #007bff;color:white;border-radius:8px;}
.box {background-color:#111;padding:20px;border-radius:12px;margin-bottom:15px;}
h1, h2, h3, h4, p, label {color:white;}
table {color:white;}
</style>
""", unsafe_allow_html=True)

# ----- App State -----
if "campaigns" not in st.session_state:
    st.session_state["campaigns"] = []

# ----- Entry Options -----
st.title("AdEase — Self-Serve Campaign Tool")
choice = st.radio("Choose an option:", ["Generate New Campaign", "Upload Previous Campaign"])

if choice == "Upload Previous Campaign":
    uploaded = st.file_uploader("Upload your saved campaign file (CSV/JSON)")
    if uploaded:
        st.session_state["campaigns"] = pd.read_csv(uploaded).to_dict("records")
        st.success("Campaigns loaded successfully.")
else:
    st.markdown("<div class='box'>", unsafe_allow_html=True)
    st.header("Step 1 — Business Details")
    business_type = st.selectbox("Select your business type", 
        ["Retail / Store", "Restaurant / Cafe", "Salon / Wellness", 
         "Education / Coaching", "E-commerce", "Services (local)", "Other"])
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='box'>", unsafe_allow_html=True)
    st.header("Step 2 — Target Segment")
    st.write("Select who you want to reach:")
    age_group = st.selectbox("Age Group", ["18-25", "26-35", "36-45", "46-60", "60+"])
    gender = st.selectbox("Gender", ["All", "Male", "Female", "Other"])
    location = st.text_input("City / Locality", placeholder="e.g., Pune")
    interest = st.selectbox("Interest Type", ["Food & Dining", "Beauty & Wellness", 
                    "Education & Learning", "Shopping", "Finance", "Home Services"])
    lifestyle = st.selectbox("Lifestyle Tier", ["Budget-conscious", "Mid-range", "Premium"])
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='box'>", unsafe_allow_html=True)
    st.header("Step 3 — Marketing Goal & Budget")
    goal = st.selectbox("Marketing Goal", ["Increase Visits", "Get Leads", "Boost Awareness"])
    budget = st.slider("Set Budget (₹)", 1000, 50000, 5000, step=500)
    creative = st.radio("Ad Format", ["Text", "Image", "Short Video"], horizontal=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Create Campaign"):
        st.success("Campaign Created Successfully.")
        st.session_state["campaigns"].append({
            "Business": business_type,
            "Goal": goal,
            "Budget": budget,
            "Creative": creative,
            "Age": age_group,
            "Gender": gender,
            "Interest": interest,
            "Lifestyle": lifestyle,
            "Location": location
        })

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='box'>", unsafe_allow_html=True)
        if st.button("View Insights"):
            st.session_state["view_insights"] = True
        st.markdown("</div>", unsafe_allow_html=True)

# ----- Insights Page -----
if st.session_state.get("view_insights"):
    st.header("Campaign Insights")
    if len(st.session_state["campaigns"]) == 0:
        st.warning("No campaigns created yet.")
    else:
        df = pd.DataFrame(st.session_state["campaigns"])
        st.table(df[["Business","Goal","Budget","Creative","Location"]])

        selected = st.selectbox("Select a campaign to view metrics", df["Business"])
        campaign = df[df["Business"] == selected].iloc[0]

        # Generate 3 relevant metrics depending on goal
        np.random.seed(42)
        reach = np.random.randint(5000, 15000)
        engagements = np.random.randint(200, 800)
        cpm = round(np.random.uniform(45, 75), 2)

        st.markdown("<div class='box'>", unsafe_allow_html=True)
        st.subheader(f"Insights for {campaign['Business']} ({campaign['Goal']})")
        if campaign["Goal"] == "Get Leads":
            m1, m2, m3 = st.columns(3)
            m1.metric("People Reached", f"{reach:,}")
            m2.metric("Leads / Clicks", f"{engagements}")
            m3.metric("Estimated Cost per 1000 Views (₹)", f"{cpm}")
        elif campaign["Goal"] == "Boost Awareness":
            m1, m2, m3 = st.columns(3)
            m1.metric("People Reached", f"{reach:,}")
            m2.metric("Engagements", f"{engagements}")
            m3.metric("Avg Cost per 1000 Views (₹)", f"{cpm}")
        else:
            m1, m2, m3 = st.columns(3)
            m1.metric("Visits / Actions", f"{engagements}")
            m2.metric("People Reached", f"{reach:,}")
            m3.metric("Avg Cost per 1000 Views (₹)", f"{cpm}")
        st.markdown("</div>", unsafe_allow_html=True)
