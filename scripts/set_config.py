import sys
import os
import argparse
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Configuration du path pour les imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from database.database import SessionLocal
from database.operations import config_operations, user_operations, vote_operations
from database.models import vote as vote_model

def update_all_user_votes(db: Session, new_total_votes: int):
    """Met à jour le nombre de votes pour tous les utilisateurs."""
    users = user_operations.get_all_users(db)
    for user in users:
        # On ne change que le nombre de votes, pas les propositions
        user.votes_left = new_total_votes
    db.commit()
    print(f"Tous les utilisateurs ont maintenant {new_total_votes} votes.")

def reset_all_votes(db: Session):
    """Supprime tous les votes de la base de données."""
    db.query(vote_model.Vote).delete()
    db.commit()
    print("Tous les votes ont été réinitialisés.")


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Gère la configuration de l'application.")
    parser.add_argument("--key", type=str, required=True, help="La clé de configuration à modifier (ex: DEFAULT_VOTES).")
    parser.add_argument("--value", type=int, required=True, help="La nouvelle valeur entière pour la clé.")
    
    args = parser.parse_args()
    
    db = SessionLocal()
    
    # Récupérer l'ancienne valeur pour comparaison, si elle existe
    old_value = config_operations.get_config_value(db, args.key, -1)
    
    # Mettre à jour la configuration
    config_operations.set_config_value(db, args.key, args.value)
    print(f"La clé '{args.key}' a été mise à jour à la valeur '{args.value}'.")
    
    # Logique spécifique si on change le nombre de votes par défaut
    if args.key == "DEFAULT_VOTES":
        if args.value < old_value:
            print("Le nombre de votes a été réduit.")
            print("Réinitialisation de tous les votes pour être juste envers tout le monde.")
            reset_all_votes(db)
            update_all_user_votes(db, args.value)
        elif args.value > old_value:
            print("Le nombre de votes a été augmenté.")
            # On ne réinitialise pas, on ajoute simplement la différence.
            # Cependant, la demande était de mettre à jour le total, donc on fait ça.
            update_all_user_votes(db, args.value)

    db.close()

if __name__ == "__main__":
    main()
