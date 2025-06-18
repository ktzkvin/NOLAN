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

def generate_title(response: str) -> str:
    try:
        title_prompt = f"Donne-moi un titre très concis (3 à 4 mots max), sans préfixe, résumant la première réponse de l'assistant : {response}"
        title = asyncio.run(call_openai(title_prompt)).strip().strip('"')
        if ":" in title:
            title = title.split(":", 1)[1].strip()
        return " ".join(title.split()[:4]) or "Untitled Conversation"
    except Exception:
        return "Untitled Conversation"

def render_bubble(msg: dict) -> str:
    if msg["role"] == "user":
        background = "background: radial-gradient(circle, rgba(206,223,245,1) 0%, rgba(171,206,237,1) 89%);"
        justify = "flex-end"
        text_color = "#000000"
    else:
        background = "background: radial-gradient(circle, rgba(36,103,171,1) 0%, rgba(14,71,128,1) 89%);"
        justify = "flex-start"
        text_color = "#ffffff"
    return f"""
        <div style='display: flex; justify-content: {justify}; margin: 5px 0;'>
            <div style='{background} padding: 10px 14px; border-radius: 12px; max-width: 80%; word-wrap: break-word; overflow-wrap: break-word; box-shadow: 0 1px 2px rgba(0,0,0,0.05); text-align: left; color: {text_color};'>
                {msg["content"]}
            </div>
        </div>
    """

def render_loader_bubble() -> str:
    return """
    <div style='display:flex;justify-content:flex-start;margin:5px 0;'>
      <div style='background:#2467ab;padding:10px 14px;border-radius:12px;
                  max-width:80%;text-align:left;box-shadow:0 1px 2px rgba(0,0,0,0.05);'>
        <div style="display: flex; gap: 6px;">
          <span style="width: 8px; height: 8px; background: white; border-radius: 50%; animation: bounce 1.2s infinite ease-in-out;"></span>
          <span style="width: 8px; height: 8px; background: white; border-radius: 50%; animation: bounce 1.2s infinite ease-in-out; animation-delay: 0.2s;"></span>
          <span style="width: 8px; height: 8px; background: white; border-radius: 50%; animation: bounce 1.2s infinite ease-in-out; animation-delay: 0.4s;"></span>
        </div>
      </div>
    </div>
    <style>
    @keyframes bounce {
        0%, 80%, 100% { transform: scale(0.6); opacity: 0.3; }
        40% { transform: scale(1.0); opacity: 1; }
    }
    </style>
    """

def display():
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
            with st.sidebar.container():
                st.markdown(f"""
                    <div style="display:flex;align-items:center;justify-content:space-between;
                                background:#f3f6fa;border-radius:8px;padding:8px 12px;margin-bottom:8px;
                                box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                        <form action="#" method="post">
                            <button type="submit" name="select_{convo['id']}" style="
                                all: unset;
                                font-weight: 500;
                                color: #333;
                                max-width: 150px;
                                white-space: nowrap;
                                overflow: hidden;
                                text-overflow: ellipsis;
                                cursor: pointer;">
                                {label}
                            </button>
                        </form>
                        <form action="#" method="post">
                            <button type="submit" name="del_{convo['id']}" style="
                                all: unset;
                                color: #c00;
                                font-size: 16px;
                                cursor: pointer;">🗑️</button>
                        </form>
                    </div>
                """, unsafe_allow_html=True)

                if st.session_state.get(f"select_{convo['id']}"):
                    st.session_state.conversation_id = convo["id"]
                    st.session_state.messages = convo["messages"]
                    st.rerun()

                if st.session_state.get(f"del_{convo['id']}"):
                    delete_conversation(convo["id"])
                    if convo["id"] == st.session_state.conversation_id:
                        st.session_state.conversation_id = None
                        st.session_state.messages = []
                    st.rerun()
    else:
        st.sidebar.info("Aucune conversation enregistrée.")

    if st.sidebar.button("Nouvelle conversation"):
        st.session_state.conversation_id = None
        st.session_state.messages = []
        st.rerun()

    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.markdown(f"""
            <h3 style='text-align:center; font-family:"Dancing Script", Helvetica, serif; font-size:1.7rem; font-style:italic; color:#001f3f;'>
                Bienvenue {st.session_state.username} ! Comment puis-je vous aider ?
            </h3>
        """, unsafe_allow_html=True)

        with st.form("chat_form", clear_on_submit=True):
            for msg in st.session_state.messages[-500:]:
                if msg["content"] == "__LOADER__":
                    st.markdown(render_loader_bubble(), unsafe_allow_html=True)
                else:
                    st.markdown(render_bubble(msg), unsafe_allow_html=True)

            uploaded_file = st.file_uploader("📄 Joindre un doc.", type=["txt", "pdf", "docx"], label_visibility="visible")
            user_input = st.text_input("Votre message :", placeholder="J'ai besoin d'aide pour...", label_visibility="visible")
            submitted = st.form_submit_button("➤")

    if submitted and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "assistant", "content": "__LOADER__"})
        st.rerun()

    if st.session_state.messages and "typing-indicator" in st.session_state.messages[-1]["content"]:
        user_msg = next((m["content"] for m in reversed(st.session_state.messages[:-1]) if m["role"] == "user"), "")
        try:
            resp = requests.post(
                "http://127.0.0.1:8000/orchestrate/",
                headers={"Content-Type": "application/json"},
                data=json.dumps({"prompt": user_msg})
            )
            assistant_reply = resp.json().get("response", "No response") if resp.status_code == 200 else f"Error {resp.status_code}"
        except Exception as e:
            assistant_reply = f"Request failed: {e}"

        st.session_state.messages[-1] = {"role": "assistant", "content": assistant_reply}

        if st.session_state.conversation_id is None:
            cid = save_conversation(st.session_state.username, st.session_state.messages, title=generate_title(assistant_reply))
            st.session_state.conversation_id = cid
        else:
            save_conversation(st.session_state.username, st.session_state.messages, conversation_id=st.session_state.conversation_id)

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
        st.session_state.messages.append({"role": "user", "content": text[:1500] + "..."})
        st.rerun()
