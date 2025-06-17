<<<<<<< Updated upstream
import streamlit as st

st.set_page_config(page_title="N.O.L.A.N. – Assistant RH", layout="centered")

# --- CSS pour un look plus clean ---
st.markdown("""
    <style>
    html, body {
        background-color: #f9f9f9;
    }
    .message {
        border-radius: 12px;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 85%;
        line-height: 1.5;
    }
    .user {
        background-color: #e1f0ff;
        align-self: flex-end;
        text-align: right;
    }
    .bot {
        background-color: #ffffff;
        border: 1px solid #ddd;
    }
    .chat-container {
        display: flex;
        flex-direction: column;
    }
    .input-box input {
        width: 100%;
        padding: 12px;
        font-size: 16px;
    }
    .stButton > button {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        background-color: #1a73e8;
        color: white;
        border: none;
        font-weight: 500;
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- Titre principal ---
st.markdown("<h1 style='text-align: center;'>N.O.L.A.N. – Assistant RH intelligent</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Posez vos questions RH, je vous réponds avec précision.</p>", unsafe_allow_html=True)

# --- Simuler l'historique de conversation ---
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Exemple d'historique
st.markdown('<div class="message user">Est-ce que je peux poser des congés la première semaine d’août ?</div>', unsafe_allow_html=True)
st.markdown('<div class="message bot">Oui, à condition de respecter un délai de prévenance d’au moins un mois. Souhaitez-vous que je vous indique la procédure ?</div>', unsafe_allow_html=True)
st.markdown('<div class="message user">Oui merci.</div>', unsafe_allow_html=True)
st.markdown('<div class="message bot">Vous pouvez formuler la demande via le portail RH en sélectionnant “Congé payé”, puis choisir vos dates. Un accusé de réception sera généré automatiquement.</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- Formulaire d'envoi ---
with st.form("ask_form", clear_on_submit=True):
    user_input = st.text_input("Posez votre question ici :", placeholder="Ex : Puis-je reporter mes RTT après août ?")
    submitted = st.form_submit_button("Envoyer")

# --- Réponse factice pour la démo ---
if submitted and user_input:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.markdown(f'<div class="message user">{user_input}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="message bot">Je traite votre demande... (réponse à venir)</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Bas de page ---
st.markdown("---")
st.markdown('<p style="text-align: center; color: #999;">N.O.L.A.N. © 2025 – Hackathon EFREI x Finelog</p>', unsafe_allow_html=True)
=======
from fastapi import FastAPI
from orchestrator import router

app = FastAPI(title="NOLAN Orchestrator")
app.include_router(router.router, prefix="/orchestrate")
>>>>>>> Stashed changes
