import streamlit as st
import json
import os

st.set_page_config(page_title="New Campaign", layout="wide")

# --- Styling ---
st.markdown(
    """
    <style>
    body {background-color: #111; color: white;}
    input, select, textarea {background-color:#222 !important; color:white !important;}
    .stButton>button {background-color:black; color:white; border-radius:8px;}
    </style>
    """, unsafe_allow_html=True
)

st.title("New Campaign")

# --- Inputs ---
sector = st.selectbox("Company Sector", [
    "Retail", "Technology", "FMCG", "Healthcare", "Education",
    "Hospitality", "Finance", "Entertainment", "Fashion", "Automobile"
])

desc = st.text_area("Description", placeholder="description (e.g., name, website, location, products...)")

st.subheader("Marketing Goals")
goals = ["Increase Reach", "Boost Awareness", "Engagement", "Other"]
selected_goal = st.radio("Select Goal", goals, horizontal=True)
other_goal = ""
if selected_goal == "Other":
    other_goal = st.text_input("Enter custom goal")

st.subheader("Target Age")
age = st.slider("Select age range", 0, 100, (20, 40))
ai_decide = st.checkbox("Let AI Decide")
if ai_decide:
    st.caption("AI will automatically determine optimal age range.")
    st.slider("Select age range", 0, 100, (20, 40), disabled=True)

st.subheader("Reach")
reach = st.radio("Select target region", ["My City", "My State", "My Country", "Global"], horizontal=True)

st.subheader("Budget")
budget = st.slider("Select budget (₹)", 1000, 500000, 10000, step=1000)

st.subheader("Creative Type")
creative = st.radio("Choose creative type", ["Text", "Video", "Audio"], horizontal=True)

# --- Buttons for creative ---
st.write("")
col1, col2 = st.columns(2)
with col1:
    upload = st.button("Upload File")
with col2:
    gen_ai = st.button("Generate via AI")

# --- Placeholder for output ---
if upload or gen_ai:
    st.success("This is how your ad looks 👇")
    st.image("https://placehold.co/600x400?text=Your+Ad+Preview", use_column_width=True)
    st.write("Estimated Reach: ~25,000 users")
    st.write("Estimated Cost per 1,000 impressions: ₹35")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("View Insights"):
            # Save campaign mock data
            if os.path.exists("campaigns.json"):
                with open("campaigns.json", "r") as f:
                    data = json.load(f)
            else:
                data = {"campaigns": []}

            new_campaign = {
                "sector": sector,
                "description": desc,
                "marketing_goal": other_goal if selected_goal == "Other" else selected_goal,
                "age_target": f"{age[0]}-{age[1]}" if not ai_decide else "AI decided",
                "reach": reach,
                "budget": budget,
                "creative_type": creative,
                "impressions": 20000,
                "ctr": 2.5,
                "frequency": 1.3
            }
            data["campaigns"].append(new_campaign)
            with open("campaigns.json", "w") as f:
                json.dump(data, f, indent=2)

            st.switch_page("pages/1_Insights.py")

    with c2:
        if st.button("Home"):
            st.switch_page("app.py")
