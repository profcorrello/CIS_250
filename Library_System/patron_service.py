from sqlalchemy.orm import Session
from models import Patron
import schemas
from fastapi import HTTPException

# PatronCreate and PatronResponse are now in schemas


def create_patron(db: Session, patron: schemas.PatronCreate):
    valid_types = ["Student", "Staff", "General"]
    if patron.patron_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid patron type. Must be one of {valid_types}")

    db_patron = Patron(name=patron.name, email=patron.email, patron_type=patron.patron_type)
    db.add(db_patron)
    db.commit()
    db.refresh(db_patron)
    return db_patron

def get_patron(db: Session, patron_id: int):
    return db.query(Patron).filter(Patron.id == patron_id).first()

def get_patrons(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Patron).offset(skip).limit(limit).all()
