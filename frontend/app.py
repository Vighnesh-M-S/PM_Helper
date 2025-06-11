import streamlit as st
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("API")


API = "http://localhost:8000"

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.template = None
    st.session_state.portfolio_data = {}

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
    templates = ["Minimal", "With Image", "Detailed"]
    cols = st.columns(len(templates))
    for i, template in enumerate(templates):
        with cols[i]:
            st.image(f"https://via.placeholder.com/200x150.png?text={template}")
            if st.button(f"Select {template}"):
                st.session_state.template = template
                st.success(f"{template} template selected!")
                st.rerun()

def build_form():
    st.title(f"🧰 Fill Portfolio Details ({st.session_state.template} Template)")

    # Initialize default data for preview
    title = ""
    overview = ""
    image_link = ""
    media_links = []
    timeline = ""
    tools = []
    outcomes = ""

    with st.form("portfolio_form"):
        title = st.text_input("Title")

        if st.session_state.template == "Minimal":
            overview = st.text_area("Overview")

        elif st.session_state.template == "With Image":
            overview = st.text_area("Overview")
            image_link = st.text_input("Image Link (URL)")

        elif st.session_state.template == "Detailed":
            overview = st.text_area("Project Overview")
            media_links = st.text_area("Media Links (comma-separated)").split(",")
            timeline = st.text_area("Timeline")
            tools = st.text_input("Tools Used (comma-separated)").split(",")
            outcomes = st.text_area("Outcomes / Testimonials")

        submit = st.form_submit_button("Save Portfolio")

    preview_data = {
        "theme": st.session_state.template,
        "title": title,
        "overview": overview,
        "media": ([image_link] if st.session_state.template == "With Image" and image_link else media_links),
        "timeline": timeline,
        "tools": tools,
        "outcomes": outcomes,
    }

    if submit:
        payload = {
            "username": st.session_state.username,
            "theme": st.session_state.template,
            "title": title,
            "overview": overview,
            "media": preview_data["media"],
            "timeline": timeline if st.session_state.template == "Detailed" else "",
            "tools": tools if st.session_state.template == "Detailed" else [],
            "outcomes": outcomes if st.session_state.template == "Detailed" else "",
        }
        res = requests.post(f"{API}/portfolio", json=payload)
        if res.status_code == 200:
            st.toast("✅ Portfolio Saved Successfully!", icon="🎉")
            # Clear form manually but DO NOT rerun
            st.session_state.template = None
        else:
            st.error("Failed to save portfolio.")

    st.markdown("---")
    st.header("🔍 Live Preview")
    render_preview(preview_data)

def render_preview(portfolio):
    theme = portfolio.get("theme")
    title = portfolio.get("title", "")
    overview = portfolio.get("overview", "")
    media = portfolio.get("media", [])
    timeline = portfolio.get("timeline", "")
    tools = portfolio.get("tools", [])
    outcomes = portfolio.get("outcomes", "")

    box_style = """
        <style>
            .preview-box {
                border: 1px solid #ddd;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                background-color: #f9f9f9;
            }
            .preview-title {
                font-weight: bold;
                font-size: 24px;
                margin-bottom: 10px;
            }
            .preview-overview {
                font-size: 16px;
                margin-top: 10px;
            }
            .preview-image {
                max-width: 100%;
                margin: 10px 0;
                border-radius: 6px;
            }
        </style>
    """
    st.markdown(box_style, unsafe_allow_html=True)

    if theme == "Minimal":
        st.markdown(f"""
        <div class="preview-box">
            <div class="preview-title">{title}</div>
            <div class="preview-overview">{overview}</div>
        </div>
        """, unsafe_allow_html=True)

    elif theme == "With Image":
        img_html = f'<img src="{media[0]}" class="preview-image">' if media else ""
        st.markdown(f"""
        <div class="preview-box">
            <div class="preview-title">{title}</div>
            {img_html}
            <div class="preview-overview">{overview}</div>
        </div>
        """, unsafe_allow_html=True)

    elif theme == "Detailed":
        media_html = ""
        for link in media:
            link = link.strip()
            if not link:
                continue
            # If link ends with video extension, embed video
            if link.endswith(('.mp4', '.webm', '.ogg')):
                media_html += f'<video controls src="{link}" style="max-width:100%; margin-bottom: 10px; border-radius: 6px;"></video>'
            else:
                media_html += f'<img src="{link}" class="preview-image">'
        tools_str = ", ".join([t.strip() for t in tools if t.strip()])
        st.markdown(f"""
        <div class="preview-box">
            <div class="preview-title">{title}</div>
            {media_html}
            <div class="preview-overview">{overview}</div>
            <div><b>Timeline:</b> {timeline}</div>
            <div><b>Tools Used:</b> {tools_str}</div>
            <div><b>Outcomes / Testimonials:</b> {outcomes}</div>
        </div>
        """, unsafe_allow_html=True)

