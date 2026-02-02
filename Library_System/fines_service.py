from sqlalchemy.orm import Session
from models import Fine, Patron
import schemas

FINE_CONFIG = {
    "rates": {
        "General": {"Book": 0.50, "DVD": 1.00, "Reference": 5.00},
        "Student": {"Book": 0.10, "DVD": 0.50, "Reference": 1.00},
        "Staff": {"Book": 0.00, "DVD": 0.00, "Reference": 0.00}
    },
    "grace_period_days": 1,
    "max_fine_per_item": 20.00
}

def calculate_fine(days_overdue: int, patron_type: str, item_type: str) -> float:
    """
    Calculate fine based on overdue days, patron type, and item type.
    Includes grace period and maximum fine cap logic.
    """
    if days_overdue <= 0:
        return 0.0

    # Grace Period Check
    if days_overdue <= FINE_CONFIG["grace_period_days"]:
        return 0.0

    # Determine Rate
    patron_rates = FINE_CONFIG["rates"].get(patron_type, FINE_CONFIG["rates"]["General"])
    rate = patron_rates.get(item_type, patron_rates.get("Book", 0.50))

    # Calculate Fine
    # Note: Fines usually accrue for the grace period days too if the grace period is exceeded.
    # Policy: If overdue > grace_period, charge for all days.
    total_fine = days_overdue * rate

    # Apply Cap
    return min(total_fine, FINE_CONFIG["max_fine_per_item"])

def create_fine(db: Session, fine: schemas.FineCreate):
    db_fine = Fine(**fine.dict())
    db.add(db_fine)
    db.commit()
    db.refresh(db_fine)
    return db_fine

from fastapi import HTTPException
import datetime

# ... (existing imports)

# ... (existing code)

def pay_fine(db: Session, fine_id: int, amount: float):
    fine = db.query(Fine).filter(Fine.id == fine_id).first()
    if not fine:
        raise HTTPException(status_code=404, detail="Fine not found")
        
    if fine.is_paid:
         raise HTTPException(status_code=400, detail="Fine is already paid")
         
    new_amount_paid = fine.amount_paid + amount
    if new_amount_paid > fine.amount:
        raise HTTPException(status_code=400, detail="Payment exceeds fine amount")
        
    fine.amount_paid = new_amount_paid
    if fine.amount_paid >= fine.amount:
        fine.is_paid = True
        fine.payment_date = datetime.datetime.utcnow()
        
    db.commit()
    db.refresh(fine)
    return fine

def get_patron_fines(db: Session, patron_id: int):
    return db.query(Fine).filter(Fine.patron_id == patron_id).all()
