from pathlib import Path
from typing import List

import joblib
import pandas as pd
from fastapi import APIRouter, HTTPException

from schemas.prediction import PropertyFeatures, PricePrediction, CoxPrediction

# ────────────────────────────────────────────────────────────────────────────────
# Locate artefacts (mounted via docker-compose)
# ────────────────────────────────────────────────────────────────────────────────
BASE_DIR  = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "model"
PKL_DIR   = MODEL_DIR / "models"

rent_model  = joblib.load(PKL_DIR / "rent_price_model.pkl")   # this is a Pipeline
sales_model = joblib.load(PKL_DIR / "sell_price_model.pkl")   # also a Pipeline
cox_model   = joblib.load(PKL_DIR / "cox_model.pkl")          # lifelines CoxPHFitter

# ────────────────────────────────────────────────────────────────────────────────
# Extract feature names used at training
# ────────────────────────────────────────────────────────────────────────────────
def _get_features(m) -> List[str]:
    if hasattr(m, "feature_names_in_"):
        return list(m.feature_names_in_)
    raise AttributeError("Model missing `feature_names_in_`. Retrain with sklearn>=1.0.")

RENT_FEATURES = _get_features(rent_model)   # ['size_sqm','rooms','floor','year_built','district','renovation_status']
SALE_FEATURES = _get_features(sales_model)
COX_FEATURES  = list(cox_model.params_.index)

# ────────────────────────────────────────────────────────────────────────────────
# FastAPI router
# ────────────────────────────────────────────────────────────────────────────────
router = APIRouter(prefix="/predict", tags=["Prediction"])

# ────────────────────────────────────────────────────────────────────────────────
# Helper: build raw DataFrame for pipeline-based models
# ────────────────────────────────────────────────────────────────────────────────
def _to_df(item: PropertyFeatures) -> pd.DataFrame:
    """
    Return a single-row DataFrame with exactly the fields in PropertyFeatures.
    The Pipeline loaded from rent_model/sales_model will handle encoding.
    """
    return pd.DataFrame([item.dict()])

# ────────────────────────────────────────────────────────────────────────────────
# POST /predict/rent
# ────────────────────────────────────────────────────────────────────────────────
@router.post("/rent", response_model=PricePrediction)
def predict_rent(data: PropertyFeatures):
    try:
        X = _to_df(data)
        price = float(rent_model.predict(X)[0])
        return {"predicted_price": price}
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))

# ────────────────────────────────────────────────────────────────────────────────
# POST /predict/sale
# ────────────────────────────────────────────────────────────────────────────────
@router.post("/sale", response_model=PricePrediction)
def predict_sale(data: PropertyFeatures):
    try:
        X = _to_df(data)
        price = float(sales_model.predict(X)[0])
        return {"predicted_price": price}
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))

# ────────────────────────────────────────────────────────────────────────────────
# POST /predict/cox
# ────────────────────────────────────────────────────────────────────────────────
@router.post("/cox", response_model=CoxPrediction)
def predict_cox(data: PropertyFeatures):
    try:
        # 1) Get sale & rent preds
        Xsale = _to_df(data)
        sell_price = float(sales_model.predict(Xsale)[0])
        Xrent = _to_df(data)
        rent_price = float(rent_model.predict(Xrent)[0])

        # 2) Build Cox input from raw dict + preds
        df_cox = pd.DataFrame([data.dict()])
        df_cox["predicted_sell_price"] = sell_price
        df_cox["predicted_rent_price"] = rent_price

        # 3) One-hot encode and align to training columns
        df_cox = pd.get_dummies(df_cox)
        df_cox = df_cox.reindex(columns=COX_FEATURES, fill_value=0)

        # 4) Compute survival at t=150
        surv = cox_model.predict_survival_function(df_cox, times=[150])
        prob = float(1.0 - surv.loc[150].values[0])

        return {"prob_sold_within_5_months": prob}
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))
