from sqlalchemy.orm import Session
from models import Hold, Book, Patron
import schemas

from fastapi import HTTPException
from datetime import datetime

def create_hold(db: Session, hold: schemas.HoldCreate):
    # 1. Check if book exists
    book = db.query(Book).filter(Book.id == hold.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # 2. Check if book is actually available (if so, error - should checkout)
    if book.status == "Available":
        raise HTTPException(status_code=400, detail="Book is available. Please check it out instead of placing a hold.")

    # 3. Check for Duplicate Hold
    existing_hold = db.query(Hold).filter(
        Hold.book_id == hold.book_id, 
        Hold.patron_id == hold.patron_id, 
        Hold.is_active == True
    ).first()
    if existing_hold:
        raise HTTPException(status_code=400, detail="Use already has an active hold on this book.")

    db_hold = Hold(**hold.dict())
    db.add(db_hold)
    db.commit()
    db.refresh(db_hold)
    return db_hold

def get_book_holds(db: Session, book_id: int):
    return db.query(Hold).filter(Hold.book_id == book_id).order_by(Hold.created_at.asc()).all()

def process_hold_expiry(db: Session, expiry_days: int = 5):
    """
    Cancel holds that have been active and unclaimed for longer than expiry_days.
    """
    from datetime import datetime, timedelta
    
    # Logic note: We only expire holds that are 'promoted' i.e. available_since is set.
    # If available_since is NULL, it means the book hasn't come back yet, so the hold shouldn't expire.
    
    expiry_threshold = datetime.utcnow() - timedelta(days=expiry_days)
    
    expired_holds = db.query(Hold).filter(
        Hold.is_active == True,
        Hold.available_since != None,
        Hold.available_since <= expiry_threshold
    ).all()
    
    count = 0
    for hold in expired_holds:
        hold.is_active = False
        count += 1
        # Trigger next hold?
        promote_next_hold(db, hold.book_id)
        
    db.commit()
    return count

def promote_next_hold(db: Session, book_id: int):
    """
    Find the next active hold for a book and notify the patron.
    This should be called when a book is returned OR when a previous hold expires.
    """
    # Find next active hold that hasn't been promoted yet
    next_hold = db.query(Hold).filter(
        Hold.book_id == book_id,
        Hold.is_active == True,
        Hold.available_since == None
    ).order_by(Hold.created_at.asc()).first()
    
    if next_hold:
        next_hold.available_since = datetime.utcnow()
        db.commit()
        db.refresh(next_hold)
        # Placeholder for notification logic
        # notify_patron(next_hold.patron_id)
        return next_hold
    return None
