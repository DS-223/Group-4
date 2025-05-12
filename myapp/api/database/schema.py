from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal

# User schemas
class UserBase(BaseModel):
    user_id: int
    user_type: Optional[str]
    username: Optional[str]
    email: Optional[str]
    phone_number: Optional[str]

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    user_type: Optional[str] = None



class LocationBase(BaseModel):
    location_id: int
    region: Optional[str]
    city: Optional[str]
    district: Optional[str]

    class Config:
        from_attributes= True


class LocationCreate(BaseModel):
    region: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None

# PropertyType schemas

class PropertyTypeBase(BaseModel):
    type_id: int
    type_name: str

    class Config:
        from_attributes= True
    
class PropertyTypeCreate(BaseModel):
    type_name: str

# Property schemas

class PropertyBase(BaseModel):
    property_id: int
    type_id: int
    user_id: int
    location_id: int
    title: Optional[str]
    deal_type: Optional[str]
    status: Optional[str]
    post_date: Optional[date]
    sell_date: Optional[date]
    size_sqm: Optional[float]
    floor: Optional[int]
    rooms: Optional[int]
    year_built: Optional[int]
    renovation_status: Optional[str]
    estimated_saleprice: Optional[int]
    estimated_rentprice: Optional[int]

    class Config:
        from_attributes= True


class PropertyCreate(BaseModel):
    title: Optional[str] = None
    deal_type: Optional[str] = None
    status: Optional[str] = None
    post_date: Optional[date] = None
    sell_date: Optional[date] = None
    size_sqm: Optional[float] = None
    floor: Optional[int] = None
    rooms: Optional[int] = None
    year_built: Optional[int] = None
    renovation_status: Optional[str] = None
    estimated_saleprice: Optional[int] = None
    estimated_rentprice: Optional[int] = None


# Image schemas
class ImageBase(BaseModel):
    image_id: int
    property_id: int

    image_url: str

    class Config:
        from_attributes= True

class ImageCreate(BaseModel):
    image_url: str
    

#Prediction schemas
class PredictionBase(BaseModel):
    property_id: int
    prediction_id: int
    predicted_sell_price: int
    predicted_rent_price: int
    prob_sold_within_5_months: float

    class Config:
        from_attributes = True


class PredictionCreate(BaseModel):
    predicted_sell_price: int
    predicted_rent_price: int
    prob_sold_within_5_months: float


class CoxPredictionBase(BaseModel):
    prob_sold_within_5_months: float
