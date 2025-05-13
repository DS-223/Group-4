# backend/main.py
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from database.models import User, Location, PropertyType, Property, Image, Prediction
from database.schema import UserBase, PropertyBase, PropertyTypeBase, LocationBase, ImageBase

from prediction_router import router as prediction_router
from database.engine import engine
from database.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Marketing-Analytics API",
    description="CRUD operations + House Price Prediction (Rent/Sale/Survival)",
    version="1.0.0"
)

# Attach ML prediction endpoints
app.include_router(prediction_router)

# ------------------- USER -------------------

@app.get("/users/{user_id}", response_model=UserBase)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ------------------- LOCATION -------------------

@app.get("/locations/{location_id}", response_model=LocationBase)
def get_location(location_id: int, db: Session = Depends(get_db)):
    loc = db.query(Location).filter(Location.location_id == location_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    return loc

# ------------------- PROPERTY TYPE -------------------

@app.get("/property_types/{type_id}", response_model=PropertyTypeBase)
def get_property_type(type_id: int, db: Session = Depends(get_db)):
    pt = db.query(PropertyType).filter(PropertyType.type_id == type_id).first()
    if not pt:
        raise HTTPException(status_code=404, detail="Property type not found")
    return pt

# ------------------- PROPERTY -------------------

@app.get("/properties/{property_id}", response_model=PropertyBase)
def get_property(property_id: int, db: Session = Depends(get_db)):
    prop = db.query(Property).filter(Property.property_id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop

@app.get("/prediction/")
def get_prediction(property_id: int, db: Session = Depends(get_db)):
    prop = db.query(Prediction).filter(Prediction.property_id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return prop

# ------------------- IMAGE -------------------

@app.get("/images/{image_id}", response_model=ImageBase)
def get_image(image_id: int, db: Session = Depends(get_db)):
    img = db.query(Image).filter(Image.image_id == image_id).first()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    return img