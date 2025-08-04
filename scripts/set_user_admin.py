import sys
import os
import argparse

# Ajouter le chemin racine du projet au sys.path
# pour permettre les imports relatifs (database.database, etc.)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from database.database import SessionLocal
from database.operations import user_operations
# Importer tous les modèles pour que SQLAlchemy les connaisse
from database.models import user, proposition, vote, config

def main(pseudo: str):
    """
    Script pour promouvoir un utilisateur au statut d'administrateur.
    """
    db = SessionLocal()
    print(f"Recherche de l'utilisateur '{pseudo}'...")
    
    user = user_operations.get_user_by_pseudo(db, pseudo)
    
    if not user:
        print(f"Erreur : Utilisateur '{pseudo}' non trouvé.")
        db.close()
        return

    if user.is_admin:
        print(f"Info : L'utilisateur '{pseudo}' est déjà administrateur.")
    else:
        print(f"Promotion de l'utilisateur '{pseudo}' au rang d'administrateur...")
        user_operations.set_admin(db, user.id)
        print("Opération réussie ! Les votes précédents de l'utilisateur comptent maintenant double.")
        
    db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Passe un utilisateur en administrateur.")
    parser.add_argument("pseudo", type=str, help="Le pseudo de l'utilisateur à promouvoir.")
    
    args = parser.parse_args()
    main(args.pseudo)
