import pandas as pd
import joblib
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, r2_score
from lifelines import CoxPHFitter
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database.database import engine
from pathlib import Path
from sqlalchemy import func
from database.engine import engine
from database.database import Base
from sqlalchemy.types import Integer, Float

# Create all tables
Base.metadata.create_all(bind=engine)


# Connect to database
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()


# Replace old load logic
df = pd.read_sql("SELECT * FROM property_ml_ready", engine)
print(df.head())

#df_property = pd.read_sql("SELECT * FROM properties", engine)
#print(df_property.head())

#df_user = pd.read_sql("SELECT * FROM users", engine)
#print(df_user.head())

if df.empty:
    raise RuntimeError("Failed to load data from database. Exiting model training.")


df['post_date'] = pd.to_datetime(df['post_date'])
df['sell_date'] = pd.to_datetime(df['sell_date'])
today = pd.to_datetime("today")
df['duration'] = (df['sell_date'].fillna(today) - df['post_date']).dt.days
df['event'] = df['sell_date'].notna().astype(int)


# 2. Feature Engineering
def prepare_features(df):
    cat_cols = ['type_name', 'district', 'renovation_status', 'deal_type', 'user_type']
    df_encoded = pd.get_dummies(df, columns=cat_cols, drop_first=True)
    exclude = ['property_id', 'post_date', 'sell_date', 'duration', 'event', 'estimated_rentprice', 'estimated_saleprice']
    features = [col for col in df_encoded.columns if col not in exclude]
    return df_encoded, features

# Folders
script_dir = Path(__file__).parent
output_dir = script_dir / "output"
output_dir.mkdir(exist_ok=True)
models_dir = script_dir / "models"
models_dir.mkdir(exist_ok=True)

# Define features
numerical_features = ['size_sqm', 'rooms', 'floor', 'year_built']
categorical_features = ['district', 'renovation_status']
all_features = numerical_features + categorical_features

# Preprocessor
preprocessor = ColumnTransformer([
    ('num', 'passthrough', numerical_features),
    ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
])

# --- Sell Price Model ---
df_sell = df[df['estimated_saleprice'].notna()]
X_sell = df_sell[all_features]
y_sell = df_sell['estimated_saleprice']

X_sell_train, X_sell_test, y_sell_train, y_sell_test = train_test_split(X_sell, y_sell, test_size=0.2, random_state=42)

sell_pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(random_state=42))
])
sell_pipeline.fit(X_sell_train, y_sell_train)
y_sell_pred = sell_pipeline.predict(X_sell_test)

print("Sell Price Model Evaluation:")
print(f"MAE: {mean_absolute_error(y_sell_test, y_sell_pred):.2f}")
print(f"R²: {r2_score(y_sell_test, y_sell_pred):.2f}")

joblib.dump(sell_pipeline, models_dir / 'sell_price_model.pkl')
df['predicted_sell_price'] = sell_pipeline.predict(df[all_features])

# --- Rent Price Model ---
df_rent = df[df['estimated_rentprice'].notna()]
X_rent = df_rent[all_features]
y_rent = df_rent['estimated_rentprice']

X_rent_train, X_rent_test, y_rent_train, y_rent_test = train_test_split(X_rent, y_rent, test_size=0.2, random_state=42)

rent_pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(random_state=42))
])
rent_pipeline.fit(X_rent_train, y_rent_train)
y_rent_pred = rent_pipeline.predict(X_rent_test)

print("\nRent Price Model Evaluation:")
print(f"MAE: {mean_absolute_error(y_rent_test, y_rent_pred):.2f}")
print(f"R²: {r2_score(y_rent_test, y_rent_pred):.2f}")

joblib.dump(rent_pipeline, models_dir / 'rent_price_model.pkl')
df['predicted_rent_price'] = rent_pipeline.predict(df[all_features])

# --- Cox Model ---
cox_input = df[all_features].copy()
cox_input['predicted_sell_price'] = df['predicted_sell_price']
cox_input['predicted_rent_price'] = df['predicted_rent_price']
cox_input['duration'] = df['duration']
cox_input['event'] = df['event']
cox_input_encoded = pd.get_dummies(cox_input, columns=categorical_features, drop_first=True)

cph = CoxPHFitter()
cph.fit(cox_input_encoded, duration_col='duration', event_col='event')
joblib.dump(cph, models_dir / 'cox_model.pkl')

surv_funcs = cph.predict_survival_function(cox_input_encoded, times=[150])
df['prob_sold_within_5_months'] = 1 - surv_funcs.loc[150].values


# Select only the relevant columns for SQL table
predictions_df = df[['property_id', 'predicted_sell_price', 'predicted_rent_price', 'prob_sold_within_5_months']].copy()

# Add prediction_id column manually
predictions_df = predictions_df.reset_index(drop=True)
predictions_df['prediction_id'] = predictions_df.index + 1

# --- Save Predictions ---
output_cols = ['property_id', 'prediction_id','predicted_sell_price', 'predicted_rent_price', 'prob_sold_within_5_months']
predictions_df[output_cols].to_csv(output_dir / 'predictions.csv', index=False)

print("\n✅ Models trained and saved. Predictions written to 'output/predictions.csv'")


# Define SQL types explicitly (optional but recommended)
sql_dtypes = {
    "prediction_id": Integer(),
    "property_id": Integer(),
    "predicted_sell_price": Float(),
    "predicted_rent_price": Float(),
    "prob_sold_within_5_months": Float()
}

# Insert using pandas.to_sql
predictions_df[output_cols].to_sql(
    name='predictions',
    con=engine,
    if_exists='replace',  # or 'append' to avoid dropping table
    index=False,
    dtype=sql_dtypes
)
print("Predictions saved to PostgreSQL using pandas.to_sql.")
print("Predictions saved to PostgreSQL.")