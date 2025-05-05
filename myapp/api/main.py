# # backend/main.py

# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from typing import Dict

# # Dummy data generators (replace with DB calls when ready)
# from etl.database.data_generate import (
#     generate_user,
#     generate_property,
#     generate_location,
#     generate_property_type,
#     generate_image,
# )

# # Import ML router
# from prediction_router import router as prediction_router

# app = FastAPI(
#     title="Marketing-Analytics API",
#     description="CRUD stubs + ML predictions (DB integration pending)",
#     version="1.0.0",
# )

# # Mount ML endpoints
# app.include_router(prediction_router)


# # In-memory stores for CRUD stubs
# db_users: Dict[int, dict] = {}
# db_locations: Dict[int, dict] = {}
# db_property_types: Dict[int, dict] = {}
# db_properties: Dict[int, dict] = {}
# db_images: Dict[int, dict] = {}


# class UserCreate(BaseModel):
#     """Schema for creating a new user."""
#     user_id: int
#     user_type: str


# class LocationCreate(BaseModel):
#     """Schema for creating a new location."""
#     location_id: int


# class PropertyTypeCreate(BaseModel):
#     """Schema for creating a new property type."""
#     type_id: int
#     type_name: str


# class PropertyCreate(BaseModel):
#     """Schema for creating a new property."""
#     property_id: int
#     user_id: int
#     location_id: int


# class ImageCreate(BaseModel):
#     """Schema for creating a new image record."""
#     image_id: int
#     property_id: int
#     image_url: str


# @app.post("/users/", summary="Create a new user")
# def create_user(user: UserCreate):
#     """
#     Create a new user entry.

#     - **user_id**: unique integer identifier for the user
#     - **user_type**: category of the user (e.g. Owner, Agent)

#     Returns a message and the generated user record.
#     """
#     if user.user_id in db_users:
#         raise HTTPException(status_code=400, detail="User exists")
#     data = generate_user(user.user_id, [user.user_type])
#     db_users[user.user_id] = data
#     return {"message": "User created", "user": data}


# @app.get("/users/{user_id}", summary="Retrieve an existing user")
# def get_user(user_id: int):
#     """
#     Fetch a user by their ID.

#     - **user_id**: integer ID of the user

#     Returns the user record if found, else 404.
#     """
#     if user_id not in db_users:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_users[user_id]


# @app.post("/locations/", summary="Create a new location")
# def create_location(loc: LocationCreate):
#     """
#     Create a new location entry.

#     - **location_id**: unique integer identifier for the location

#     Returns a message and the generated location data.
#     """
#     if loc.location_id in db_locations:
#         raise HTTPException(status_code=400, detail="Location exists")
#     data = generate_location(loc.location_id, [])
#     db_locations[loc.location_id] = data
#     return {"message": "Location created", "location": data}


# @app.get("/locations/{location_id}", summary="Retrieve a location")
# def get_location(location_id: int):
#     """
#     Fetch a location by its ID.

#     - **location_id**: integer ID of the location

#     Returns the location record if found, else 404.
#     """
#     if location_id not in db_locations:
#         raise HTTPException(status_code=404, detail="Location not found")
#     return db_locations[location_id]


# @app.post("/property_types/", summary="Create a new property type")
# def create_property_type(pt: PropertyTypeCreate):
#     """
#     Create a new property type entry.

#     - **type_id**: unique integer identifier for the type
#     - **type_name**: name of the property type (e.g. Apartment)

#     Returns a message and the generated type record.
#     """
#     if pt.type_id in db_property_types:
#         raise HTTPException(status_code=400, detail="Type exists")
#     data = generate_property_type(pt.type_id, [])
#     db_property_types[pt.type_id] = data
#     return {"message": "Property type created", "property_type": data}


# @app.get("/property_types/{type_id}", summary="Retrieve a property type")
# def get_property_type(type_id: int):
#     """
#     Fetch a property type by its ID.

#     - **type_id**: integer ID of the property type

#     Returns the type record if found, else 404.
#     """
#     if type_id not in db_property_types:
#         raise HTTPException(status_code=404, detail="Type not found")
#     return db_property_types[type_id]


