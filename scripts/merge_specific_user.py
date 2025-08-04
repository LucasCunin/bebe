import sys
import os
from dotenv import load_dotenv
from collections import defaultdict
import argparse

# --- Configuration du Path et de l'environnement ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
load_dotenv(os.path.join(project_root, '.env'))

# --- Imports de l'application ---
from database.database import SessionLocal
from database.models import user as user_model, vote as vote_model, proposition as prop_model
from sqlalchemy.orm import Session
from sqlalchemy import func

def merge_users(db: Session, original_user: user_model.User, duplicate_user: user_model.User):
    """Fusionne un utilisateur doublon dans l'utilisateur original."""
    print(f"  -> Fusion de l'ID {duplicate_user.id} ('{duplicate_user.pseudo}') dans l'ID {original_user.id} ('{original_user.pseudo}')...")
    
    # --- Fusion des quotas ---
    original_user.proposals_left += duplicate_user.proposals_left
    original_user.votes_left += duplicate_user.votes_left
    print(f"     - Quotas ajoutés. Total votes: {original_user.votes_left}, Total propositions: {original_user.proposals_left}.")

    # --- Ré-attribution des votes ---
    votes_to_move = db.query(vote_model.Vote).filter(vote_model.Vote.user_id == duplicate_user.id).all()
    for vote in votes_to_move:
        # Si l'original a déjà voté pour cette proposition, on ignore le vote du doublon.
        existing_vote = db.query(vote_model.Vote).filter_by(user_id=original_user.id, proposition_id=vote.proposition_id).first()
        if not existing_vote:
            vote.user_id = original_user.id
    
    # --- Ré-attribution des propositions ---
    db.query(prop_model.Proposition).filter(prop_model.Proposition.proposer_id == duplicate_user.id).update({"proposer_id": original_user.id})
    
    # --- Suppression de l'utilisateur doublon ---
    db.delete(duplicate_user)
    print(f"     - Utilisateur doublon (ID: {duplicate_user.id}) marqué pour suppression.")

def main():
    parser = argparse.ArgumentParser(description="Fusionne tous les comptes utilisateurs en double pour un pseudo donné.")
    parser.add_argument("correct_pseudo", type=str, help="Le pseudo correct (nettoyé) à conserver.")
    
    args = parser.parse_args()
    db = SessionLocal()
    
    try:
        clean_pseudo = args.correct_pseudo.strip().lower()
        print(f"Recherche des comptes correspondants à '{clean_pseudo}'...")
        
        users_found = db.query(user_model.User).filter(func.lower(func.trim(user_model.User.pseudo)) == clean_pseudo).order_by(user_model.User.id).all()
        
        if len(users_found) <= 1:
            print("✅ Aucun doublon trouvé pour ce pseudo. Aucune action n'est nécessaire.")
            return

        original_user = users_found[0]
        duplicates = users_found[1:]
        
        print(f"\n{len(duplicates)} doublon(s) trouvé(s) pour le pseudo '{clean_pseudo}'.")
        print(f"Le compte original à conserver est l'ID {original_user.id} (pseudo: '{original_user.pseudo}').")
        print("Les comptes suivants seront fusionnés et supprimés :")
        for dup in duplicates:
            print(f"  - ID: {dup.id}, Pseudo: '{dup.pseudo}', Votes: {dup.votes_left}, Props: {dup.proposals_left}")

        confirm = input("\nVoulez-vous procéder à cette fusion ? (oui/non): ")
        if confirm.lower() != 'oui':
            print("Opération annulée.")
            return

        print("\n--- Lancement de la fusion ---")
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
