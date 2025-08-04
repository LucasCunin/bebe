from sqlalchemy import Column, Integer, String
from database.database import Base

class Config(Base):
    __tablename__ = "config"

    key = Column(String, primary_key=True, index=True)
    value = Column(Integer, nullable=False)