# @app.post("/properties/", summary="Create a new property")
# def create_property(prop: PropertyCreate):
#     """
#     Create a new property entry.

#     - **property_id**: unique integer identifier for the property
#     - **user_id**: integer ID of the owner/agent
#     - **location_id**: integer ID of the property location

#     Returns a message and the generated property record.
#     """
#     if prop.property_id in db_properties:
#         raise HTTPException(status_code=400, detail="Property exists")
#     data = generate_property(
#         prop.property_id,
#         prop.user_id,
#         prop.location_id,
#         list(db_property_types.values()),
#         list(db_property_types.values()),
#         list(db_locations.values()),
#         list(db_property_types.values()),
#     )
#     db_properties[prop.property_id] = data
#     return {"message": "Property created", "property": data}


# @app.get("/properties/{property_id}", summary="Retrieve a property")
# def get_property(property_id: int):
#     """
#     Fetch a property by its ID.

#     - **property_id**: integer ID of the property

#     Returns the property record if found, else 404.
#     """
#     if property_id not in db_properties:
#         raise HTTPException(status_code=404, detail="Property not found")
#     return db_properties[property_id]


# @app.post("/images/", summary="Create a new image")
# def create_image(img: ImageCreate):
#     """
#     Create a new image record attached to a property.

#     - **image_id**: unique integer identifier for the image
#     - **property_id**: integer ID of the associated property
#     - **image_url**: URL of the image

#     Returns a message and the generated image record.
#     """
#     if img.image_id in db_images:
#         raise HTTPException(status_code=400, detail="Image exists")
#     data = generate_image(img.image_id, img.property_id)
#     db_images[img.image_id] = data
#     return {"message": "Image created", "image": data}


# @app.get("/images/{image_id}", summary="Retrieve an image")
# def get_image(image_id: int):
#     """
#     Fetch an image record by its ID.

#     - **image_id**: integer ID of the image

#     Returns the image record if found, else 404.
#     """
#     if image_id not in db_images:
#         raise HTTPException(status_code=404, detail="Image not found")
#     return db_images[image_id]


# @app.get("/images/", summary="List all images")
# def list_images():
#     """
#     List all image records currently stored.

#     Returns a list of image objects.
#     """
#     return list(db_images.values())

# backend/main.py
# backend/main.py

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session

from etl.database.database import get_db
from etl.database.models import (
    User    as UserModel,
    Location as LocationModel,
    PropertyType as PropertyTypeModel,
    Property as PropertyModel,
    Image   as ImageModel,
)
from etl.database.data_generate import (
    generate_user,
    generate_location,
    generate_property_type,
    generate_property,
    generate_image,
)

from prediction_router import router as prediction_router

app = FastAPI(
    title="Marketing-Analytics API",
    description="CRUD via Postgres + ML predictions",
    version="1.0.0",
)

app.include_router(prediction_router)


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


# ─── USERS ─────────────────────────────────────────────────────────────

@app.post("/users/", summary="Create a new user")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(UserModel).get(user.user_id):
        raise HTTPException(400, "User already exists")
    payload = generate_user(user.user_id, [user.user_type])
    new = UserModel(**payload)
    db.add(new); db.commit(); db.refresh(new)
    return new.__dict__

@app.get("/users/{user_id}", summary="Fetch a user by ID")
def get_user(user_id: int, db: Session = Depends(get_db)):
    u = db.query(UserModel).get(user_id)
    if not u:
        raise HTTPException(404, "User not found")
    return u.__dict__

@app.get("/users/", summary="List all users", response_model=List[dict])
def list_users(db: Session = Depends(get_db)):
    """
    Return a full list of all users in the database.
    """
    users = db.query(UserModel).all()
    return [u.__dict__ for u in users]


# ─── LOCATIONS ────────────────────────────────────────────────────────

@app.post("/locations/", summary="Create a new location")
def create_location(loc: LocationCreate, db: Session = Depends(get_db)):
    if db.query(LocationModel).get(loc.location_id):
        raise HTTPException(400, "Location already exists")
    payload = generate_location(loc.location_id, [])
    new = LocationModel(**payload)
    db.add(new); db.commit(); db.refresh(new)
    return new.__dict__

