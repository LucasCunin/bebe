import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. On cherche une variable d'environnement DATABASE_URL.
# 2. Si elle n'est pas trouvée, on utilise la base de données SQLite locale par défaut.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./votes.db")

from sqlalchemy.pool import NullPool

# 1. On cherche une variable d'environnement DATABASE_URL.
# 2. Si elle n'est pas trouvée, on utilise la base de données SQLite locale par défaut.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./votes.db")

# Dictionnaire pour les arguments de l'engine SQLAlchemy
engine_args = {}

# Si on est en local avec SQLite
if DATABASE_URL.startswith("sqlite"):
    engine_args['connect_args'] = {"check_same_thread": False}
# Si on est en production avec PostgreSQL (Supabase)
elif DATABASE_URL.startswith("postgresql"):
    # On désactive le pooling côté SQLAlchemy pour laisser Supabase le gérer.
    # C'est la solution recommandée pour les environnements serverless.
    engine_args['poolclass'] = NullPool

engine = create_engine(DATABASE_URL, **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
