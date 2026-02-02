from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ILLRequestBase(BaseModel):
    title: str
    author: str
    patron_id: int

class ILLRequestCreate(ILLRequestBase):
    pass

class ILLRequestResponse(ILLRequestBase):
    id: int
    status: str
    partner_library_id: Optional[int]
    
    class Config:
        from_attributes = True

class FineBase(BaseModel):
    patron_id: int
    amount: float
    reason: str

class FineCreate(FineBase):
    pass

class FineResponse(FineBase):
    id: int
    is_paid: bool
    created_at: datetime
    payment_date: Optional[datetime] = None
    amount_paid: float
    
    class Config:
        from_attributes = True

class HoldBase(BaseModel):
    patron_id: int
    book_id: int

class HoldCreate(HoldBase):
    pass

class HoldResponse(HoldBase):
    id: int
    created_at: datetime
    is_active: bool
    available_since: Optional[datetime] = None

    class Config:
        from_attributes = True

class PatronBase(BaseModel):
    name: str
    email: str
    patron_type: str = "General"

class PatronCreate(PatronBase):
    pass

class PatronResponse(PatronBase):
    id: int
    
    class Config:
        from_attributes = True
