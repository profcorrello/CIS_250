from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

import models
import schemas
import ill_service
import fines_service
import holds_service
import patron_service
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Library Management System")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Library System API"}

# ILL Endpoints
@app.post("/ill/requests/", response_model=schemas.ILLRequestResponse)
def create_ill(request: schemas.ILLRequestCreate, db: Session = Depends(get_db)):
    return ill_service.create_ill_request(db=db, request=request)

@app.get("/ill/requests/", response_model=List[schemas.ILLRequestResponse])
def read_ill_requests(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return ill_service.get_ill_requests(db, skip=skip, limit=limit)

# Fines Endpoints
@app.post("/fines/", response_model=schemas.FineResponse)
def create_fine_endpoint(fine: schemas.FineCreate, db: Session = Depends(get_db)):
    return fines_service.create_fine(db=db, fine=fine)

@app.get("/patrons/{patron_id}/fines", response_model=List[schemas.FineResponse])
def read_patron_fines(patron_id: int, db: Session = Depends(get_db)):
    return fines_service.get_patron_fines(db, patron_id=patron_id)

@app.post("/fines/{fine_id}/pay", response_model=schemas.FineResponse)
def pay_fine_endpoint(fine_id: int, amount: float, db: Session = Depends(get_db)):
    return fines_service.pay_fine(db=db, fine_id=fine_id, amount=amount)

# Holds Endpoints
@app.post("/holds/", response_model=schemas.HoldResponse)
def create_hold_endpoint(hold: schemas.HoldCreate, db: Session = Depends(get_db)):
    return holds_service.create_hold(db=db, hold=hold)

@app.get("/books/{book_id}/holds", response_model=List[schemas.HoldResponse])
def read_book_holds(book_id: int, db: Session = Depends(get_db)):
    return holds_service.get_book_holds(db, book_id=book_id)

@app.post("/books/{book_id}/return", response_model=Optional[schemas.HoldResponse])
def return_book_endpoint(book_id: int, db: Session = Depends(get_db)):
    # Logic to return book would specifically update book status to Available
    # Then check for holds
    # For now, we assume this endpoint is specifically triggering the hold promotion
    # In a full system, this would be part of a larger 'check_in' service
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
        
    book.status = "Available"
    next_hold = holds_service.promote_next_hold(db, book_id=book_id)
    if next_hold:
         book.status = "Reserved" # Or similar status indicating it's held
         
    db.commit()
    db.refresh(book)
    return next_hold # Returns the next hold if promoted, or None

# Patron Endpoints
@app.post("/patrons/", response_model=schemas.PatronResponse)
def create_patron_endpoint(patron: schemas.PatronCreate, db: Session = Depends(get_db)):
    return patron_service.create_patron(db=db, patron=patron)

@app.get("/patrons/", response_model=List[schemas.PatronResponse])
def read_patrons(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return patron_service.get_patrons(db, skip=skip, limit=limit)

