from pydantic import BaseModel, Field

class PropertyFeatures(BaseModel):
    size_sqm:    float  = Field(..., example=75.0, description="Area in square meters")
    rooms:       int    = Field(..., example=3,   description="Number of rooms")
    floor:       int    = Field(..., example=2,   description="Floor number")
    year_built:  int    = Field(..., example=2010,description="Year the building was completed")
    district:    str    = Field(..., example="Kentron",           description="Administrative district")
    renovation_status: str = Field(..., example="Partially Renovated",
                                     description="Renovation state of the property")

class PricePrediction(BaseModel):
    predicted_price: float = Field(..., example=125000.0,
                                   description="Model-predicted price (AMD)")

class CoxPrediction(BaseModel):
    prob_sold_within_5_months: float = Field(..., example=0.42,
                                              description="Probability of sale by 150 days")