def view_my_portfolios():
    st.title("📁 My Portfolios")
    res = requests.get(f"{API}/portfolio/{st.session_state.username}")
    if res.status_code == 200:
        data = res.json()
        if not data:
            st.info("You have no portfolios yet.")
            return
        for portfolio in data:
            render_preview(portfolio)
            st.markdown(f"**👁️ Views:** {portfolio.get('views', 0)} | ❤️ Likes: {portfolio.get('likes', 0)}")
            st.markdown("---")
    else:
        st.warning("Failed to fetch portfolios.")


def public_portfolios():
    st.title("🌐 Public Portfolios")
    res = requests.get(f"{API}/portfolios")
    if res.status_code == 200:
        data = res.json()
        if not data:
            st.info("No public portfolios available.")
            return

        for portfolio in data:
            # Show title & author, and a "Preview" button
            col1, col2, col3 = st.columns([3, 3, 1])
            with col1:
                st.markdown(f"### {portfolio.get('title', 'Untitled')}")
            with col2:
                st.markdown(f"**Author:** {portfolio.get('username', '')}")
            with col3:
                if st.button(f"Preview {portfolio['title']}", key=f"preview_{portfolio['id']}"):
                    # Call backend to increment views + auto-like logic if needed
                    # For demo: just show preview below
                    st.session_state.selected_public_portfolio = portfolio
                    # Call backend to increment views (handled separately)
                    try:
                        requests.post(f"{API}/portfolio/view/{portfolio['id']}", params={"viewer": st.session_state.username})
                    except:
                        pass
                    # Refresh UI to show preview
                    st.rerun()

        # Show selected portfolio preview
        if "selected_public_portfolio" in st.session_state:
            st.markdown("---")
            st.subheader("Portfolio Preview")
            render_preview(st.session_state.selected_public_portfolio)
            st.markdown(f"**👁️ Views:** {st.session_state.selected_public_portfolio.get('views', 0)} | ❤️ Likes: {st.session_state.selected_public_portfolio.get('likes', 0)}")
            # Like button with one like per user
            if st.button("Like ❤️", key=f"like_{st.session_state.selected_public_portfolio['id']}"):
                try:
                    res = requests.post(f"{API}/portfolio/like/{st.session_state.selected_public_portfolio['id']}", params={"liker": st.session_state.username})
                    if res.status_code == 200:
                        st.success("Liked!")
                        # Update like count locally to avoid refresh
                        st.session_state.selected_public_portfolio["likes"] += 1
                    else:
                        st.warning(res.json().get("detail", "Already liked"))
                except:
                    st.error("Error liking portfolio")
    else:
        st.warning("Failed to load public portfolios.")

def main():

    st.sidebar.title("📂 Navigation")

    if not st.session_state.get("logged_in"):
        login_page()
        return

    # Always visible sidebar
    page = st.sidebar.radio("Choose Page", ["Build Portfolio", "My Portfolios", "Public Portfolios", "Logout"])

    if page == "Logout":
        st.session_state.logged_in = False
        st.session_state.template = None
        st.session_state.username = ""
        st.success("Logged out.")
        st.rerun()

    elif page == "Build Portfolio":
        if st.sidebar.button("🔄 Reset Template"):
            st.session_state.template = None
            st.rerun()
        if not st.session_state.get("template"):
            select_template()
        else:
            build_form()

    elif page == "My Portfolios":
        view_my_portfolios()

    elif page == "Public Portfolios":
        public_portfolios()
main()