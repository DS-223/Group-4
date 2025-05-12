# backend/main.py
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from database.models import User, Location, PropertyType, Property, Image, Prediction
from database.schema import UserBase, PropertyBase, PropertyTypeBase, LocationBase, ImageBase
from database.schema import UserCreate, LocationCreate, PropertyTypeCreate, PropertyCreate, ImageCreate

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
@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.user_id == user.user_id).first():
        raise HTTPException(status_code=400, detail="User already exists")
    db_user = User(
        user_id=user.user_id,
        user_name=user.user_name,
        email=user.email,
        phone=user.phone
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User created", "user": db_user}

@app.get("/users/{user_id}", response_model=UserBase)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ------------------- LOCATION -------------------
@app.post("/locations/")
def create_location(loc: LocationCreate, db: Session = Depends(get_db)):
    if db.query(Location).filter(Location.location_id == loc.location_id).first():
        raise HTTPException(status_code=400, detail="Location already exists")
    db_loc = Location(
        location_id=loc.location_id,
        city=loc.city,
        district=loc.district,
        country=loc.country
    )
    db.add(db_loc)
    db.commit()
    db.refresh(db_loc)
    return {"message": "Location created", "location": db_loc}

@app.get("/locations/{location_id}", response_model=LocationBase)
def get_location(location_id: int, db: Session = Depends(get_db)):
    loc = db.query(Location).filter(Location.location_id == location_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    return loc

# ------------------- PROPERTY TYPE -------------------
@app.post("/property_types/")
def create_property_type(pt: PropertyTypeCreate, db: Session = Depends(get_db)):
    if db.query(PropertyType).filter(PropertyType.type_id == pt.type_id).first():
        raise HTTPException(status_code=400, detail="Property type already exists")
    db_pt = PropertyType(
        type_id=pt.type_id,
        name=pt.name,
        description=pt.description
    )
    db.add(db_pt)
    db.commit()
    db.refresh(db_pt)
    return {"message": "Property type created", "property_type": db_pt}

@app.get("/property_types/{type_id}", response_model=PropertyTypeBase)
def get_property_type(type_id: int, db: Session = Depends(get_db)):
    pt = db.query(PropertyType).filter(PropertyType.type_id == type_id).first()
    if not pt:
        raise HTTPException(status_code=404, detail="Property type not found")
    return pt

# ------------------- PROPERTY -------------------
@app.post("/properties/")
def create_property(prop: PropertyCreate, db: Session = Depends(get_db)):
    if db.query(Property).filter(Property.property_id == prop.property_id).first():
        raise HTTPException(status_code=400, detail="Property already exists")
    db_prop = Property(
        property_id=prop.property_id,
        user_id=prop.user_id,
        type_id=prop.type_id,
        location_id=prop.location_id,
        price=prop.price,
        area=prop.area,
        bedrooms=prop.bedrooms,
        bathrooms=prop.bathrooms,
        furnished=prop.furnished,
        is_for_sale=prop.is_for_sale
    )
    db.add(db_prop)
    db.commit()
    db.refresh(db_prop)
    return {"message": "Property created", "property": db_prop}

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
@app.post("/images/")
def create_image(img: ImageCreate, db: Session = Depends(get_db)):
    if db.query(Image).filter(Image.image_id == img.image_id).first():
        raise HTTPException(status_code=400, detail="Image already exists")
    db_img = Image(
        image_id=img.image_id,
        property_id=img.property_id,
        image_url=img.image_url,
        description=img.description
    )
    db.add(db_img)
    db.commit()
    db.refresh(db_img)
    return {"message": "Image created", "image": db_img}

@app.get("/images/{image_id}", response_model=ImageBase)
def get_image(image_id: int, db: Session = Depends(get_db)):
    img = db.query(Image).filter(Image.image_id == image_id).first()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    return img

@app.get("/images/", response_model=List[ImageCreate])
def list_images(db: Session = Depends(get_db)):
    return db.query(Image).all()