@app.get("/locations/{location_id}", summary="Fetch a location by ID")
def get_location(location_id: int, db: Session = Depends(get_db)):
    loc = db.query(LocationModel).get(location_id)
    if not loc:
        raise HTTPException(404, "Location not found")
    return loc.__dict__

@app.get("/locations/", summary="List all locations", response_model=List[dict])
def list_locations(db: Session = Depends(get_db)):
    """
    Return a full list of all locations in the database.
    """
    locs = db.query(LocationModel).all()
    return [l.__dict__ for l in locs]


# ─── PROPERTY TYPES ──────────────────────────────────────────────────

@app.post("/property_types/", summary="Create a new property type")
def create_property_type(pt: PropertyTypeCreate, db: Session = Depends(get_db)):
    if db.query(PropertyTypeModel).get(pt.type_id):
        raise HTTPException(400, "PropertyType already exists")
    new = PropertyTypeModel(type_id=pt.type_id, type_name=pt.type_name)
    db.add(new); db.commit(); db.refresh(new)
    return new.__dict__

@app.get("/property_types/{type_id}", summary="Fetch a property type by ID")
def get_property_type(type_id: int, db: Session = Depends(get_db)):
    t = db.query(PropertyTypeModel).get(type_id)
    if not t:
        raise HTTPException(404, "PropertyType not found")
    return t.__dict__

@app.get("/property_types/", summary="List all property types", response_model=List[dict])
def list_property_types(db: Session = Depends(get_db)):
    """
    Return a full list of all property types in the database.
    """
    types = db.query(PropertyTypeModel).all()
    return [t.__dict__ for t in types]


# ─── PROPERTIES ───────────────────────────────────────────────────────

@app.post("/properties/", summary="Create a new property")
def create_property(prop: PropertyCreate, db: Session = Depends(get_db)):
    if db.query(PropertyModel).get(prop.property_id):
        raise HTTPException(400, "Property already exists")
    # build lists for generation
    types      = [t.type_name for t in db.query(PropertyTypeModel)]
    districts  = [l.district   for l in db.query(LocationModel)]
    deals      = ["Sale", "Rent"]
    renovations = ["Newly Renovated", "Not Renovated", "Partially Renovated"]
    payload = generate_property(
        prop.property_id,
        prop.user_id,
        prop.location_id,
        types, deals, renovations, districts
    )
    new = PropertyModel(**payload)
    db.add(new); db.commit(); db.refresh(new)
    return new.__dict__

@app.get("/properties/{property_id}", summary="Fetch a property by ID")
def get_property(property_id: int, db: Session = Depends(get_db)):
    p = db.query(PropertyModel).get(property_id)
    if not p:
        raise HTTPException(404, "Property not found")
    return p.__dict__

@app.get("/properties/", summary="List all properties", response_model=List[dict])
def list_properties(db: Session = Depends(get_db)):
    """
    Return a full list of all properties in the database.
    """
    props = db.query(PropertyModel).all()
    return [p.__dict__ for p in props]


# ─── IMAGES ─────────────────────────────────────────────────────────

@app.post("/images/", summary="Create a new image")
def create_image(img: ImageCreate, db: Session = Depends(get_db)):
    if db.query(ImageModel).get(img.image_id):
        raise HTTPException(400, "Image already exists")
    payload = generate_image(img.image_id, img.property_id)
    new = ImageModel(**payload)
    db.add(new); db.commit(); db.refresh(new)
    return new.__dict__

@app.get("/images/{image_id}", summary="Fetch an image by ID")
def get_image(image_id: int, db: Session = Depends(get_db)):
    im = db.query(ImageModel).get(image_id)
    if not im:
        raise HTTPException(404, "Image not found")
    return im.__dict__

@app.get("/images/", summary="List all images", response_model=List[dict])
def list_images(db: Session = Depends(get_db)):
    """
    Return a full list of all images in the database.
    """
    imgs = db.query(ImageModel).all()
    return [i.__dict__ for i in imgs]
