# app.py
import streamlit as st
import requests, json
import pandas as pd
import numpy as np
from datetime import datetime

# ---------- CONFIG ----------
st.set_page_config(page_title="AdEase — Self-Serve Campaign Tool", layout="centered")

# ---------- SIMPLE STYLING ----------
st.markdown("""
<style>
body {background-color: #000;}
h1,h2,h3,h4,label,p,span,div{color:#fff !important;}
.box {background-color:#0f1113;padding:18px;border-radius:10px;margin-bottom:12px;border:1px solid #222;}
.home-btn {padding:18px;border-radius:10px;background:#b91c1c;color:white;font-weight:700;}
.small-muted{color:#aab0b6;font-size:13px}
</style>
""", unsafe_allow_html=True)

# ---------- HELPERS ----------
def hf_call(prompt, model="google/flan-t5-large"):
    """Call Hugging Face Inference API (requires HUGGINGFACE_API_KEY in secrets)"""
    key = st.secrets.get("HUGGINGFACE_API_KEY") if st.secrets else None
    if not key:
        return None, "MISSING_HF_KEY"
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {key}"}
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 600, "temperature": 0.2}}
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        # HF may return list/dict with 'generated_text' or raw string
        if isinstance(data, list) and isinstance(data[0], dict):
            text = data[0].get("generated_text") or data[0].get("generated_text", "")
        elif isinstance(data, dict) and "generated_text" in data:
            text = data["generated_text"]
        else:
            # fallback stringify
            text = json.dumps(data)
        return text, None
    except Exception as e:
        return None, str(e)

def estimate_reach_and_cpm(budget, business_type, creative_type):
    base_cpm_map = {
        "Retail / Store": 55, "Restaurant / Cafe":50, "Salon / Wellness":58,
        "Education / Coaching":65, "E-commerce":62, "Services (local)":59, "Other":60
    }
    base = base_cpm_map.get(business_type, 60)
    creative_factor = {"Text":0.98, "Image":1.0, "Short Video":1.15}
    cpm = base * creative_factor.get(creative_type,1.0)
    reach = int((budget / cpm) * 1000)
    return reach, round(cpm,2)

def extract_json_from_text(raw):
    """Try to extract JSON substring from model output."""
    if not raw or not isinstance(raw, str):
        return None
    start = raw.find('{')
    end = raw.rfind('}')
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(raw[start:end+1])
        except Exception:
            return None
    # try direct parse
    try:
        return json.loads(raw)
    except Exception:
        return None

def default_plan_text_from_json(plan):
    """Create a readable summary from plan JSON"""
    if not isinstance(plan, dict): return ""
    lines = []
    lines.append(f"Campaign: {plan.get('campaign_name','[name]')}")
    lines.append(f"Objective: {plan.get('objective','')}")
    lines.append(f"Budget: ₹{plan.get('budget','')}, Reach scope: {plan.get('reach_scope','')}")
    lines.append("")
    for i, adset in enumerate(plan.get("ad_sets", []), start=1):
        lines.append(f"Ad Set {i}: {adset.get('name','')}, Targeting: {adset.get('targeting')}, Budget%: {adset.get('budget_allocation')}")
        for j, ad in enumerate(adset.get("ads", []), start=1):
            lines.append(f"  Ad {j}: {ad.get('headline','')}")
            lines.append(f"    {ad.get('body','')}")
            lines.append(f"    Media: {ad.get('media')}, Direction: {ad.get('creative_direction','')}")
    return "\n".join(lines)

# ---------- SESSION STATE SETUP ----------
st.session_state.setdefault("page", "home")          # pages: home, create, upload, insights
st.session_state.setdefault("uploaded_file_name", "")
st.session_state.setdefault("campaigns", [])          # list of saved campaign dicts
st.session_state.setdefault("last_generated_plan", None)
st.session_state.setdefault("last_raw_text", "")

# ---------- NAVIGATION / HEADER ----------
st.markdown("<div style='display:flex;justify-content:space-between;align-items:center'>"
            "<h2 style='margin:0'>AdEase — Self-Serve Campaign Tool</h2>"
            "<div style='text-align:right'><small class='small-muted'>Prototype</small></div></div>", unsafe_allow_html=True)
st.write("")

# ---------- PAGE: HOME ----------
if st.session_state["page"] == "home":
    st.markdown("<div class='box' style='text-align:center'>", unsafe_allow_html=True)
    st.write("Choose an option to get started")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Create New Campaign", key="home_create"):
            st.session_state["page"] = "create"
            st.session_state["uploaded_file_name"] = ""
            st.session_state["last_generated_plan"] = None
    with col2:
        if st.button("Track / Upload Previous Campaign", key="home_upload"):
            st.session_state["page"] = "upload"
    st.markdown("</div>", unsafe_allow_html=True)

    # quick links
    c1,c2,c3 = st.columns(3)
    with c1:
        if st.button("View Insights"):
            st.session_state["page"] = "insights"
    with c2:
        st.write("")
    with c3:
        st.write("")

