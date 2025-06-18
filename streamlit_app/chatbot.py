import streamlit as st
import requests
import json
from PyPDF2 import PdfReader
from docx import Document
import sys
import os

# 🔧 Accès aux modules externes
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.chat_history import save_conversation, load_conversations


def display():
    # 🟦 Charger les conversations passées
    history = load_conversations(st.session_state.username)

    # 🟨 Afficher la sidebar
    st.sidebar.title("💬 Conversations")
    if history:
        for idx, convo in enumerate(history):
            label = f"Conversation {idx + 1}"
            if st.sidebar.button(label):
                st.session_state.messages = convo["messages"]
                st.rerun()
    else:
        st.sidebar.info("Aucune conversation enregistrée.")

    # 🟩 Affichage principal
    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.markdown(f"<h3 style='text-align:center;'>Welcome {st.session_state.username} 👋</h3>", unsafe_allow_html=True)

        with st.container():
            with st.form("chat_form", clear_on_submit=True):
                max_messages = 500
                messages_to_display = st.session_state.messages[-max_messages:]

                with st.container(height=500):
                    for msg in messages_to_display:
                        st.markdown(render_bubble(msg), unsafe_allow_html=True)

                uploaded_file = st.file_uploader("📄 Submit a document", type=["txt", "pdf", "docx"], label_visibility="visible")
                user_input = st.text_input("Your message :", placeholder="Start to say something...", label_visibility="visible")
                submitted = st.form_submit_button("Send")

        if submitted and user_input:
            user_msg = {"role": "user", "content": user_input}
            st.session_state.messages.append(user_msg)

            try:
                response = requests.post(
                    "http://127.0.0.1:8000/orchestrate/",
                    headers={"Content-Type": "application/json"},
                    data=json.dumps({"prompt": user_input})
                )

                if response.status_code == 200:
                    data = response.json()
                    assistant_reply = data.get("response", "No response from server.")
                else:
                    assistant_reply = f"❌ Server error: {response.status_code}"

            except Exception as e:
                assistant_reply = f"❌ Request failed: {e}"

            assistant_msg = {"role": "assistant", "content": assistant_reply}
            st.session_state.messages.append(assistant_msg)

            # 💾 Sauvegarde dans Cosmos DB
            save_conversation(st.session_state.username, st.session_state.messages)

            st.rerun()

        if uploaded_file is not None:
            file_type = uploaded_file.type

            if file_type == "text/plain":
                content = uploaded_file.read().decode("utf-8")
                st.session_state.messages.append({"role": "user", "content": f"📄 Text file:\n\n{content[:1500]}..."})
                st.rerun()

            elif file_type == "application/pdf":
                reader = PdfReader(uploaded_file)
                text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
                st.session_state.messages.append({"role": "user", "content": f"📄 PDF:\n\n{text[:1500]}..."})
                st.rerun()

            elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc = Document(uploaded_file)
                full_text = "\n".join([p.text for p in doc.paragraphs])
                st.session_state.messages.append({"role": "user", "content": f"📄 DOCX:\n\n{full_text[:1500]}..."})
                st.rerun()

            else:
                st.warning("Unsupported file type.")


def render_bubble(msg):
    if msg["role"] == "user":
        color = "#99CCFF"
        justify = "flex-end"
        text_align = "right"
    else:
        color = "#DDEEFF"
        justify = "flex-start"
        text_align = "left"

    return f"""
        <div style='
            display: flex;
            justify-content: {justify};
            margin: 5px 0;
        '>
            <div style='
                background-color: {color};
                padding: 10px 14px;
                border-radius: 12px;
                max-width: 80%;
                word-wrap: break-word;
                overflow-wrap: break-word;
                box-shadow: 0 1px 2px rgba(0,0,0,0.05);
                text-align: {text_align};
            '>
                {msg["content"]}
            </div>
        </div>
    """