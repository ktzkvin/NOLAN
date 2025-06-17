import streamlit as st

def display():
    cols = st.columns([1, 1, 1])

    with cols[1]:
        # 🔼 Logo centré en haut
        st.markdown("<div style='text-align:center; margin-bottom: 20px;'>", unsafe_allow_html=True)
        st.image("assets/logo.png", width=150)  # adapte le chemin si nécessaire
        st.markdown("</div>", unsafe_allow_html=True)

        # 📝 Formulaire de connexion
        with st.form("login_form"):
            st.markdown("<h2 style='text-align:center;'>Sign In</h2>", unsafe_allow_html=True)
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Login")

            if submitted:
                if username in st.session_state.users and st.session_state.users[username] == password:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.page = "chatbot"
                    st.success("Login successful ✅")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")