import sys
import os
from dotenv import load_dotenv
from collections import defaultdict

# --- Configuration du Path et de l'environnement ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
load_dotenv(os.path.join(project_root, '.env'))

from database.database import SessionLocal
from database.models import user as user_model, vote as vote_model, proposition as prop_model
from sqlalchemy.orm import Session

def merge_users(db: Session, original_user: user_model.User, duplicate_user: user_model.User):
    """Fusionne un utilisateur doublon dans l'utilisateur original."""
    print(f"  -> Fusion de l'utilisateur ID {duplicate_user.id} ('{duplicate_user.pseudo}') dans l'ID {original_user.id} ('{original_user.pseudo}')...")
    
    # --- Ré-attribution des votes ---
    votes_to_move = db.query(vote_model.Vote).filter(vote_model.Vote.user_id == duplicate_user.id).all()
    moved_votes = 0
    deleted_votes = 0
    for vote in votes_to_move:
        # Vérifier si l'original a déjà voté pour cette proposition
        existing_vote = db.query(vote_model.Vote).filter(
            vote_model.Vote.user_id == original_user.id,
            vote_model.Vote.proposition_id == vote.proposition_id
        ).first()
        
        if existing_vote:
            # Conflit : l'original a déjà voté. On supprime le vote du doublon.
            db.delete(vote)
            deleted_votes += 1
        else:
            # Pas de conflit : on déplace le vote.
            vote.user_id = original_user.id
            moved_votes += 1
    
    if moved_votes > 0: print(f"     - {moved_votes} vote(s) transféré(s).")
    if deleted_votes > 0: print(f"     - {deleted_votes} vote(s) en conflit supprimé(s).")

    # --- Ré-attribution des propositions ---
    propositions_to_move = db.query(prop_model.Proposition).filter(prop_model.Proposition.proposer_id == duplicate_user.id).all()
    moved_props = 0
    for prop in propositions_to_move:
        prop.proposer_id = original_user.id
        moved_props += 1
    
    if moved_props > 0: print(f"     - {moved_props} proposition(s) transférée(s).")

    # --- Suppression de l'utilisateur doublon ---
    db.delete(duplicate_user)
    print(f"     - Utilisateur doublon (ID: {duplicate_user.id}) supprimé.")


def main():
    """
    Script pour trouver et fusionner les comptes utilisateurs en double
    (basé sur le pseudo une fois nettoyé et mis en minuscules).
    """
    db = SessionLocal()
    
    try:
        print("Recherche de comptes utilisateurs en double...")
        all_users = db.query(user_model.User).all()
        
        users_by_clean_pseudo = defaultdict(list)
        for user in all_users:
            clean_pseudo = user.pseudo.strip().lower()
            users_by_clean_pseudo[clean_pseudo].append(user)
            
        duplicate_groups = {pseudo: users for pseudo, users in users_by_clean_pseudo.items() if len(users) > 1}
        
        if not duplicate_groups:
            print("✅ Aucun compte en double trouvé. Tout est propre !")
            return

        print(f"\nAttention : {len(duplicate_groups)} groupe(s) de doublons trouvé(s).")
        for pseudo, users in duplicate_groups.items():
            ids = sorted([u.id for u in users])
            print(f"- Pseudo '{pseudo}': trouvé pour les IDs {ids}. L'ID {ids[0]} sera conservé.")

        confirm = input("\nVoulez-vous procéder à la fusion de ces comptes ? (oui/non): ")
        if confirm.lower() != 'oui':
            print("Opération annulée.")
            return

        print("\n--- Lancement de la fusion ---")
        for pseudo, users in duplicate_groups.items():
            # Trier par ID pour identifier l'original (le plus ancien)
            sorted_users = sorted(users, key=lambda u: u.id)
            original_user = sorted_users[0]
            duplicates = sorted_users[1:]
            
            for duplicate in duplicates:
                merge_users(db, original_user, duplicate)
        
        db.commit()
        print("\n✅ Fusion terminée avec succès !")

    except Exception as e:
        print(f"\n❌ Une erreur est survenue : {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
