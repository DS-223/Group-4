from pydantic import BaseModel, Field
from typing import Optional

class PropertyFeatures(BaseModel):
    district: str                 = Field(example="Kentron")
    type_name: str                = Field(example="Apartment")
    status: str                   = Field(example="Resale")
    renovation_status: str        = Field(example="Newly Renovated")
    area: float                   = Field(example=75.0)
    num_rooms: int                = Field(example=2)
    longitude: Optional[float]    = Field(example=44.51)
    latitude:  Optional[float]    = Field(example=40.18)

class PricePrediction(BaseModel):
    predicted_price: float
