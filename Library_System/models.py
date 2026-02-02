from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, DateTime, Float
from sqlalchemy.orm import relationship
from database import Base
import datetime

class PartnerLibrary(Base):
    __tablename__ = "partner_libraries"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    contact_email = Column(String)
    shipping_address = Column(String)

class Patron(Base):
    __tablename__ = "patrons"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    patron_type = Column(String, default="General") # Student, Staff, General

    holds = relationship("Hold", back_populates="patron", cascade="all, delete-orphan")
    fines = relationship("Fine", back_populates="patron", cascade="all, delete-orphan")

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    isbn = Column(String, unique=True, index=True)
    status = Column(String, default="Available") # Available, Checked Out, Lost
    item_type = Column(String, default="Book") 

    holds = relationship("Hold", back_populates="book", cascade="all, delete-orphan")

class ILLRequest(Base):
    __tablename__ = "ill_requests"
    id = Column(Integer, primary_key=True, index=True)
    patron_id = Column(Integer, ForeignKey("patrons.id"))
    title = Column(String)
    author = Column(String)
    status = Column(String, default="Draft") # Draft, Submitted, In Transit, Received, Checked Out, Returned
    partner_library_id = Column(Integer, ForeignKey("partner_libraries.id"), nullable=True)

class Fine(Base):
    __tablename__ = "fines"
    id = Column(Integer, primary_key=True, index=True)
    patron_id = Column(Integer, ForeignKey("patrons.id"))
    amount = Column(Float, default=0.0)
    amount_paid = Column(Float, default=0.0)
    reason = Column(String)
    is_paid = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    payment_date = Column(DateTime, nullable=True)

    patron = relationship("Patron", back_populates="fines")

class Hold(Base):
    __tablename__ = "holds"
    id = Column(Integer, primary_key=True, index=True)
    patron_id = Column(Integer, ForeignKey("patrons.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    available_since = Column(DateTime, nullable=True)
    
    patron = relationship("Patron", back_populates="holds")
    book = relationship("Book", back_populates="holds")
