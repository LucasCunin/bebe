import sys
import os
import argparse
from dotenv import load_dotenv

# Charger l'environnement AVANT tout autre import de notre application
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
load_dotenv(os.path.join(project_root, '.env'))

# Maintenant que l'environnement est chargé, on peut importer sans risque
from database.database import SessionLocal
from database.operations import user_operations
from database.models import user as user_model, proposition, vote, config
from sqlalchemy import func

def promote_user(db_session, user_to_promote):
    """Factorisation de la logique de promotion."""
    if user_to_promote.is_admin:
        print(f"Info : L'utilisateur '{user_to_promote.pseudo}' (ID: {user_to_promote.id}) est déjà un Parent.")
    else:
        print(f"Promotion de l'utilisateur '{user_to_promote.pseudo}' (ID: {user_to_promote.id}) au rang de Parent...")
        user_operations.set_admin(db_session, user_to_promote.id)
        print("✅ Opération réussie ! Ses votes précédents comptent maintenant double.")

def main():
    parser = argparse.ArgumentParser(description="Passe un utilisateur au statut de Parent (admin). Peut chercher par pseudo partiel ou par ID.")
    parser.add_argument("identifier", type=str, help="Un morceau du pseudo ou l'ID numérique de l'utilisateur.")
    
    args = parser.parse_args()
    db = SessionLocal()

    try:
        # Si l'identifiant est un nombre, on cherche par ID en priorité
        if args.identifier.isdigit():
            user_id = int(args.identifier)
            print(f"Recherche de l'utilisateur par ID : {user_id}...")
            user = user_operations.get_user_by_id(db, user_id)
            if user:
                promote_user(db, user)
            else:
                print(f"❌ Erreur : Aucun utilisateur trouvé avec l'ID {user_id}.")
            return

        # Sinon, on fait une recherche partielle par pseudo
        search_term = f"%{args.identifier.lower()}%"
        print(f"Recherche des utilisateurs contenant '{args.identifier}'...")
        
        users_found = db.query(user_model.User).filter(func.lower(user_model.User.pseudo).like(search_term)).all()

        if len(users_found) == 1:
            promote_user(db, users_found[0])
        elif len(users_found) > 1:
            print(f"Plusieurs utilisateurs trouvés. Veuillez être plus précis ou utiliser l'ID.")
            for u in users_found:
                print(f"  - ID: {u.id}, Pseudo: {u.pseudo}")
        else:
            print(f"❌ Erreur : Aucun utilisateur trouvé contenant '{args.identifier}'.")

    finally:
        db.close()

if __name__ == "__main__":
    main()
