# 🫏 Application de Vote de Prénom

Cette application, construite avec Streamlit, permet à un groupe de personnes de proposer des prénoms et de voter pour leurs préférés. Elle inclut un système de vote double pour les "Parents" (administrateurs).

## Lancement de l'application

### 1. Installation des dépendances

Assurez-vous d'avoir Python installé. Ensuite, installez les paquets nécessaires :

```bash
pip install -r requirements.txt
```

### 2. Configuration de la base de données

L'application peut fonctionner avec deux types de bases de données :

-   **Locale (pour le test)** : Par défaut, si aucune configuration n'est spécifiée, l'application créera et utilisera un fichier `votes.db` à la racine du projet.
-   **Production (PostgreSQL)** : Pour se connecter à une base de données de production (comme Supabase), créez un fichier `.env` à la racine du projet et mettez-y l'URL de connexion :
    ```
    DATABASE_URL="votre_url_postgresql_ici"
    ```

### 3. Lancement

Une fois la configuration prête, lancez l'application avec la commande :

```bash
streamlit run app.py
```

---

## Guide des Scripts d'Administration

Les scripts de modération se trouvent dans le dossier `/scripts`. Ils sont conçus pour être lancés depuis votre terminal local pour gérer l'application en production.

**Important** : Pour que ces scripts interagissent avec la base de données de production, assurez-vous que votre fichier `.env` est présent et configuré à la racine du projet.

### Promouvoir un utilisateur au statut "Parent"

Ce script permet de donner des droits d'administrateur (vote double) à un utilisateur.

-   **Nom du script** : `set_user_admin.py`
-   **Cas d'usage** : Quand un parent ou un modérateur a besoin que ses votes comptent double.
-   **Comment l'utiliser** : Vous pouvez utiliser soit l'ID de l'utilisateur (le plus précis), soit un morceau de son pseudo.

**Par ID (recommandé) :**
```bash
python scripts/set_user_admin.py 3
```

**Par recherche de pseudo :**
```bash
python scripts/set_user_admin.py carole
```

---

### Ajouter des votes ou des propositions à tout le monde

Ces scripts sont utiles pour relancer l'engagement en donnant à tous les participants plus de ressources.

#### Ajouter des propositions

-   **Nom du script** : `add_proposals_to_all.py`
-   **Cas d'usage** : Si tout le monde a épuisé ses propositions et que vous voulez permettre de nouvelles idées.
-   **Comment l'utiliser** : Passez en argument le nombre de propositions à ajouter.

**Exemple : Ajouter 2 propositions à chaque utilisateur**
```bash
python scripts/add_proposals_to_all.py 2
```

#### Ajouter des votes

-   **Nom du script** : `add_votes_to_all.py`
-   **Cas d'usage** : Si vous voulez prolonger la phase de vote ou donner plus de poids aux participants.
-   **Comment l'utiliser** : Passez en argument le nombre de votes à ajouter.

**Exemple : Ajouter 5 votes à chaque utilisateur**
```bash
python scripts/add_votes_to_all.py 5
```

---

### Réinitialiser tous les votes

Ce script est un "reset" complet. Il est parfait pour démarrer un nouveau tour de scrutin.

-   **Nom du script** : `reset_all_votes.py`
-   **Cas d'usage** : À la fin d'un tour de vote, si vous voulez effacer tous les suffrages et repartir de zéro, en redonnant à chacun son quota de votes initial.
-   **Ce qu'il fait** :
    1.  Supprime **tous les votes** de la table `votes`.
    2.  Réinitialise le compteur de votes restants de chaque utilisateur à la valeur définie dans la configuration (`DEFAULT_VOTES`).
-   **Comment l'utiliser** : Le script vous demandera une confirmation.

```bash
python scripts/reset_all_votes.py
```

---

### Gérer la configuration globale

Ce script permet de changer les paramètres de base de l'application.

-   **Nom du script** : `set_config.py`
-   **Cas d'usage** : Changer le nombre de votes ou de propositions que les **nouveaux** utilisateurs reçoivent, ou mettre à jour ces valeurs pour tout le monde.
-   **Comment l'utiliser** : Spécifiez la clé (`--key`) et la nouvelle valeur (`--value`).

**Exemple : Définir le nombre de votes par défaut à 7**
```bash
python scripts/set_config.py --key DEFAULT_VOTES --value 7
```
*Note : Si vous diminuez le nombre de votes, le script réinitialisera tous les votes existants pour être juste.*
