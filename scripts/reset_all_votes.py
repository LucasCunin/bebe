import sys
import os
from sqlalchemy.orm import Session

# Configuration du path pour les imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from database.database import SessionLocal
from database.models import vote as vote_model, user as user_model
from database.operations import config_operations

from dotenv import load_dotenv

def main():
    """
    Ce script supprime tous les votes existants et réinitialise le compteur
    de votes de chaque utilisateur à la valeur définie dans la configuration.
    """
    load_dotenv()
    db = SessionLocal()
    
    print("Ce script va supprimer TOUS les votes et réinitialiser les compteurs des utilisateurs.")
    confirm = input("Êtes-vous sûr de vouloir continuer ? (oui/non): ")
    
    if confirm.lower() != 'oui':
        print("Opération annulée.")
        db.close()
        return
        
    try:
        # 1. Supprimer tous les votes
        num_deleted = db.query(vote_model.Vote).delete()
        print(f"{num_deleted} vote(s) supprimé(s).")
        
        # 2. Récupérer le nombre de votes par défaut
        default_votes = config_operations.get_config_value(db, "DEFAULT_VOTES", 5)
        print(f"Le nombre de votes par défaut est de {default_votes}.")
        
        # 3. Mettre à jour tous les utilisateurs
        users = db.query(user_model.User).all()
        for user in users:
            user.votes_left = default_votes
        
        db.commit()
        print("Tous les compteurs de votes des utilisateurs ont été réinitialisés.")
        print("Opération terminée avec succès.")
        
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
