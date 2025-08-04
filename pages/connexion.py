import streamlit as st
from database.operations import user_operations
from database.database import SessionLocal
# Importer tous les modèles pour que SQLAlchemy les connaisse
from database.models import user, proposition, vote, config

from streamlit_extras.encrypted_cookie import EncryptedCookieManager

# Clé de chiffrement, doit être la même que dans app.py
COOKIE_ENCRYPTION_KEY = "LAfermeestjaunepisse_pour_les_cookies"

st.set_page_config(page_title="Qui est-ce ?", page_icon="👋")
st.title("👋 Qui êtes-vous ?")
st.write("Dites-nous qui vous êtes pour participer à la fête !")

# Initialiser le gestionnaire de cookies
cookies = EncryptedCookieManager(
    key=COOKIE_ENCRYPTION_KEY,
    # Le préfixe est nécessaire pour Streamlit Cloud
    prefix="streamlit_cookies_manager/",
)

if not cookies.is_ready():
    # Attendre que le navigateur renvoie les cookies
    st.stop()

db = SessionLocal()

def login_or_register(pseudo: str):
    """Connecte un utilisateur, crée un compte et dépose un cookie."""
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
    
    # Déposer le cookie avec une date d'expiration (ex: 30 jours)
    cookies['user_pseudo'] = user.pseudo
    
    st.success(f"Bienvenue, {user.pseudo} !")
    st.rerun()

# --- Affichage de la page ---

if st.session_state.get("user"):
    st.write(f"Vous êtes déjà connecté en tant que **{st.session_state.user['pseudo']}**.")
    if st.button("Se déconnecter"):
        # Supprimer le cookie
        del cookies['user_pseudo']
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
