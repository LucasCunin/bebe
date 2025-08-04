from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    pseudo = Column(String, unique=True, index=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    proposals_left = Column(Integer, nullable=False)
    votes_left = Column(Integer, nullable=False)

    propositions = relationship("Proposition", back_populates="proposer")
    votes = relationship("Vote", back_populates="voter")
