import streamlit as st
import home
import chatbot
from urllib.parse import unquote

st.set_page_config(page_title="NOLAN", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom, #cce5ff, #99ccff, #66b3ff, #3399ff);
        background-attachment: fixed;
    }
    .stForm {
        background-color: rgba(255, 255, 255, 1);
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        width: 100%;
        min-width: 500px;
        margin: auto;
    }
    .centered {
        text-align: center;
    }
    .navbar {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 20px;
        padding: 15px 30px 0 0;
        background-color: transparent;
        margin-bottom: 60px;
    }
    .nav-btn {
        padding: 8px 16px;
        background-color: white;
        border-radius: 8px;
        font-weight: 500;
        text-decoration: none;
        color: black;
        border: none;
        transition: 0.2s ease-in-out;
        font-family: 'Segoe UI', sans-serif;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    .nav-btn:hover {
        background-color: #eeeeee;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

def get_all_cookies():
    try:
        headers = st.context.headers
    except AttributeError:
        return {}
    if not headers or "cookie" not in headers:
        return {}
    cookie_string = headers["cookie"]
    cookie_kv_pairs = cookie_string.split(";")
    cookie_dict = {}
    for kv in cookie_kv_pairs:
        parts = kv.split("=", 1)
        if len(parts) == 2:
            cookie_dict[parts[0].strip()] = unquote(parts[1].strip())
    return cookie_dict

if "logged_out" not in st.session_state:
    st.session_state.logged_out = False
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "page" not in st.session_state:
    st.session_state.page = "home"
if "users" not in st.session_state:
    st.session_state.users = {"admin": "hugolpb"}
if "messages" not in st.session_state:
    st.session_state.messages = []

cookies = get_all_cookies()
cookie_username = cookies.get("nolan_user")

if cookie_username and not st.session_state.authenticated and not st.session_state.logged_out:
    st.session_state.username = cookie_username
    st.session_state.authenticated = True
    st.session_state.page = "chatbot"

def display_navbar():
    col_spacer, col_icon = st.columns([11, 1])
    with col_icon:
        with st.popover("⚙️", use_container_width=True):
            st.markdown("### Options")
            st.write("---")
            if st.button("🛠️ Settings"):
                st.info("Paramètres à venir...")
            if st.button("👤 Account"):
                st.info("Profil bientôt disponible...")
            if st.button("🚪 Disconnect"):
                st.session_state.authenticated = False
                st.session_state.username = ""
                st.session_state.page = "home"
                st.session_state.messages = []
                st.session_state.logged_out = True
                st.markdown("""
                    <script>
                        document.cookie = "nolan_user=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC;";
                    </script>
                """, unsafe_allow_html=True)
                st.rerun()
    st.markdown('<div class="navbar-space"></div>', unsafe_allow_html=True)

if st.session_state.authenticated:
    display_navbar()

if st.session_state.page == "home":
    home.display()
elif st.session_state.page == "chatbot" and st.session_state.authenticated:
    chatbot.display()
else:
    st.error("Erreur d'accès. Veuillez vous connecter.")
