from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Proposition(Base):
    __tablename__ = "propositions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    proposer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    proposer = relationship("User", back_populates="propositions")
    votes = relationship("Vote", back_populates="proposition")
