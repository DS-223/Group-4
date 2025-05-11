from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal

# User schemas
class UserBase(BaseModel):
    user_id: int
    user_type: str

class UserCreate(UserBase):
    username: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    user_type: Optional[str] = None

class User(UserBase):
    username: Optional[str]
    email: Optional[str]
    phone_number: Optional[str]
    user_type: Optional[str]
    
    class Config:
        from_attributes= True

# Location schemas
class LocationBase(BaseModel):
    location_id: int

class LocationCreate(LocationBase):
    region: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None

class Location(LocationBase):
    region: Optional[str]
    city: Optional[str]
    district: Optional[str]

    class Config:
        from_attributes= True

# PropertyType schemas
class PropertyTypeBase(BaseModel):
    type_id: int
    type_name: str

class PropertyTypeCreate(PropertyTypeBase):
    pass

class PropertyType(PropertyTypeBase):
    class Config:
        from_attributes= True

# Property schemas
class PropertyBase(BaseModel):
    property_id: int
    type_id: int
    user_id: int
    location_id: int

class PropertyCreate(PropertyBase):
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
    estimated_saleprice: Optional[Decimal] = None
    esimated_rentprice: Optional[Decimal] = None

class Property(PropertyBase):
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
    estimated_saleprice: Optional[Decimal]
    esimated_rentprice: Optional[Decimal]

    class Config:
        from_attributes= True

# Image schemas
class ImageBase(BaseModel):
    image_id: int
    property_id: int

class ImageCreate(ImageBase):
    image_url: str

class Image(ImageBase):
    image_url: str

    class Config:
        from_attributes= True

#Prediction schemas
class PredictionBase(BaseModel):
    property_id: int

class PredictionCreate(PredictionBase):
    predicted_sell_price: float
    predicted_rent_price: float
    prob_sold_within_5_months: float

class Prediction(PredictionBase):
    predicted_sell_price: float
    predicted_rent_price: float
    prob_sold_within_5_months: float

    class Config:
        from_attributes= True


#ML prediction output schemas
class PricePrediction(BaseModel):
    predicted_price: float

class CoxPrediction(BaseModel):
    prob_sold_within_5_months: float
