
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models import Book, Patron, Hold, Fine, ILLRequest
from ill_service import update_ill_status
from fines_service import calculate_fine, pay_fine, create_fine
from holds_service import create_hold, process_hold_expiry, promote_next_hold
from patron_service import create_patron
from schemas import PatronCreate, HoldCreate, FineCreate
from fastapi import HTTPException
from datetime import datetime, timedelta

# Setup in-memory DB
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_fine_calculation():
    # General, Book, 10 days overdue -> 10 * 0.50 = 5.0
    assert calculate_fine(10, "General", "Book") == 5.0
    # Student, Book, 10 days overdue -> 10 * 0.10 = 1.0
    assert calculate_fine(10, "Student", "Book") == 1.0
    # Grace period check (1 day grace)
    assert calculate_fine(1, "General", "Book") == 0.0

def test_pay_fine(db):
    patron = Patron(name="Test", email="test@test.com", patron_type="General")
    db.add(patron)
    db.commit()
    
    fine = Fine(patron_id=patron.id, amount=10.0, reason="Overdue")
    db.add(fine)
    db.commit()
    
    # Partial payment
    pay_fine(db, fine.id, 5.0)
    assert fine.amount_paid == 5.0
    assert fine.is_paid == False
    
    # Full payment
    pay_fine(db, fine.id, 5.0)
    assert fine.amount_paid == 10.0
    assert fine.is_paid == True
    assert fine.payment_date is not None

def test_ill_transitions(db):
    req = ILLRequest(title="Rare Book", author="Unknown", status="Draft")
    db.add(req)
    db.commit()
    
    # Invalid transition Draft -> Received
    with pytest.raises(HTTPException):
        update_ill_status(db, req.id, "Received")
        
    # Valid transition Draft -> Submitted (requires partner if strictly enforced? Code: "Submitted" requires partner)
    # logic: if status in ["Submitted", "In Transit"] and not request.partner_library_id: raise
    with pytest.raises(HTTPException):
        update_ill_status(db, req.id, "Submitted")
        
    req.partner_library_id = 1
    db.commit()
    
    updated = update_ill_status(db, req.id, "Submitted")
    assert updated.status == "Submitted"

def test_hold_logic(db):
    # Setup
    book = Book(title="Popular Book", author="Star", status="Checked Out") # Must be unavailable for hold
    db.add(book)
    p1 = Patron(name="P1", email="p1@test.com")
    p2 = Patron(name="P2", email="p2@test.com")
    db.add_all([p1, p2])
    db.commit()
    
    # Create Hold P1
    h1 = create_hold(db, HoldCreate(patron_id=p1.id, book_id=book.id))
    assert h1.is_active == True
    
    # Create Hold P2
    h2 = create_hold(db, HoldCreate(patron_id=p2.id, book_id=book.id))
    
    # Duplicate Hold P1
    with pytest.raises(HTTPException):
        create_hold(db, HoldCreate(patron_id=p1.id, book_id=book.id))
        
    # Return Book -> Promote P1
    # Simulate return by calling promote_next_hold
    # But promote_next_hold works on existing holds.
    promoted = promote_next_hold(db, book.id)
    assert promoted.id == h1.id
    assert promoted.available_since is not None
    
    # Expire P1
    # Manually set available_since to old date
    promoted.available_since = datetime.utcnow() - timedelta(days=10)
    db.commit()
    
    count = process_hold_expiry(db, expiry_days=5)
    assert count == 1
    assert h1.is_active == False
    
    # Check if P2 got promoted
    # process_hold_expiry calls promote_next_hold
    db.refresh(h2)
    assert h2.available_since is not None
