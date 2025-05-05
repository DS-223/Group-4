# # backend/prediction_router.py

# from pathlib import Path
# from typing import List

# import joblib
# import pandas as pd
# from fastapi import APIRouter, HTTPException

# from schemas.prediction import PropertyFeatures, PricePrediction, CoxPrediction

# # ────────────────────────────────────────────────────────────────────────────────
# # Locate model artifacts (mounted by docker-compose)
# # ────────────────────────────────────────────────────────────────────────────────
# BASE_DIR  = Path(__file__).resolve().parent
# MODEL_DIR = BASE_DIR / "model"
# PKL_DIR   = MODEL_DIR / "models"

# rent_model  = joblib.load(PKL_DIR / "rent_price_model.pkl")
# sales_model = joblib.load(PKL_DIR / "sell_price_model.pkl")
# cox_model   = joblib.load(PKL_DIR / "cox_model.pkl")

# # ────────────────────────────────────────────────────────────────────────────────
# # Extract feature names used at training
# # ────────────────────────────────────────────────────────────────────────────────
# def _get_features(m) -> List[str]:
#     """
#     Return the exact list of feature names the sklearn pipeline expects.
#     Raises if `feature_names_in_` is missing (older model).
#     """
#     if hasattr(m, "feature_names_in_"):
#         return list(m.feature_names_in_)
#     raise AttributeError("Model missing `feature_names_in_`. Retrain with sklearn>=1.0.")

# RENT_FEATURES = _get_features(rent_model)
# SALE_FEATURES = _get_features(sales_model)
# COX_FEATURES  = list(cox_model.params_.index)

# # ────────────────────────────────────────────────────────────────────────────────
# # FastAPI router for ML predictions
# # ────────────────────────────────────────────────────────────────────────────────
# router = APIRouter(prefix="/predict", tags=["Prediction"])


# def _to_df(item: PropertyFeatures) -> pd.DataFrame:
#     """
#     Convert the flat Pydantic model into a one-row DataFrame.

#     The loaded Pipeline (rent_model/sales_model) will handle any
#     categorical encoding internally.
#     """
#     return pd.DataFrame([item.dict()])


# @router.post("/rent", response_model=PricePrediction, summary="Predict monthly rent")
# def predict_rent(data: PropertyFeatures):
#     """
#     Predict the monthly rent price for a property.

#     - **data**: JSON body matching `PropertyFeatures` schema.

#     Returns:
#     - **predicted_price**: float, the model’s rent estimate.
#     """
#     try:
#         X = _to_df(data)
#         price = float(rent_model.predict(X)[0])
#         return {"predicted_price": price}
#     except Exception as err:
#         raise HTTPException(status_code=400, detail=str(err))


# @router.post("/sale", response_model=PricePrediction, summary="Predict sale price")
# def predict_sale(data: PropertyFeatures):
#     """
#     Predict the sale price for a property.

#     - **data**: JSON body matching `PropertyFeatures` schema.

#     Returns:
#     - **predicted_price**: float, the model’s sales estimate.
#     """
#     try:
#         X = _to_df(data)
#         price = float(sales_model.predict(X)[0])
#         return {"predicted_price": price}
#     except Exception as err:
#         raise HTTPException(status_code=400, detail=str(err))


# @router.post("/cox", response_model=CoxPrediction, summary="Predict probability of sale")
# def predict_cox(data: PropertyFeatures):
#     """
#     Estimate the probability a property will sell within 150 days.

#     Steps:
#     1. Use sale and rent pipelines to predict prices.
#     2. Build a DataFrame including the original features plus those predictions.
#     3. One-hot encode and align to Cox model’s training columns.
#     4. Compute survival function at t=150 and return 1 - S(150).

#     - **data**: JSON body matching `PropertyFeatures` schema.

#     Returns:
#     - **prob_sold_within_5_months**: float in [0,1].
#     """
#     try:
#         # 1) Price predictions
#         Xsale = _to_df(data)
#         sell_price = float(sales_model.predict(Xsale)[0])
#         Xrent = _to_df(data)
#         rent_price = float(rent_model.predict(Xrent)[0])

#         # 2) Cox DataFrame
#         df_cox = pd.DataFrame([data.dict()])
#         df_cox["predicted_sell_price"] = sell_price
#         df_cox["predicted_rent_price"] = rent_price

#         # 3) Encoding & alignment
#         df_cox = pd.get_dummies(df_cox)
#         df_cox = df_cox.reindex(columns=COX_FEATURES, fill_value=0)

#         # 4) Survival probability
#         surv = cox_model.predict_survival_function(df_cox, times=[150])
#         prob = float(1.0 - surv.loc[150].values[0])

#         return {"prob_sold_within_5_months": prob}
#     except Exception as err:
#         raise HTTPException(status_code=400, detail=str(err))
# backend/prediction_router.py

# backend/prediction_router.py

from pathlib import Path
from typing import List

