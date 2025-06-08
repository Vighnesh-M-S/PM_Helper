import streamlit as st
import requests
import json

API = "http://localhost:8000"

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.template = None

def login_page():
    st.title("🔐 Login or Register")
    mode = st.radio("Select mode:", ["Login", "Register"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button(mode):
        res = requests.post(f"{API}/{mode.lower()}", json={"username": username, "password": password})
        if res.status_code == 200:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"{mode} successful. Welcome, {username}!")
            st.rerun()
        else:
            st.error(res.json().get("detail"))

def select_template():
    st.title("🎨 Choose a Portfolio Template")
    templates = ["Classic", "Modern", "Minimal"]
    cols = st.columns(len(templates))
    for i, template in enumerate(templates):
        with cols[i]:
            st.image(f"https://via.placeholder.com/200x150.png?text={template}")
            if st.button(f"Select {template}"):
                st.session_state.template = template
                st.rerun()

def build_form():
    st.title(f"🧰 Fill Portfolio Details ({st.session_state.template} Theme)")
    with st.form("portfolio_form"):
        title = st.text_input("Project Title")
        overview = st.text_area("Project Overview")
        media_links = st.text_area("Media Links (comma-separated)").split(",")
        timeline = st.text_area("Timeline")
        tools = st.text_input("Tools Used (comma-separated)").split(",")
        outcomes = st.text_area("Outcomes / Testimonials")
        submit = st.form_submit_button("Save Portfolio")

        if submit:
            payload = {
                "username": st.session_state.username,
                "title": title,
                "overview": overview,
                "media": media_links,
                "timeline": timeline,
                "tools": tools,
                "outcomes": outcomes,
                "theme": st.session_state.template,
            }
            res = requests.post(f"{API}/portfolio", json=payload)
            if res.status_code == 200:
                st.success("✅ Portfolio Saved Successfully!")
            else:
                st.error("Failed to save portfolio.")

    st.markdown("---")
    st.header("🔍 Live Preview")
    st.markdown(f"### Theme: {st.session_state.template}")
    st.markdown(f"**Title:** {title}")
    st.markdown(f"**Overview:** {overview}")
    st.markdown(f"**Timeline:** {timeline}")
    st.markdown(f"**Tools:** {', '.join(tools)}")
    st.markdown(f"**Media:** {', '.join(media_links)}")
    st.markdown(f"**Outcomes:** {outcomes}")

def view_my_portfolios():
    st.title("📁 My Portfolios")
    res = requests.get(f"{API}/portfolio/{st.session_state['username']}")
    if res.status_code == 200:
        for data in res.json():
            st.subheader(f"Your Portfolio - {data.get('theme', '')} Theme")
            st.markdown(f"**Title:** {data.get('title', '')}")
            st.markdown(f"**Overview:** {data.get('overview', '')}")
            st.markdown(f"**Timeline:** {data.get('timeline', '')}")
            st.markdown(f"**Tools:** {', '.join(data.get('tools', []))}")
            st.markdown(f"**Media:** {', '.join(data.get('media', []))}")
            st.markdown(f"**Outcomes:** {data.get('outcomes', '')}")
            st.markdown(f"**👁️ Views:** {data.get('views', 0)} | ❤️ Likes: {data.get('likes', 0)}")
            st.markdown("---")
    else:
        st.warning("No portfolio found.")

def public_portfolios():
    st.title("🌐 Public Portfolios")
    res = requests.get(f"{API}/portfolios")
    if res.status_code == 200:
        for portfolio in res.json():
            st.markdown(f"### {portfolio['title']} by {portfolio['username']}")
            if st.button(f"👁️ Preview {portfolio['id']}"):
                # Auto-like when previewed
                if st.session_state.username != portfolio['username']:
                    requests.post(f"{API}/portfolio/view/{portfolio['id']}?viewer={st.session_state.username}")
                st.markdown(f"**Theme:** {portfolio.get('theme', '')}")
                st.markdown(f"**Overview:** {portfolio.get('overview', '')}")
                st.markdown(f"**Timeline:** {portfolio.get('timeline', '')}")
                st.markdown(f"**Tools:** {', '.join(portfolio.get('tools', []))}")
                st.markdown(f"**Media:** {', '.join(portfolio.get('media', []))}")
                st.markdown(f"**Outcomes:** {portfolio.get('outcomes', '')}")
                st.markdown(f"**👁️ Views:** {portfolio.get('views', 0)} | ❤️ Likes: {portfolio.get('likes', 0)}")
            if st.button(f"❤️ Like {portfolio['id']}"):
                try:
                    like_res = requests.post(f"{API}/portfolio/like/{portfolio['id']}?liker={st.session_state.username}")
                    if like_res.status_code == 200:
                        st.success("❤️ Liked!")
                    else:
                        try:
                            detail = like_res.json().get("detail", "Already liked.")
                        except json.JSONDecodeError:
                            detail = "Already liked."
                        st.warning(detail)
                except requests.RequestException as e:
                    st.error(f"Failed to like portfolio: {e}")

            st.markdown("---")
    else:
        st.error("Failed to load public portfolios.")

def main():
    if not st.session_state.logged_in:
        login_page()
    elif not st.session_state.template:
        select_template()
    else:
        page = st.sidebar.radio("Navigation", ["Build Portfolio", "My Portfolios", "Explore Public", "Logout"])
        if page == "Build Portfolio":
            build_form()
        elif page == "My Portfolios":
            view_my_portfolios()
        elif page == "Explore Public":
            public_portfolios()
        elif page == "Logout":
            st.session_state.logged_in = False
            st.session_state.template = None
            st.session_state.username = ""
            st.success("Logged out.")
            st.rerun()

main()