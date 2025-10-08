import streamlit as st
import json
import os

st.set_page_config(page_title="Insights", layout="centered")

# --- Load campaign data ---
if os.path.exists("campaigns.json"):
    with open("campaigns.json", "r") as f:
        data = json.load(f)
else:
    data = {"campaigns": []}

num_campaigns = len(data["campaigns"])

st.markdown("<h1 style='color:white;'>Insights</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='color:white;'>Choose Campaign</h3>", unsafe_allow_html=True)

if num_campaigns == 0:
    selected = st.selectbox(" ", ["No Campaign"])
else:
    options = [f"Campaign {i+1}" for i in range(num_campaigns)]
    selected = st.selectbox(" ", options)

st.write("---")

# Display campaign data
if selected != "No Campaign":
    idx = int(selected.split(" ")[1]) - 1
    c = data["campaigns"][idx]
    st.subheader(c.get("description", ""))
    st.write(f"**Impressions:** {c.get('impressions', 'N/A')}")
    st.write(f"**CTR:** {c.get('ctr', 'N/A')}%")
    st.write(f"**Frequency:** {c.get('frequency', 'N/A')}")
else:
    st.info("No campaign data available.")
