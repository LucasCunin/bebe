from sqlalchemy.orm import Session
from database.models import vote as vote_model
from database.operations import user_operations

def create_vote(db: Session, user_id: int, proposition_id: int):
    """Crée un vote si l'utilisateur a des votes restants."""
    user = user_operations.get_user_by_id(db, user_id)
    if user and user.votes_left > 0:
        if user_operations.decrement_user_votes(db, user_id):
            db_vote = vote_model.Vote(
                user_id=user_id,
                proposition_id=proposition_id,
                is_admin_vote=user.is_admin
            )
            db.add(db_vote)
            db.commit()
            db.refresh(db_vote)
            return db_vote
    return None

def get_user_vote_for_proposition(db: Session, user_id: int, proposition_id: int):
    """Récupère le vote d'un utilisateur pour une proposition spécifique."""
    return db.query(vote_model.Vote).filter(
        vote_model.Vote.user_id == user_id,
        vote_model.Vote.proposition_id == proposition_id
    ).first()

def cancel_vote(db: Session, vote_id: int):
    """Annule un vote et restaure le crédit de vote de l'utilisateur."""
    vote = db.query(vote_model.Vote).filter(vote_model.Vote.id == vote_id).first()
    if vote:
        user_operations.increment_user_votes(db, vote.user_id)
        db.delete(vote)
        db.commit()
        return True
    return False

def get_vote_counts_for_proposition(db: Session, proposition_id: int):
    """Compte les votes normaux et admin pour une proposition."""
    normal_votes = db.query(vote_model.Vote).filter(
        vote_model.Vote.proposition_id == proposition_id,
        vote_model.Vote.is_admin_vote == False
    ).count()
    admin_votes = db.query(vote_model.Vote).filter(
        vote_model.Vote.proposition_id == proposition_id,
        vote_model.Vote.is_admin_vote == True
    ).count()
    return {"normal_votes": normal_votes, "admin_votes": admin_votes}
