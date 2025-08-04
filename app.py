import streamlit as st
import sys
import os

# Ajouter la racine du projet au sys.path pour les imports absolus
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from streamlit_autorefresh import st_autorefresh
from database.database import Base, engine, SessionLocal
from database.operations import user_operations
# Importer tous les modèles pour que Base les connaisse
from database.models import user, proposition, vote, config

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
    finally:
        db.close()


def main():
    # Créer les tables dans la base de données si elles n'existent pas
    Base.metadata.create_all(bind=engine)

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
