# app.py
import streamlit as st
import pandas as pd
import numpy as np

# ---------- CONFIG ----------
st.set_page_config(page_title="AdEase – Campaign Creator", layout="centered")

# ---------- STYLING ----------
st.markdown("""
<style>
body {background-color: #000;}
h1,h2,h3,h4,label,p,span,div{color:white !important;}
div.stButton > button:first-child {
    background-color:#007bff;color:white;border-radius:8px;
    padding:10px 20px;font-weight:600;margin:5px;
}
.box {background-color:#111;padding:20px;border-radius:12px;margin:12px 0;}
</style>
""", unsafe_allow_html=True)

# ---------- STATE ----------
for k,v in {
    "mode":None,"step1_done":False,"step2_done":False,
    "show_insights":False,"campaigns":[]
}.items():
    st.session_state.setdefault(k,v)

# ---------- HEADER ----------
st.title("AdEase — Self-Serve Campaign Tool")

# ---------- MODE SELECTION ----------
col1,col2 = st.columns(2)
with col1:
    if st.button("🪄 Generate New Campaign"):
        st.session_state.mode = "generate"
        st.session_state.step1_done = st.session_state.step2_done = False
        st.session_state.show_insights = False
with col2:
    if st.button("📁 Upload Previous Campaign"):
        st.session_state.mode = "upload"
        st.session_state.step1_done = st.session_state.step2_done = False
        st.session_state.show_insights = False

# ---------- UPLOAD OR GENERATE ----------
if st.session_state.mode == "upload":
    st.markdown("<div class='box'>", unsafe_allow_html=True)
    st.subheader("Upload your previous creative")
    file_type = st.selectbox("Creative Type", ["Image","Video","Text"])
    uploaded = st.file_uploader("Drop or choose your file", type=None)
    if uploaded:
        st.success(f"{uploaded.name} uploaded.")
        st.session_state.step1_done = True
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.mode == "generate":
    st.session_state.step1_done = True

# ---------- STEP 1 – BUSINESS DETAILS ----------
if st.session_state.step1_done:
    st.markdown("<div class='box'>", unsafe_allow_html=True)
    st.header("Step 1 — Business Details")
    business_type = st.selectbox("Business Type", 
        ["Retail / Store","Restaurant / Cafe","Salon / Wellness",
         "Education / Coaching","E-commerce","Services (local)","Other"])
    if business_type:
        st.session_state.step2_ready = True
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.stop()

# ---------- STEP 2 – SEGMENTATION ----------
if st.session_state.get("step2_ready"):
    st.markdown("<div class='box'>", unsafe_allow_html=True)
    st.header("Step 2 — Target Segment")
    age_group = st.selectbox("Age Group", ["18-25","26-35","36-45","46-60","60+"])
    gender = st.selectbox("Gender", ["All","Male","Female","Other"])
    location = st.text_input("City / Locality", placeholder="e.g., Pune")
    interest = st.selectbox("Interest Type", 
        ["Food & Dining","Beauty & Wellness","Education & Learning",
         "Shopping","Finance","Home Services"])
    lifestyle = st.selectbox("Lifestyle Tier", 
        ["Budget-conscious","Mid-range","Premium"])
    if all([age_group,gender,location,interest,lifestyle]):
        st.session_state.step2_done = True
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- STEP 3 – GOAL + BUDGET ----------
if st.session_state.step2_done:
    st.markdown("<div class='box'>", unsafe_allow_html=True)
    st.header("Step 3 — Marketing Goal & Budget")
    goal = st.selectbox("Goal", ["Increase Visits","Get Leads","Boost Awareness"])
    budget = st.slider("Budget (₹)",1000,50000,5000,step=500)
    creative = st.radio("Creative Format", ["Text","Image","Short Video"], horizontal=True)
    if st.button("Create Campaign"):
        st.session_state.campaigns.append({
            "Business":business_type,"Goal":goal,"Budget":budget,"Creative":creative,
            "Age":age_group,"Gender":gender,"Interest":interest,
            "Lifestyle":lifestyle,"Location":location
        })
        st.success("✅ Campaign created successfully.")
        st.session_state.show_insights = True
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- INSIGHTS ----------
if st.session_state.show_insights and len(st.session_state.campaigns)>0:
    st.markdown("<div class='box'>", unsafe_allow_html=True)
    st.header("Insights")
    df = pd.DataFrame(st.session_state.campaigns)
    st.table(df[["Business","Goal","Budget","Creative","Location"]])
    selected = df.iloc[-1]   # show last campaign
    np.random.seed(0)
    reach = np.random.randint(5000,15000)
    engagement = np.random.randint(200,800)
    cpm = np.random.uniform(45,75)
    c1,c2,c3 = st.columns(3)
    c1.metric("People Reached", f"{reach:,}")
    c2.metric("Engagements", f"{engagement}")
    c3.metric("Cost per 1000 Views (₹)", f"{cpm:.2f}")
    st.markdown("</div>", unsafe_allow_html=True)
