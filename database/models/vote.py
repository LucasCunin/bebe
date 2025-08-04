from sqlalchemy import Boolean, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    proposition_id = Column(Integer, ForeignKey("propositions.id"), nullable=False)
    is_admin_vote = Column(Boolean, default=False, nullable=False)

    voter = relationship("User", back_populates="votes")
    proposition = relationship("Proposition", back_populates="votes")