# ---------- PAGE: UPLOAD ----------
if st.session_state["page"] == "upload":
    st.markdown("<div class='box'>", unsafe_allow_html=True)
    st.subheader("Upload Previous Campaign Creative / File")
    st.write("Choose creative type first, then upload any file. We will accept any file type for now.")
    creative_type = st.selectbox("Creative Type", ["Image","Video","Text"], index=0)
    uploaded = st.file_uploader("Drop a file or browse (any type accepted)", type=None)
    if uploaded:
        st.success(f"Uploaded: {uploaded.name}")
        st.session_state["uploaded_file_name"] = uploaded.name
        # move user to create page with the uploaded name prefilled
        if st.button("Proceed to Campaign Creation"):
            st.session_state["page"] = "create"
    st.write("")
    if st.button("Back to Home"):
        st.session_state["page"] = "home"
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- PAGE: CREATE CAMPAIGN ----------
if st.session_state["page"] == "create":
    st.markdown("<div style='display:flex;align-items:center;justify-content:space-between'>", unsafe_allow_html=True)
    st.markdown("<h3> Create a Campaign </h3>", unsafe_allow_html=True)
    if st.button("Back to Home"):
        st.session_state["page"] = "home"
        st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Step 1 — Business sector & description
    st.markdown("<div class='box'>", unsafe_allow_html=True)
    st.subheader("Step 1 — Business details")
    business_type = st.selectbox("Company Sector", ["Retail / Store","Restaurant / Cafe","Salon / Wellness",
                                                     "Education / Coaching","E-commerce","Services (local)","Other"])
    suggestion = "Name, website, how old?, locality, what you sell (brief)."
    description = st.text_area("Description (the more detail the better)", value=(st.session_state.get("uploaded_file_name","") or ""), help=suggestion, height=120)
    usp = st.text_input("Unique selling point (optional)", placeholder="e.g., Handmade sweets with family recipe")
    if description.strip():
        st.session_state["step1_ok"] = True
    else:
        st.session_state["step1_ok"] = False
    st.markdown("</div>", unsafe_allow_html=True)

    # Step 2 — Segmentation (visible only if step1_ok)
    if st.session_state.get("step1_ok"):
        st.markdown("<div class='box'>", unsafe_allow_html=True)
        st.subheader("Step 2 — Target segment (5 fields)")
        age_group = st.selectbox("Age group", ["18-25","26-35","36-45","46-60","60+"])
        gender = st.selectbox("Gender", ["All","Male","Female","Other"])
        location = st.text_input("City / Locality", placeholder="e.g., Pune")
        interest = st.selectbox("Interest (psychographic)", ["Food & Dining","Beauty & Wellness","Education",
                                                             "Shopping","Finance","Home Services"])
        lifestyle = st.selectbox("Lifestyle Tier", ["Budget-conscious","Mid-range","Premium"])
        if all([age_group, gender, location, interest, lifestyle]):
            st.session_state["step2_ok"] = True
        else:
            st.session_state["step2_ok"] = False
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Fill the business description to unlock targeting.")

    # Step 3 — Goal + Reach slider + Budget (visible only if step2_ok)
    if st.session_state.get("step2_ok"):
        st.markdown("<div class='box'>", unsafe_allow_html=True)
        st.subheader("Step 3 — Goal, Reach and Budget")
        goal = st.selectbox("Marketing goal", ["Increase Visits","Get Leads","Boost Awareness","Other"])
        reach_scope = st.radio("Reach scope (pick one)", ["Locality","City","State","National"], horizontal=True)
        budget = st.slider("Budget (₹)", 1000, 50000, 5000, step=500)
        creative_choice = st.radio("Creative format you'll run", ["Text","Image","Short Video"], horizontal=True)
        est_reach, est_cpm = estimate_reach_and_cpm(budget, business_type, creative_choice)
        st.markdown(f"**Estimated reach:** ~{est_reach:,} people — **Est CPM:** ₹{est_cpm}")
        st.markdown("</div>", unsafe_allow_html=True)

        # Generate with LLM
        st.markdown("<div class='box'>", unsafe_allow_html=True)
        st.write("Generate a campaign plan using an LLM. (Hugging Face API must be configured in Streamlit Secrets.)")
        if st.button("Generate Campaign with AI"):
            # build prompt
            prompt = f"""
You are an expert digital ad planner. Output ONLY valid JSON with schema:
{{"campaign_name":"","objective":"","budget":0,"reach_scope":"","ad_sets":[{{"name":"","targeting":{{"age":"","gender":"","interest":"","location":"","lifestyle":""}},"budget_allocation":0,"ads":[{{"headline":"","body":"","media":"","creative_direction":""}}]}}]}}
Input:
Business sector: {business_type}
Description: {description}
USP: {usp}
Goal: {goal}
Budget: {budget}
Reach scope: {reach_scope}
Segmentation: Age={age_group}, Gender={gender}, Interest={interest}, Location={location}, Lifestyle={lifestyle}
Return 2-3 ad_sets and 2 ads per ad_set. Keep language simple for an SMB user.
"""
            with st.spinner("Calling Hugging Face model..."):
                raw_text, err = hf_call(prompt)
            if err:
                st.error("LLM call failed: " + str(err))
                st.session_state["last_raw_text"] = ""
                st.session_state["last_generated_plan"] = None
            else:
                st.session_state["last_raw_text"] = raw_text
                parsed = extract_json_from_text(raw_text)
                if parsed:
                    st.success("Generated a structured campaign plan.")
                    st.session_state["last_generated_plan"] = parsed
                    # create default human summary
                    summary = default_plan_text_from_json(parsed)
                    st.session_state["editable_summary"] = summary
                else:
                    st.warning("Model returned non-JSON output. You can edit the raw plan below.")
                    st.session_state["last_generated_plan"] = None
                    st.session_state["editable_summary"] = raw_text or "No output"
        st.write("")
        # show editable summary if any
        editable = st.session_state.get("editable_summary","")
        if editable:
            st.subheader("Review / Edit Generated Summary")
            edited = st.text_area("Edit the suggested campaign summary (or keep as is)", value=editable, height=260)
            if st.button("Save Plan & View Insights"):
                # convert edited back to a simple saved plan record
                saved_plan = {
                    "id": f"plan_{len(st.session_state['campaigns'])+1}",
                    "campaign_name": st.session_state.get("last_generated_plan",{}).get("campaign_name", f"{business_type} campaign"),
                    "objective": goal,
                    "budget": budget,
                    "reach_scope": reach_scope,
                    "business_type": business_type,
                    "description": description,
                    "usp": usp,
                    "segmentation": {"age":age_group,"gender":gender,"location":location,"interest":interest,"lifestyle":lifestyle},
                    "generated_json": st.session_state.get("last_generated_plan"),
                    "summary_text": edited,
                    "created_at": datetime.now().isoformat()
                }
                st.session_state["campaigns"].append(saved_plan)
                st.success("Plan saved.")
                st.session_state["page"] = "insights"
        st.markdown("</div>", unsafe_allow_html=True)

