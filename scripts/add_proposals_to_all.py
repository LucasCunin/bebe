import sys
import os
import argparse
from sqlalchemy.orm import Session

# Configuration du path pour les imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from database.database import SessionLocal
from database.operations import user_operations
# Importer tous les modèles pour que SQLAlchemy les connaisse
from database.models import user, proposition, vote, config

def main():
    """
    Script pour ajouter un nombre donné de propositions à tous les utilisateurs.
    """
    parser = argparse.ArgumentParser(description="Ajoute des propositions à tous les utilisateurs.")
    parser.add_argument("amount", type=int, help="Le nombre de propositions à ajouter à chaque utilisateur.")
    
    args = parser.parse_args()
    
    if args.amount <= 0:
        print("Erreur : Le nombre de propositions à ajouter doit être positif.")
        return

    db = SessionLocal()
    
    try:
        users = user_operations.get_all_users(db)
        if not users:
            print("Il n'y a aucun utilisateur dans la base de données.")
            return

        print(f"Ajout de {args.amount} proposition(s) à {len(users)} utilisateur(s)...")

        for u in users:
            u.proposals_left += args.amount
        
        db.commit()
        print("Opération terminée avec succès !")

    except Exception as e:
        print(f"Une erreur est survenue : {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
