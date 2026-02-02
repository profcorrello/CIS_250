from sqlalchemy.orm import Session
from models import ILLRequest, PartnerLibrary
import schemas

def create_ill_request(db: Session, request: schemas.ILLRequestCreate):
    db_request = ILLRequest(**request.dict(), status="Draft")
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request

def get_ill_requests(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ILLRequest).offset(skip).limit(limit).all()

from fastapi import HTTPException

# ... (other imports)

def update_ill_status(db: Session, request_id: int, status: str):
    request = db.query(ILLRequest).filter(ILLRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="ILL Request not found")
        
    valid_transitions = {
        "Draft": ["Submitted"],
        "Submitted": ["In Transit"],
        "In Transit": ["Received"],
        "Received": ["Checked Out"],
        "Checked Out": ["Returned"],
        "Returned": [] 
    }
    
    current_status = request.status
    if status not in valid_transitions.get(current_status, []):
        raise HTTPException(status_code=400, detail=f"Invalid status transition from {current_status} to {status}")

    # Validation for partner library
    if status in ["Submitted", "In Transit"] and not request.partner_library_id:
         raise HTTPException(status_code=400, detail="Partner library must be assigned before submitting.")

    request.status = status
    db.commit()
    db.refresh(request)
    return request
