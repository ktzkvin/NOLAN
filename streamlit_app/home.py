import streamlit as st
import streamlit.components.v1 as components

def display():
    cols = st.columns([1, 1, 1])
    with cols[1]:
        left, center, right = st.columns([1, 1, 1])
        with center:
            st.image("assets/logo.png", width=150)
        st.markdown("<h2 style='text-align:center;'>Sign In</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Login")
            if submitted:
                if username in st.session_state.users and st.session_state.users[username] == password:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.page = "chatbot"
                    st.session_state.logged_out = False
                    components.html(
                        f"""
                        <script>
                            document.cookie = "nolan_user={username}; path=/; max-age=604800";
                        </script>
                        """,
                        height=0
                    )
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
