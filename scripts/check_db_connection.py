import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Ajouter la racine du projet au chemin pour les imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def main():
    """
    Ce script teste la connexion à la base de données définie dans la variable d'environnement DATABASE_URL.
    """
    print("--- Lancement du test de connexion à la base de données ---")
    
    # Charger les variables depuis le fichier .env (s'il existe)
    load_dotenv()
    
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        print("\nERREUR : La variable d'environnement DATABASE_URL n'a pas été trouvée.")
        print("Veuillez vous assurer qu'un fichier .env est présent à la racine avec la bonne URL.")
        return

    print(f"Tentative de connexion à l'URL : {db_url[:40]}...") # Affiche le début de l'URL pour vérification

    try:
        engine = create_engine(db_url)
        
        with engine.connect() as connection:
            print("\n✅ SUCCÈS : Connexion à la base de données établie !")
            
            print("\n--- Tentative de lecture de la table 'users' ---")
            query = text("SELECT id, pseudo, is_admin FROM users LIMIT 5")
            result = connection.execute(query)
            
            rows = result.fetchall()
            if not rows:
                print("La table 'users' est vide, mais la connexion est fonctionnelle.")
            else:
                print("Voici les 5 premiers utilisateurs trouvés :")
                for row in rows:
                    print(f"  ID: {row.id}, Pseudo: {row.pseudo}, Parent: {row.is_admin}")
        
    except OperationalError as e:
        print("\n❌ ÉCHEC : Impossible de se connecter à la base de données.")
        print("Ceci est une 'OperationalError', ce qui confirme un problème de connexion.")
        print("\nVeuillez vérifier les points suivants :")
        print("  1. L'URL dans votre fichier .env ou vos secrets Streamlit est-elle EXACTEMENT correcte (utilisateur, mdp, hôte, port) ?")
        print("  2. Utilisez-vous bien l'URL du 'Transaction Pooler' ?")
        print("  3. Votre projet Supabase n'est-il pas en pause ?")
        
    except Exception as e:
        print(f"\n❌ ÉCHEC : Une erreur inattendue est survenue : {e}")

if __name__ == "__main__":
    main()
