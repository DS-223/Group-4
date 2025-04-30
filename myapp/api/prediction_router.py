from pathlib import Path
import joblib
import pandas as pd
from fastapi import APIRouter, HTTPException
from app.schemas.prediction import PropertyFeatures, PricePrediction   # noqa: F401

router = APIRouter(prefix="/predict", tags=["Prediction"])

# ---------- load artefacts once ----------
ROOT_DIR   = Path(__file__).resolve().parents[2]   # …/GROUP-4
MODEL_DIR  = ROOT_DIR / "model"
CSV_PATH   = MODEL_DIR / "property_ml_ready.csv"

rent_model  = joblib.load(MODEL_DIR / "rent_price_model.pkl")
sales_model = joblib.load(MODEL_DIR / "sales_price_model.pkl")

# recreate training column layout so RFs get identical order
CAT_COLS = ['district', 'type_name', 'status', 'renovation_status']
TRAIN_DF = pd.get_dummies(pd.read_csv(CSV_PATH).dropna(), columns=CAT_COLS)
TARGETS  = ['estimated_rentprice', 'models/estimated_saleprice', 'id']
EXPECTED = [c for c in TRAIN_DF.columns if c not in TARGETS]

def _prepare_row(p: PropertyFeatures) -> pd.DataFrame:
    df = pd.DataFrame([p.dict()])
    df = pd.get_dummies(df, columns=CAT_COLS)
    # align to training columns – unseen categories become 0s
    df = df.reindex(columns=EXPECTED, fill_value=0)
    return df

# --------------- endpoints ----------------
@router.post("/rent", response_model=PricePrediction)
def predict_rent(payload: PropertyFeatures):
    try:
        price = float(rent_model.predict(_prepare_row(payload))[0])
        return {"predicted_price": price}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sale", response_model=PricePrediction)
def predict_sale(payload: PropertyFeatures):
    try:
        price = float(sales_model.predict(_prepare_row(payload))[0])
        return {"predicted_price": price}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
