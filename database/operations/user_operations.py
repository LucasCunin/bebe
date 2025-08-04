from sqlalchemy.orm import Session
from database.models import user as user_model
from database.operations import config_operations

def get_user_by_pseudo(db: Session, pseudo: str):
    """Trouve un utilisateur par son pseudo (insensible à la casse et aux espaces)."""
    clean_pseudo = pseudo.strip().lower()
    return db.query(user_model.User).filter(user_model.User.pseudo == clean_pseudo).first()

def get_user_by_id(db: Session, user_id: int):
    """Trouve un utilisateur par son ID."""
    return db.query(user_model.User).filter(user_model.User.id == user_id).first()

def create_user(db: Session, pseudo: str):
    """Crée un nouvel utilisateur avec les valeurs par défaut de la config."""
    default_proposals = config_operations.get_config_value(db, "DEFAULT_PROPOSALS", 3)
    default_votes = config_operations.get_config_value(db, "DEFAULT_VOTES", 5)
    
    clean_pseudo = pseudo.strip().lower()

    # Vérifier si un utilisateur avec ce pseudo nettoyé n'existe pas déjà
    existing_user = get_user_by_pseudo(db, clean_pseudo)
    if existing_user:
        # Retourner l'utilisateur existant au lieu d'en créer un nouveau
        return existing_user

    db_user = user_model.User(
        pseudo=clean_pseudo,
        proposals_left=default_proposals,
        votes_left=default_votes
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def set_admin(db: Session, user_id: int):
    """Définit un utilisateur comme administrateur et met à jour ses votes."""
    user = get_user_by_id(db, user_id)
    if user:
        if not user.is_admin:
            user.is_admin = True
            # Met à jour tous les votes passés de cet utilisateur
            for vote in user.votes:
                vote.is_admin_vote = True
            db.commit()
    return user

def increment_user_votes(db: Session, user_id: int):
    """Incrémente le compteur de votes restants d'un utilisateur."""
    user = get_user_by_id(db, user_id)
    if user:
        user.votes_left += 1
        db.commit()

def decrement_user_votes(db: Session, user_id: int):
    """Décrémente le compteur de votes restants d'un utilisateur."""
    user = get_user_by_id(db, user_id)
    if user and user.votes_left > 0:
        user.votes_left -= 1
        db.commit()
        return True
    return False

def decrement_user_proposals(db: Session, user_id: int):
    """Décrémente le compteur de propositions restantes d'un utilisateur."""
    user = get_user_by_id(db, user_id)
    if user and user.proposals_left > 0:
        user.proposals_left -= 1
        db.commit()
        return True
    return False

def get_all_users(db: Session):
    """Retourne tous les utilisateurs."""
    return db.query(user_model.User).all()
