from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict

# Dummy data generators (replace with DB calls when ready)
from etl.database.data_generate import (
    generate_user,
    generate_property,
    generate_location,
    generate_property_type,
    generate_image,
)

# Import external prediction router
from prediction_router import router as prediction_router

# Initialize app
app = FastAPI(
    title="Marketing-Analytics API",
    description="CRUD stubs + ML predictions (DB integration pending)",
    version="1.0.0",
)

# Mount the prediction router under /predict
app.include_router(prediction_router)

# In-memory stores for stubs
db_users: Dict[int, dict] = {}
db_locations: Dict[int, dict] = {}
db_property_types: Dict[int, dict] = {}
db_properties: Dict[int, dict] = {}
db_images: Dict[int, dict] = {}

# Pydantic schemas for requests
class UserCreate(BaseModel):
    user_id: int
    user_type: str

class LocationCreate(BaseModel):
    location_id: int

class PropertyTypeCreate(BaseModel):
    type_id: int
    type_name: str

class PropertyCreate(BaseModel):
    property_id: int
    user_id: int
    location_id: int

class ImageCreate(BaseModel):
    image_id: int
    property_id: int
    image_url: str

# ────────────────────────────────────────────────────────────────────────────────
# CRUD stubs
# ────────────────────────────────────────────────────────────────────────────────

@app.post("/users/")
def create_user(user: UserCreate):
    if user.user_id in db_users:
        raise HTTPException(status_code=400, detail="User exists")
    data = generate_user(user.user_id, [user.user_type])
    db_users[user.user_id] = data
    return {"message": "User created", "user": data}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id not in db_users:
        raise HTTPException(status_code=404, detail="User not found")
    return db_users[user_id]

@app.post("/locations/")
def create_location(loc: LocationCreate):
    if loc.location_id in db_locations:
        raise HTTPException(status_code=400, detail="Location exists")
    data = generate_location(loc.location_id, [])
    db_locations[loc.location_id] = data
    return {"message": "Location created", "location": data}

@app.get("/locations/{location_id}")
def get_location(location_id: int):
    if location_id not in db_locations:
        raise HTTPException(status_code=404, detail="Location not found")
    return db_locations[location_id]

@app.post("/property_types/")
def create_property_type(pt: PropertyTypeCreate):
    if pt.type_id in db_property_types:
        raise HTTPException(status_code=400, detail="Type exists")
    data = generate_property_type(pt.type_id, [])
    db_property_types[pt.type_id] = data
    return {"message": "Property type created", "property_type": data}

@app.get("/property_types/{type_id}")
def get_property_type(type_id: int):
    if type_id not in db_property_types:
        raise HTTPException(status_code=404, detail="Type not found")
    return db_property_types[type_id]

@app.post("/properties/")
def create_property(prop: PropertyCreate):
    if prop.property_id in db_properties:
        raise HTTPException(status_code=400, detail="Property exists")
    data = generate_property(
        prop.property_id,
        prop.user_id,
        prop.location_id,
        list(db_property_types.values()),
        list(db_property_types.values()),
        list(db_locations.values()),
        list(db_property_types.values()),
    )
    db_properties[prop.property_id] = data
    return {"message": "Property created", "property": data}

@app.get("/properties/{property_id}")
def get_property(property_id: int):
    if property_id not in db_properties:
        raise HTTPException(status_code=404, detail="Property not found")
    return db_properties[property_id]

@app.post("/images/")
def create_image(img: ImageCreate):
    if img.image_id in db_images:
        raise HTTPException(status_code=400, detail="Image exists")
    data = generate_image(img.image_id, img.property_id)
    db_images[img.image_id] = data
    return {"message": "Image created", "image": data}

@app.get("/images/{image_id}")
def get_image(image_id: int):
    if image_id not in db_images:
        raise HTTPException(status_code=404, detail="Image not found")
    return db_images[image_id]

@app.get("/images/")
def list_images():
    return list(db_images.values())