# ---------- PAGE: INSIGHTS ----------
if st.session_state["page"] == "insights":
    st.markdown("<div style='display:flex;align-items:center;justify-content:space-between'>", unsafe_allow_html=True)
    st.subheader("Campaigns & Insights")
    if st.button("Back to Home"):
        st.session_state["page"] = "home"
        st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    if len(st.session_state["campaigns"]) == 0:
        st.info("No saved campaigns yet. Create one first.")
    else:
        df = pd.DataFrame(st.session_state["campaigns"])
        st.write("Saved campaigns")
        # show table with small columns
        st.dataframe(df[["id","campaign_name","objective","budget","created_at"]].rename(columns={
            "id":"ID","campaign_name":"Campaign","objective":"Goal","budget":"Budget(₹)","created_at":"Created"
        }), height=220)
        # selector
        selected_idx = st.selectbox("Select a campaign to view 3 key metrics", list(range(len(st.session_state["campaigns"]))),
                                    format_func=lambda i: st.session_state["campaigns"][i]["id"] + " — " + st.session_state["campaigns"][i]["campaign_name"] if st.session_state["campaigns"][i].get("campaign_name") else st.session_state["campaigns"][i]["id"])
        camp = st.session_state["campaigns"][selected_idx]
        # compute metrics with estimate
        est_reach, est_cpm = estimate_reach_and_cpm(camp["budget"], camp["business_type"], "Image")
        # engagement heuristic
        engagement = int(est_reach * 0.03)  # assume 3% interactions
        col1,col2,col3 = st.columns(3)
        col1.metric("People Reached", f"{est_reach:,}")
        col2.metric("Engagements", f"{engagement:,}")
        col3.metric("Cost per 1000 Views (₹)", f"{est_cpm:.2f}")
        st.markdown("### Campaign Summary")
        st.code(camp.get("summary_text","No summary"))
        # export / download option
        if st.button("Download plan (JSON)"):
            st.download_button("Download JSON", data=json.dumps(camp, indent=2), file_name=f"{camp['id']}.json", mime="application/json")
