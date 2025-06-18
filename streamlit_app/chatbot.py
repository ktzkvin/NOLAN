import streamlit as st
import json
import requests
import asyncio
from PyPDF2 import PdfReader
from docx import Document
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.chat_history import save_conversation, load_conversations, delete_conversation
from services.rag_engine import call_openai

def generate_title(prompt):
    try:
        title_prompt = (
            f"Donne-moi un titre très concis (3 à 4 mots max), "
            f"pas de 'Résumé de conversation' ou autre préfixe, tu dois juster donner un titre résumant une prompt"
            f"donc sans préfixe, résume cette conversation : {prompt}"
        )
        title = asyncio.run(call_openai(title_prompt)).strip().strip('"')
        if ":" in title:
            title = title.split(":", 1)[-1].strip()
        return " ".join(title.split()[:4]) or "Untitled Conversation"
    except Exception:
        return "Untitled Conversation"

def render_bubble(msg):
    if msg["role"] == "user":
        color, justify, ta = "#99CCFF", "flex-end", "right"
    else:
        color, justify, ta = "#DDEEFF", "flex-start", "left"
    return (
        "<div style='display:flex;justify-content:" + justify + ";margin:5px 0;'>"
        "<div style='background:" + color + ";padding:10px;border-radius:12px;"
        "max-width:80%;word-wrap:break-word;overflow-wrap:break-word;"
        "text-align:" + ta + ";box-shadow:0 1px 2px rgba(0,0,0,0.05);'>"
        + msg["content"] +
        "</div></div>"
    )

def render_loader_bubble():
    return """
    <div style='display:flex;justify-content:flex-start;margin:5px 0;'>
      <div style='background:#DDEEFF;padding:10px 14px;border-radius:12px;
                  max-width:80%;text-align:left;box-shadow:0 1px 2px rgba(0,0,0,0.05);'>
        <div class='typing-indicator'>
            <span></span><span></span><span></span>
        </div>
      </div>
    </div>
    """

def display():
    # Injection du CSS global pour l'animation
    st.markdown("""
    <style>
    .typing-indicator {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        height: 20px;
        padding-left: 2px;
    }
    .typing-indicator span {
        display: inline-block;
        width: 8px;
        height: 8px;
        margin: 0 2px;
        background-color: #666;
        border-radius: 50%;
        animation: bounce 1.2s infinite ease-in-out;
    }
    .typing-indicator span:nth-child(1) { animation-delay: 0s; }
    .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
    .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes bounce {
        0%, 80%, 100% { transform: scale(0.6); opacity: 0.3; }
        40% { transform: scale(1.0); opacity: 1; }
    }
    </style>
    """, unsafe_allow_html=True)

    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []

    history = load_conversations(st.session_state.username)

    st.sidebar.title("Conversations")
    if history:
        for convo in history:
            is_active = convo["id"] == st.session_state.conversation_id
            title = convo.get("title", "Untitled Conversation")
            label = f"👉 {title}" if is_active else title

            col1, col2 = st.sidebar.columns([5, 1])
            if col1.button(label, key=convo["id"]):
                st.session_state.conversation_id = convo["id"]
                st.session_state.messages = convo["messages"]
                st.rerun()

            if col2.button("🗑️", key="del_" + convo["id"]):
                delete_conversation(convo["id"])
                if is_active:
                    st.session_state.conversation_id = None
                    st.session_state.messages = []
                st.rerun()
    else:
        st.sidebar.info("Aucune conversation enregistree.")

    if st.sidebar.button("Nouvelle conversation"):
        st.session_state.conversation_id = None
        st.session_state.messages = []
        st.rerun()

    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.markdown(
            f"<h3 style='text-align:center;'>Bievenue {st.session_state.username} ! Comment puis-je vous aider ?</h3>",
            unsafe_allow_html=True
        )

        with st.container():
            with st.form("chat_form", clear_on_submit=True):
                messages_to_display = st.session_state.messages[-500:]
                for msg in messages_to_display:
                    st.markdown(render_bubble(msg), unsafe_allow_html=True)

                uploaded_file = st.file_uploader("Submit a document", type=["txt", "pdf", "docx"])
                user_input = st.text_input("Your message :", placeholder="Start to say something...")
                submitted = st.form_submit_button("Send")

        if submitted and user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.messages.append({"role": "assistant", "content": render_loader_bubble()})
            st.rerun()

        if st.session_state.messages and "typing-indicator" in st.session_state.messages[-1]["content"]:
            user_msg = next((m["content"] for m in reversed(st.session_state.messages[:-1]) if m["role"] == "user"),"")

            try:
                resp = requests.post(
                    "http://127.0.0.1:8000/orchestrate/",
                    headers={"Content-Type": "application/json"},
                    data=json.dumps({"prompt": user_msg})
                )
                if resp.status_code == 200:
                    assistant_reply = resp.json().get("response", "No response")
                else:
                    assistant_reply = f"Error {resp.status_code}"
            except Exception as e:
                assistant_reply = f"Request failed: {e}"

            st.session_state.messages[-1] = {"role": "assistant", "content": assistant_reply}

            if st.session_state.conversation_id is None:
                title = generate_title(assistant_reply)
                cid = save_conversation(
                    st.session_state.username,
                    st.session_state.messages,
                    title=title
                )
                st.session_state.conversation_id = cid
            else:
                save_conversation(
                    st.session_state.username,
                    st.session_state.messages,
                    conversation_id=st.session_state.conversation_id
                )

            st.rerun()

        if uploaded_file is not None:
            ft = uploaded_file.type
            if ft == "text/plain":
                text = uploaded_file.read().decode("utf-8")
            elif ft == "application/pdf":
                reader = PdfReader(uploaded_file)
                text = "".join([p.extract_text() or "" for p in reader.pages])
            elif ft == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc = Document(uploaded_file)
                text = "\n".join([p.text for p in doc.paragraphs])
            else:
                st.warning("Unsupported file type.")
                return

            st.session_state.messages.append(
                {"role": "user", "content": text[:1500] + "..."}
            )
            st.rerun()
