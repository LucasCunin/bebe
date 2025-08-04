import streamlit as st
import sys
import os

# Ajouter la racine du projet au sys.path pour les imports absolus
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from streamlit_autorefresh import st_autorefresh
from streamlit_extras.encrypted_cookie import EncryptedCookieManager
from database.database import Base, engine, SessionLocal
from database.operations import user_operations
# Importer tous les modèles pour que Base les connaisse
from database.models import user, proposition, vote, config

# Clé de chiffrement pour les cookies. Changez-la pour votre projet.
# Le mot de passe de la DB est une bonne source d'inspiration.
COOKIE_ENCRYPTION_KEY = "LAfermeestjaunepisse_pour_les_cookies"

def attempt_login_from_cookie(cookies):
    """Tente de connecter l'utilisateur si un cookie valide est trouvé."""
    if 'user' in st.session_state and st.session_state.user:
        return # Déjà connecté, on ne fait rien

    pseudo = cookies.get('user_pseudo')
    if not pseudo:
        return # Pas de cookie, on ne fait rien

    db = SessionLocal()
    try:
        user_in_db = user_operations.get_user_by_pseudo(db, pseudo)
        if user_in_db:
            st.session_state.user = {
                "id": user_in_db.id,
                "pseudo": user_in_db.pseudo,
                "is_admin": user_in_db.is_admin,
                "proposals_left": user_in_db.proposals_left,
                "votes_left": user_in_db.votes_left,
            }
    finally:
        db.close()

def sync_user_session():
    """Vérifie si l'état de l'utilisateur a changé en DB et met à jour la session."""
    if 'user' not in st.session_state or st.session_state.user is None:
        return
    
    db = SessionLocal()
    try:
        current_user_in_db = user_operations.get_user_by_id(db, st.session_state.user['id'])
        if not current_user_in_db:
            # L'utilisateur a été supprimé, on le déconnecte
            st.session_state.user = None
            return

        # On compare les infos clés et on met à jour si besoin
        if (st.session_state.user['is_admin'] != current_user_in_db.is_admin or
            st.session_state.user['votes_left'] != current_user_in_db.votes_left or
            st.session_state.user['proposals_left'] != current_user_in_db.proposals_left):
            
            st.session_state.user = {
                "id": current_user_in_db.id,
                "pseudo": current_user_in_db.pseudo,
                "is_admin": current_user_in_db.is_admin,
                "proposals_left": current_user_in_db.proposals_left,
                "votes_left": current_user_in_db.votes_left,
            }
            # Pas besoin de rerun ici, le simple fait de changer le state
            # et le rafraîchissement global suffisent.
    finally:
        db.close()


def main():
    # Créer les tables dans la base de données si elles n'existent pas
    Base.metadata.create_all(bind=engine)
    
    # Initialiser le gestionnaire de cookies
    cookies = EncryptedCookieManager(key=COOKIE_ENCRYPTION_KEY)

    # Tenter de se connecter via le cookie AVANT toute autre chose
    attempt_login_from_cookie(cookies)

    # Rafraîchit l'application toutes les 15 secondes
    st_autorefresh(interval=15 * 1000, key="datarefresh")

    st.set_page_config(
        page_title="Vote pour le Prénom !",
        page_icon="🫏",
        layout="centered",
        initial_sidebar_state="expanded",
    )

    st.title("🫏 Bienvenue !")

    st.info("Utilisez le menu à gauche pour participer. 🎉")

    # Synchroniser la session avec la DB à chaque re-exécution
    sync_user_session()

    if 'user' not in st.session_state:
        st.session_state.user = None
    
    if st.session_state.user:
        st.sidebar.success(f"Connecté en tant que : {st.session_state.user['pseudo']}")
        if st.session_state.user['is_admin']:
            st.sidebar.info("Statut : Parent 👑")
    else:
        st.sidebar.warning("Vous n'êtes pas connecté.")


if __name__ == "__main__":
    main()
