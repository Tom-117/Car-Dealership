from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from .models import Car, CarCreate, CarResponse
from .database import get_db

app = FastAPI(
    title="Car Dealership API",
    description="Inventory management for a car dealership",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def health():
    return {"status": "healthy"}


@app.post("/cars", response_model=CarResponse)
async def create_car(car: CarCreate, db: AsyncSession = Depends(get_db)):
    db_car = Car(**car.dict())
    db.add(db_car)
    await db.commit()
    await db.refresh(db_car)
    return db_car

@app.get("/cars", response_model=list[CarResponse])
async def read_cars(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Car))
    return result.scalars().all()

@app.get("/cars/{car_id}", response_model=CarResponse)
async def read_car(car_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Car).where(Car.id == car_id))
    car = result.scalar_one_or_none()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car

@app.put("/cars/{car_id}", response_model=CarResponse)
async def update_car(car_id: int, car: CarCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Car).where(Car.id == car_id))
    db_car = result.scalar_one_or_none()
    if not db_car:
        raise HTTPException(status_code=404, detail="Car not found")
    for k, v in car.dict().items():
        setattr(db_car, k, v)
    await db.commit()
    await db.refresh(db_car)
    return db_car

@app.delete("/cars/{car_id}")
async def delete_car(car_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Car).where(Car.id == car_id))
    car = result.scalar_one_or_none()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    await db.delete(car)
    await db.commit()
    return {"detail": "Car deleted"}