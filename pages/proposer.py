import streamlit as st
from database.operations import proposition_operations
from database.database import SessionLocal
# Importer tous les modèles pour que SQLAlchemy les connaisse
from database.models import user, proposition, vote, config

st.set_page_config(page_title="Boîte à idées", page_icon="💡")
st.title("💡 La Boîte à Idées")
st.write("Vous avez une idée de génie ? Partagez-la ici !")

db = SessionLocal()

if not st.session_state.get("user"):
    st.warning("Veuillez vous connecter pour proposer un prénom.")
    st.stop()

user = st.session_state.user
st.info(f"Il vous reste {user['proposals_left']} proposition(s).")

with st.form("proposal_form"):
    new_name = st.text_input("Nouveau prénom à proposer :")
    submitted = st.form_submit_button("Proposer")

    if submitted:
        # On nettoie les espaces avant et après la chaîne
        clean_name = new_name.strip() if new_name else ""
        
        if clean_name:
            if proposition_operations.get_proposition_by_name(db, clean_name):
                st.error("Ce prénom a déjà été proposé.")
            else:
                proposition = proposition_operations.create_proposition(db, name=clean_name, proposer_id=user['id'])
                if proposition:
                    st.success(f"Le prénom '{clean_name}' a été ajouté !")
                    st.session_state.user['proposals_left'] -= 1
                    st.rerun()
                else:
                    st.error("Vous n'avez plus de propositions disponibles.")
        else:
            st.warning("Veuillez entrer un prénom.")

st.header("Prénoms déjà proposés :")
propositions = proposition_operations.get_all_propositions(db)
for prop in propositions:
    st.write(f"- {prop.name} (proposé par {prop.proposer.pseudo})")

db.close()
