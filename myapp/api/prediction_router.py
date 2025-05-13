# backend/prediction_router.py

from pathlib import Path
from typing import List

import joblib
import pandas as pd
from fastapi import APIRouter, HTTPException, Depends
from database.database import get_db
from sqlalchemy.orm import Session
from database.models import Location, User, PropertyType
from database.schema import PropertyBase, CoxPredictionBase, PredictionBase, PricePrediction,SaleCoxPrediction ,RentCoxPrediction

# ────────────────────────────────────────────────────────────────────────────────
# Locate model artifacts (mounted by docker-compose)
# ────────────────────────────────────────────────────────────────────────────────
BASE_DIR  = Path(__file__).resolve().parent
PKL_DIR   = BASE_DIR / "models"

rent_model  = joblib.load(PKL_DIR / "rent_price_model.pkl")
sales_model = joblib.load(PKL_DIR / "sell_price_model.pkl")
cox_model   = joblib.load(PKL_DIR / "cox_model.pkl")

# ────────────────────────────────────────────────────────────────────────────────
# Extract feature names used at training
# ────────────────────────────────────────────────────────────────────────────────
def _get_features(m) -> List[str]:
    """
    Return the exact list of feature names the sklearn pipeline expects.
    Raises if `feature_names_in_` is missing (older model).
    """
    if hasattr(m, "feature_names_in_"):
        return list(m.feature_names_in_)
    raise AttributeError("Model missing `feature_names_in_`. Retrain with sklearn>=1.0.")

RENT_FEATURES = _get_features(rent_model)
SALE_FEATURES = _get_features(sales_model)
COX_FEATURES  = list(cox_model.params_.index)

CATEGORICAL_FEATURES = ["district", "renovation_status"]

# ────────────────────────────────────────────────────────────────────────────────
# FastAPI router for ML predictions
# ────────────────────────────────────────────────────────────────────────────────
router = APIRouter(prefix="/predict", tags=["Prediction"])


def _to_df(item: PropertyBase) -> pd.DataFrame:
    """
    Convert the flat Pydantic model into a one-row DataFrame.

    The loaded Pipeline (rent_model/sales_model) will handle any
    categorical encoding internally.
    """
    return pd.DataFrame([item.dict()])


@router.post(
    "/rent-cox",
    response_model=RentCoxPrediction,
    summary="Predict monthly rent and probability of sale"
)
def predict_rent_and_cox(
    data: PropertyBase,
    db: Session = Depends(get_db)
):
    try:
        # — prepare X for price models —
        X = _to_df(data)
        loc = db.query(Location).filter(Location.location_id == data.location_id).first()
        if not loc:
            raise HTTPException(status_code=400, detail="Invalid location_id")
        X["district"] = loc.district

        # — predict both rent & sale for Cox inputs —
        rent_price = float(rent_model.predict(X)[0])
        sell_price = float(sales_model.predict(X)[0])

        # — build the Cox input frame —
        df_cox = pd.DataFrame([data.dict()])[[
            "size_sqm", "rooms", "floor", "year_built"
        ]].copy()
        df_cox["district"] = loc.district
        df_cox["renovation_status"] = data.renovation_status
        df_cox["predicted_sell_price"] = sell_price
        df_cox["predicted_rent_price"] = rent_price

        # — one-hot encode and align to model covariates —
        df_encoded = pd.get_dummies(
            df_cox,
            columns=CATEGORICAL_FEATURES,
            drop_first=True
        )
        df_ready = df_encoded.reindex(columns=COX_FEATURES, fill_value=0)

        # — predict survival → probability sold by t=150 days —
        surv = cox_model.predict_survival_function(df_ready, times=[150])
        prob = float(1 - surv.loc[150].values[0])

        return {
            "predicted_rent_price": rent_price,
            "prob_sold_within_5_months": prob
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/sale-cox",
    response_model=SaleCoxPrediction,
    summary="Predict sale price and probability of sale"
)
def predict_sale_and_cox(
    data: PropertyBase,
    db: Session = Depends(get_db)
):
    try:
        # — prepare X for price models —
        X = _to_df(data)
        loc = db.query(Location).filter(Location.location_id == data.location_id).first()
        if not loc:
            raise HTTPException(status_code=400, detail="Invalid location_id")
        X["district"] = loc.district

        # — predict both sale & rent for Cox inputs —
        sell_price = float(sales_model.predict(X)[0])
        rent_price = float(rent_model.predict(X)[0])

        # — build the Cox input frame —
        df_cox = pd.DataFrame([data.dict()])[[
            "size_sqm", "rooms", "floor", "year_built"
        ]].copy()
        df_cox["district"] = loc.district
        df_cox["renovation_status"] = data.renovation_status
        df_cox["predicted_sell_price"] = sell_price
        df_cox["predicted_rent_price"] = rent_price

        # — one-hot encode and align to model covariates —
        df_encoded = pd.get_dummies(
            df_cox,
            columns=CATEGORICAL_FEATURES,
            drop_first=True
        )
        df_ready = df_encoded.reindex(columns=COX_FEATURES, fill_value=0)

        # — predict survival → probability sold by t=150 days —
        surv = cox_model.predict_survival_function(df_ready, times=[150])
        prob = float(1 - surv.loc[150].values[0])

        return {
            "predicted_sale_price": sell_price,
            "prob_sold_within_5_months": prob
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))