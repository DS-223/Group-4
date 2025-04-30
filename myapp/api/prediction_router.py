from pathlib import Path
from typing import List

import joblib
import pandas as pd
from fastapi import APIRouter, HTTPException

from schemas.prediction import PropertyFeatures, PricePrediction

# ────────────────────────────────────────────────────────────────
# Locate artefacts
# container path:  /backend/model/…   (mounted by docker-compose)
# ────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent          # /backend
MODEL_DIR  = BASE_DIR / "model"                       # /backend/model
PKL_DIR    = MODEL_DIR / "models"                     # /backend/model/models

rent_model  = joblib.load(PKL_DIR / "rent_price_model.pkl")
sales_model = joblib.load(PKL_DIR / "sales_price_model.pkl")

# training CSV is optional (kept for reference / later inspection)
CSV_PATH = MODEL_DIR / "property_ml_ready.csv"

# ────────────────────────────────────────────────────────────────
# Canonical feature lists taken directly from the trained models
# ────────────────────────────────────────────────────────────────
def _get_features(m) -> List[str]:
    """Return the feature names exactly as the model saw them at fit time."""
    if hasattr(m, "feature_names_in_"):          # scikit-learn ≥ 1.0
        return list(m.feature_names_in_)
    raise AttributeError(
        "Model is missing 'feature_names_in_' — it was probably trained with "
        "an older pandas / sklearn. Retrain or hard-code the column list."
    )

RENT_FEATURES = _get_features(rent_model)
SALE_FEATURES = _get_features(sales_model)

# ────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────
def _prepare_row(item: PropertyFeatures, feature_list: List[str]) -> pd.DataFrame:
    """
    → One-row DataFrame with dummies.
    → Columns reordered / zero-filled so they match `feature_list`.
    """
    df = pd.DataFrame([item.dict()])
    df = pd.get_dummies(df)                       # explode categoricals
    df = df.reindex(columns=feature_list, fill_value=0)  # align
    return df


# ────────────────────────────────────────────────────────────────
# FastAPI router
# ────────────────────────────────────────────────────────────────
router = APIRouter(prefix="/predict", tags=["Prediction"])


@router.post("/rent", response_model=PricePrediction)
def predict_rent(payload: PropertyFeatures):
    try:
        X = _prepare_row(payload, RENT_FEATURES)
        price = float(rent_model.predict(X)[0])
        return {"predicted_price": price}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/sale", response_model=PricePrediction)
def predict_sale(payload: PropertyFeatures):
    try:
        X = _prepare_row(payload, SALE_FEATURES)
        price = float(sales_model.predict(X)[0])
        return {"predicted_price": price}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
