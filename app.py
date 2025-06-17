import streamlit as st
import home
import chatbot

st.set_page_config(page_title="NOLAN", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom, #cce5ff, #99ccff, #66b3ff, #3399ff);
        background-attachment: fixed;
    }

    /* Formulaires Streamlit */
    .stForm {
        background-color: rgba(255, 255, 255, 1);
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        width: 100%;
        min-width: 500px;
        margin: auto;
    }

    /* Centrer tous les éléments markdown */
    .centered {
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        body {
            background-color: #e6f0ff;  /* Bleu très clair */
        }
        .stApp {
            background-color: #e6f0ff;
        }
    </style>
""", unsafe_allow_html=True)



# Initialisation
if "page" not in st.session_state:
    st.session_state.page = "home"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "users" not in st.session_state:
    # ⚠️ Exemple d’utilisateurs autorisés en dur
    st.session_state.users = {
        "admin": "admin",
        "kevin_salopard": "vieillepute"
    }
if "messages" not in st.session_state:
    st.session_state.messages = []

def display_navbar():
    cols = st.columns([1, 1, 1, 1])

    # 🔹 Colonne 0 : logo centré
    with cols[0]:
        subcol1, subcol2, subcol3 = st.columns([1, 2, 1])
        with subcol2:
            st.markdown(
                """
                <div style="text-align: center; position: relative; top: -50px;">
                """,
                unsafe_allow_html=True
            )
            st.image("assets/logo.png", width=150)
            st.markdown(
                """
                </div>
                """,
                unsafe_allow_html=True
            )

    # 🔹 Colonne 1 : Chatbot bouton centré
    with cols[1]:
        subcol1, subcol2, subcol3 = st.columns([1, 2, 1])
        with subcol2:
            if st.button("💬 Chatbot"):
                st.session_state.page = "chatbot"

    # 🔹 Colonne 2 : Account
    with cols[2]:
        subcol1, subcol2, subcol3 = st.columns([1, 2, 1])
        with subcol2:
            if st.button("👤 Account"):
                st.info("Fonctionnalité à venir...")

    # 🔹 Colonne 3 : Disconnect
    with cols[3]:
        subcol1, subcol2, subcol3 = st.columns([1, 2, 1])
        with subcol2:
            if st.button("🚪 Disconnect"):
                st.session_state.authenticated = False
                st.session_state.username = ""
                st.session_state.page = "home"
                st.session_state.messages = []
                st.rerun()




if st.session_state.authenticated:
    display_navbar()

# 🔁 Navigation
if st.session_state.page == "home":
    home.display()
elif st.session_state.page == "chatbot" and st.session_state.authenticated:
    chatbot.display()
else:
    st.error("Erreur d'accès. Veuillez vous connecter.")
