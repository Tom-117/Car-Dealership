from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()

class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True, index=True)
    make = Column(String, index=True)
    model = Column(String, index=True)
    year = Column(Integer)
    price = Column(Float)
    vin = Column(String, unique=True, index=True)
    color = Column(String)

class CarCreate(BaseModel):
    make: str
    model: str
    year: int
    price: float
    vin: str
    color: str

class CarResponse(BaseModel):
    id: int
    make: str
    model: str
    year: int
    price: float
    vin: str
    color: str

    class Config:
        from_attributes = True