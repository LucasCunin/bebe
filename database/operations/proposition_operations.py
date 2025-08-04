from sqlalchemy.orm import Session
from database.models import proposition as proposition_model
from database.operations import user_operations

def get_proposition_by_name(db: Session, name: str):
    """Trouve une proposition par son nom."""
    return db.query(proposition_model.Proposition).filter(proposition_model.Proposition.name == name).first()

def create_proposition(db: Session, name: str, proposer_id: int):
    """Crée une nouvelle proposition si l'utilisateur a des propositions restantes."""
    user = user_operations.get_user_by_id(db, proposer_id)
    if user and user.proposals_left > 0:
        if user_operations.decrement_user_proposals(db, proposer_id):
            db_proposition = proposition_model.Proposition(name=name, proposer_id=proposer_id)
            db.add(db_proposition)
            db.commit()
            db.refresh(db_proposition)
            return db_proposition
    return None

def get_all_propositions(db: Session):
    """Retourne toutes les propositions."""
    return db.query(proposition_model.Proposition).order_by(proposition_model.Proposition.name).all()
