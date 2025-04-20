from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from etl.database.data_generate import (
    generate_user,
    generate_property,
    generate_location,
    generate_property_type,
    generate_image,
)

app = FastAPI()

# Dummy data storage
users = {}
properties = {}
locations = {}
property_types = ["Apartment", "House", "Commercial"]
deal_types = ["Sale", "Rent"]
renovation_statuses = ["Newly Renovated", "Not Renovated", "Partially Renovated"]
districts = ["Kentron", "Ajapnyak", "Nubarashen", "Arabkir"]

# Models for API requests
class User(BaseModel):
    user_id: int
    user_type: str

class Property(BaseModel):
    property_id: int
    user_id: int
    location_id: int

# Endpoints
@app.post("/users/")
def create_user(user: User):
    if user.user_id in users:
        raise HTTPException(status_code=400, detail="User already exists")
    users[user.user_id] = generate_user(user.user_id, [user.user_type])
    return {"message": "User created", "user": users[user.user_id]}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": users[user_id]}

@app.post("/properties/")
def create_property(property: Property):
    if property.property_id in properties:
        raise HTTPException(status_code=400, detail="Property already exists")
    if property.user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    location_id = property.location_id
    if location_id not in locations:
        locations[location_id] = generate_location(location_id, districts)
    properties[property.property_id] = generate_property(
        property.property_id,
        property.user_id,
        location_id,
        property_types,
        deal_types,
        renovation_statuses,
        districts,
    )
    return {"message": "Property created", "property": properties[property.property_id]}

@app.get("/properties/{property_id}")
def get_property(property_id: int):
    if property_id not in properties:
        raise HTTPException(status_code=404, detail="Property not found")
    return {"property": properties[property_id]}

@app.get("/locations/{location_id}")
def get_location(location_id: int):
    if location_id not in locations:
        raise HTTPException(status_code=404, detail="Location not found")
    return {"location": locations[location_id]}

@app.get("/properties/")
def list_properties():
    return {"properties": list(properties.values())}