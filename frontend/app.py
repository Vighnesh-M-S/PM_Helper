import streamlit as st
import requests

API = "http://localhost:8000"

st.set_page_config(page_title="PM_Helper", layout="wide")

st.title("📁 PM_Helper – Case Study Generator")



page = st.sidebar.selectbox("Choose View", ["Create Case Study"])

if page == "Create Case Study":
    st.subheader("Create New Case Study")

    with st.form("case_form"):
        title = st.text_input("Project Title")
        overview = st.text_area("Project Overview")
        tools = st.multiselect("Tools Used", ["Python", "React", "Figma"])
        outcomes = st.text_area("Outcomes (comma-separated key:value)")
        media = st.text_input("Image URLs (comma separated)")
        submit = st.form_submit_button("Save")

        if submit and username:
            outcome_dict = {o.split(":")[0]: o.split(":")[1] for o in outcomes.split(",") if ":" in o}
            payload = {
                "username": username,
                "title": title,
                "overview": overview,
                "tools": tools,
                "outcomes": outcome_dict,
                "media": media.split(",")
            }
            res = requests.post(f"{API}/add_case_study", json=payload)
            st.success("Saved!" if res.ok else "Error saving.")

