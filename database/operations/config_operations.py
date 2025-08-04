from sqlalchemy.orm import Session
from database.models import config as config_model

def get_config_value(db: Session, key: str, default: int) -> int:
    """Récupère une valeur de configuration, ou la crée si elle n'existe pas."""
    config_entry = db.query(config_model.Config).filter(config_model.Config.key == key).first()
    if not config_entry:
        config_entry = config_model.Config(key=key, value=default)
        db.add(config_entry)
        db.commit()
        db.refresh(config_entry)
    return config_entry.value

def set_config_value(db: Session, key: str, value: int):
    """Définit une valeur de configuration."""
    config_entry = db.query(config_model.Config).filter(config_model.Config.key == key).first()
    if config_entry:
        config_entry.value = value
    else:
        config_entry = config_model.Config(key=key, value=value)
        db.add(config_entry)
    db.commit()
    return config_entry
