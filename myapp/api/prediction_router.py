# backend/prediction_router.py

from pathlib import Path
from typing import List

import joblib
import pandas as pd
from fastapi import APIRouter, HTTPException

from database.schema import Property
from database.engine import engine
from database.database import Base

Base.metadata.create_all(bind=engine)
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

# ────────────────────────────────────────────────────────────────────────────────
# FastAPI router for ML predictions
# ────────────────────────────────────────────────────────────────────────────────
router = APIRouter(prefix="/predict", tags=["Prediction"])


def _to_df(item: Property) -> pd.DataFrame:
    """
    Convert the flat Pydantic model into a one-row DataFrame.

    The loaded Pipeline (rent_model/sales_model) will handle any
    categorical encoding internally.
    """
    return pd.DataFrame([item.dict()])


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
