import streamlit as st

st.set_page_config(page_title="Dad Ad", page_icon="📊", layout="centered")

# Dark minimal style
st.markdown(
    """
    <style>
    body {background-color: #111; color: white;}
    .stButton>button {
        background-color: black; 
        color: white; 
        border-radius: 10px; 
        height: 70px; 
        width: 220px; 
        font-size: 20px;
        border: 1px solid white;
    }
    .stButton>button:hover {background-color: #222;}
    </style>
    """,
    unsafe_allow_html=True
)

# --- Page layout ---
st.markdown("<h1 style='text-align:center;'>DAD AD</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;'>Campaign Creation Tool</h3>", unsafe_allow_html=True)
st.write("")
st.write("")

col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("Generate New"):
        st.switch_page("pages/2_New_Campaign.py")
    st.write("")
    if st.button("Track Old"):
        st.switch_page("pages/1_Insights.py")
