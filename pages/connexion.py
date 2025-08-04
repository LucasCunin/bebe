import streamlit as st
from database.operations import user_operations
from database.database import SessionLocal
# Importer tous les modèles pour que SQLAlchemy les connaisse
from database.models import user, proposition, vote, config

st.set_page_config(page_title="Qui est-ce ?", page_icon="👋")
st.title("👋 Qui êtes-vous ?")
st.write("Dites-nous qui vous êtes pour participer à la fête !")

db = SessionLocal()

def login_or_register(pseudo: str):
    """Connecte un utilisateur ou en crée un s'il n'existe pas."""
    user = user_operations.get_user_by_pseudo(db, pseudo)
    
    if not user:
        st.info("Ce pseudo n'existe pas, nous allons en créer un pour vous.")
        user = user_operations.create_user(db, pseudo)
        st.success(f"Compte pour '{user.pseudo}' créé avec succès !")

    st.session_state.user = {
        "id": user.id,
        "pseudo": user.pseudo,
        "is_admin": user.is_admin,
        "proposals_left": user.proposals_left,
        "votes_left": user.votes_left,
    }
    
    st.success(f"Bienvenue, {user.pseudo} !")
    st.rerun()

# --- Affichage de la page ---

if st.session_state.get("user"):
    st.write(f"Vous êtes déjà connecté en tant que **{st.session_state.user['pseudo']}**.")
    if st.button("Se déconnecter"):
        st.session_state.user = None
        st.rerun()
else:
    with st.form("login_form"):
        pseudo = st.text_input("Entrez votre pseudo", help="Si le pseudo n'existe pas, un compte sera créé.")
        submitted = st.form_submit_button("Valider")
        
        if submitted:
            clean_pseudo = pseudo.strip() if pseudo else ""
            if clean_pseudo:
                login_or_register(clean_pseudo)
            else:
                st.warning("Veuillez entrer un pseudo.")

db.close()