import joblib
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# ──────────────────────────────
# Database imports
# ──────────────────────────────
from etl.database.database import get_db                        # :contentReference[oaicite:0]{index=0}:contentReference[oaicite:1]{index=1}
from etl.database.models   import Property as PropertyModel    # :contentReference[oaicite:2]{index=2}:contentReference[oaicite:3]{index=3}

# ──────────────────────────────
# Response schemas
# ──────────────────────────────
from schemas.prediction import PricePrediction, CoxPrediction

# ──────────────────────────────
# Model artifacts (mounted via docker-compose)
# ──────────────────────────────
BASE_DIR  = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "model"
PKL_DIR   = MODEL_DIR / "models"

rent_model  = joblib.load(PKL_DIR / "rent_price_model.pkl")
sales_model = joblib.load(PKL_DIR / "sell_price_model.pkl")
cox_model   = joblib.load(PKL_DIR / "cox_model.pkl")

# ──────────────────────────────
# Extract model feature lists
# ──────────────────────────────
def _get_features(m) -> List[str]:
    """
    Grab the exact feature names the sklearn pipeline expects.
    Raises if the model was trained without storing `feature_names_in_`.
    """
    if hasattr(m, "feature_names_in_"):
        return list(m.feature_names_in_)
    raise AttributeError("Model missing `feature_names_in_`; retrain with sklearn>=1.0.")

RENT_FEATURES = _get_features(rent_model)
SALE_FEATURES = _get_features(sales_model)
COX_FEATURES  = list(cox_model.params_.index)

# ──────────────────────────────
# FastAPI router
# ──────────────────────────────
router = APIRouter(prefix="/predict", tags=["Prediction"])

def _build_feature_df(prop: PropertyModel) -> pd.DataFrame:
    """
    Extract the six ML features from a Property ORM instance:
      • size_sqm
      • rooms
      • floor
      • year_built
      • district  (via prop.location.district)
      • renovation_status

    Returns a one-row DataFrame; pipelines handle any further encoding.
    """
    raw = {
        "size_sqm":          prop.size_sqm,
        "rooms":             prop.rooms,
        "floor":             prop.floor,
        "year_built":        prop.year_built,
        "district":          prop.location.district,
        "renovation_status": prop.renovation_status,
    }
    return pd.DataFrame([raw])


@router.get("/rent/{property_id}", response_model=PricePrediction, summary="Predict monthly rent")
def predict_rent(property_id: int, db: Session = Depends(get_db)):
    """
    Fetch a property by ID and predict its monthly rent.

    - **property_id**: integer primary key in the `properties` table.

    Returns:
    - **predicted_price**: float – the rental price estimate from the RandomForest pipeline.
    """
    prop = db.get(PropertyModel, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail=f"Property {property_id} not found")

    df = _build_feature_df(prop)
    try:
        price = float(rent_model.predict(df)[0])
        return {"predicted_price": price}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sale/{property_id}", response_model=PricePrediction, summary="Predict sale price")
def predict_sale(property_id: int, db: Session = Depends(get_db)):
    """
    Fetch a property by ID and predict its sale price.

    - **property_id**: integer primary key in the `properties` table.

    Returns:
    - **predicted_price**: float – the sales price estimate from the RandomForest pipeline.
    """
    prop = db.get(PropertyModel, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail=f"Property {property_id} not found")

    df = _build_feature_df(prop)
    try:
        price = float(sales_model.predict(df)[0])
        return {"predicted_price": price}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/cox/{property_id}", response_model=CoxPrediction, summary="Predict sale probability")
def predict_cox(property_id: int, db: Session = Depends(get_db)):
    """
    Estimate the probability a property will sell within 150 days.

    1. Load the property by ID.
    2. Run the sale & rent pipelines to get price predictions.
    3. Build a DataFrame of original features + those two prices.
    4. One-hot encode & align to Cox model’s training columns.
    5. Compute survival at t=150 and return 1 - S(150).

    - **property_id**: integer PK in `properties`.

    Returns:
    - **prob_sold_within_5_months**: float ∈ [0,1].
    """
    prop = db.get(PropertyModel, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail=f"Property {property_id} not found")

    df_base = _build_feature_df(prop)
    sell_price = float(sales_model.predict(df_base)[0])
    rent_price = float(rent_model.predict(df_base)[0])

    # assemble Cox inputs
    cox_input = {**df_base.iloc[0].to_dict(),
                 "predicted_sell_price": sell_price,
                 "predicted_rent_price":  rent_price}
    df_cox = pd.DataFrame([cox_input])
    df_cox = pd.get_dummies(df_cox)
    df_cox = df_cox.reindex(columns=COX_FEATURES, fill_value=0)

    try:
        surv = cox_model.predict_survival_function(df_cox, times=[150])
        prob = float(1.0 - surv.loc[150].values[0])
        return {"prob_sold_within_5_months": prob}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
