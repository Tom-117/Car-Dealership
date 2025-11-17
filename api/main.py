from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Car, CarCreate, CarResponse
from .database import get_db
import os
import uuid
from typing import Optional

# Check if running in AWS
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
S3_BUCKET = os.getenv("S3_BUCKET", "")
AWS_REGION = os.getenv("AWS_REGION", "eu-central-1")


s3_client = None
if ENVIRONMENT == "production" and S3_BUCKET:
    import boto3
    from botocore.exceptions import ClientError
    s3_client = boto3.client('s3', region_name=AWS_REGION)

app = FastAPI(
    title="Car Dealership API",
    description="Inventory management for a car dealership",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    root_path="/api" if ENVIRONMENT == "production" else ""
)


if ENVIRONMENT == "production":
    allowed_origins = ["*"]
else:
    allowed_origins = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health():
    return {
        "status": "healthy",
        "environment": ENVIRONMENT,
        "s3_configured": bool(s3_client and S3_BUCKET)
    }


def upload_to_s3(file_content: bytes, filename: str, content_type: str) -> str:
    """Upload file to S3 and return the URL"""
    if not s3_client or not S3_BUCKET:
        raise HTTPException(status_code=500, detail="S3 not configured")
    
    try:
        
        file_extension = filename.split('.')[-1] if '.' in filename else 'jpg'
        unique_filename = f"cars/{uuid.uuid4()}.{file_extension}"
        
       
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=unique_filename,
            Body=file_content,
            ContentType=content_type
        )
        
        
        return f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{unique_filename}"
    
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"S3 upload failed: {str(e)}")

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Upload an image to S3 (production) or return mock URL (development)"""
    
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    
    content = await file.read()
    
   
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")
    
    # In development, just return mock URLs
    if ENVIRONMENT == "development":
        mock_id = str(uuid.uuid4())
        return {
            "image_url": f"http://localhost:8000/mock-images/{mock_id}.jpg",
            "thumbnail_url": f"http://localhost:8000/mock-images/thumb-{mock_id}.jpg",
            "message": "Image received (development mode - not uploaded to S3)"
        }
    
   
    image_url = upload_to_s3(content, file.filename, file.content_type)
    
    
    thumbnail_key = f"thumbnails/cars/{image_url.split('/')[-1]}"
    thumbnail_bucket = os.getenv('THUMBNAIL_BUCKET', S3_BUCKET)
    thumbnail_url = f"https://{thumbnail_bucket}.s3.{AWS_REGION}.amazonaws.com/{thumbnail_key}"
    
    return {
        "image_url": image_url,
        "thumbnail_url": thumbnail_url,
        "message": "Image uploaded successfully. Thumbnail will be generated in a few seconds."
    }

@app.post("/cars", response_model=CarResponse)
async def create_car(car: CarCreate, db: AsyncSession = Depends(get_db)):
    db_car = Car(**car.dict())
    db.add(db_car)
    await db.commit()
    await db.refresh(db_car)
    return db_car

@app.post("/cars-with-image", response_model=CarResponse)
async def create_car_with_image(
    make: str = Form(...),
    model: str = Form(...),
    year: int = Form(...),
    price: float = Form(...),
    vin: str = Form(...),
    color: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    """Create a car with optional image upload"""
    
    image_url = None
    thumbnail_url = None
    
    # Upload image if provided
    if image and image.filename:
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        content = await image.read()
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image too large (max 5MB)")
        
        
        if ENVIRONMENT == "development":
            mock_id = str(uuid.uuid4())
            image_url = f"http://localhost:8000/mock-images/{mock_id}.jpg"
            thumbnail_url = f"http://localhost:8000/mock-images/thumb-{mock_id}.jpg"
        else:
            
            image_url = upload_to_s3(content, image.filename, image.content_type)
            
           
            thumbnail_key = f"thumbnails/cars/{image_url.split('/')[-1]}"
            thumbnail_bucket = os.getenv('THUMBNAIL_BUCKET', S3_BUCKET)
            thumbnail_url = f"https://{thumbnail_bucket}.s3.{AWS_REGION}.amazonaws.com/{thumbnail_key}"
    
    
    db_car = Car(
        make=make,
        model=model,
        year=year,
        price=price,
        vin=vin,
        color=color,
        image_url=image_url,
        thumbnail_url=thumbnail_url
    )
    
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