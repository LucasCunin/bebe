from database.operations import proposition_operations, vote_operations
from database.database import SessionLocal
import streamlit as st
import pandas as pd
# Importer tous les modèles pour que SQLAlchemy les connaisse
from database.models import user, proposition, vote, config

st.set_page_config(page_title="À vos votes !", page_icon="🗳️")
st.title("🗳️ C'est l'heure de voter !")
st.write("Quel prénom préférez-vous ? Chaque voix compte !")

db = SessionLocal()

if not st.session_state.get("user"):
    st.warning("Veuillez vous connecter pour voter.")
    st.stop()

user = st.session_state.user
st.info(f"Il vous reste {user['votes_left']} vote(s).")
if user['is_admin']:
    st.info("En tant que parent, votre vote compte double ! 👨‍👩‍👧‍👦")

propositions = proposition_operations.get_all_propositions(db)

if not propositions:
    st.info("Aucun prénom n'a été proposé pour le moment.")
    st.stop()

# --- Affichage des scores ---
rows = []
for prop in propositions:
    counts = vote_operations.get_vote_counts_for_proposition(db, prop.id)
    total_score = counts['normal_votes'] + (counts['admin_votes'] * 2)
    rows.append({
        "Prénom": prop.name,
        "Score": total_score,
        "Votes Normaux": counts['normal_votes'],
        "Vote Parent": counts['admin_votes'],
    })

df = pd.DataFrame(rows).sort_values("Score", ascending=False)
st.dataframe(df, use_container_width=True, hide_index=True)


# --- Section de vote ---
st.header("Votez pour votre prénom préféré")

for prop in propositions:
    col1, col2 = st.columns([3, 1])
    col1.write(f"**{prop.name}**")

    existing_vote = vote_operations.get_user_vote_for_proposition(db, user_id=user['id'], proposition_id=prop.id)
    
    if existing_vote:
        if col2.button("Annuler", key=f"cancel_{prop.id}"):
            if vote_operations.cancel_vote(db, existing_vote.id):
                st.success("Vote annulé !")
                st.session_state.user['votes_left'] += 1
                st.rerun()
    elif user['votes_left'] > 0:
        if col2.button("Voter", key=f"vote_{prop.id}"):
            vote = vote_operations.create_vote(db, user_id=user['id'], proposition_id=prop.id)
            if vote:
                st.success(f"Vous avez voté pour {prop.name} !")
                st.session_state.user['votes_left'] -= 1
                st.rerun()
            else:
                st.error("Une erreur est survenue.")
    else:
        col2.empty() # Placeholder

db.close()
