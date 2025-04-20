import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib  # for saving/loading models

# Load and clean the data
df = pd.read_csv('property_ml_ready.csv')
df.dropna(inplace=True)
df.drop_duplicates(inplace=True)

# Define categorical columns
categorical_cols = ['district', 'type_name', 'status', 'renovation_status']

# One-hot encode categorical columns
df_encoded = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

# Define columns
exclude_columns = ['estimated_rent_price', 'estimated_sales_price', 'id']
feature_columns = [col for col in df_encoded.columns if col not in exclude_columns]

# ----------------- Rent Price Model -----------------
X_rent = df_encoded[feature_columns]
y_rent = df_encoded['estimated_rentprice']
X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(X_rent, y_rent, test_size=0.2, random_state=42)

model_rent = RandomForestRegressor(n_estimators=100, random_state=42)
model_rent.fit(X_train_r, y_train_r)

# Save Rent model
joblib.dump(model_rent, 'rent_price_model.pkl')

# Evaluate
y_pred_r = model_rent.predict(X_test_r)
print("\n--- Rent Price Model Evaluation ---")
print("MAE:", mean_absolute_error(y_test_r, y_pred_r))
print("RMSE:", np.sqrt(mean_squared_error(y_test_r, y_pred_r)))
print("R² Score:", r2_score(y_test_r, y_pred_r))

# ----------------- Sales Price Model -----------------
X_sales = df_encoded[feature_columns]
y_sales = df_encoded['models/estimated_saleprice']
X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(X_sales, y_sales, test_size=0.2, random_state=42)

model_sales = RandomForestRegressor(n_estimators=100, random_state=42)
model_sales.fit(X_train_s, y_train_s)

# Save Sales model
joblib.dump(model_sales, 'models/sales_price_model.pkl')

# Evaluate
y_pred_s = model_sales.predict(X_test_s)
print("\n--- Sales Price Model Evaluation ---")
print("MAE:", mean_absolute_error(y_test_s, y_pred_s))
print("RMSE:", np.sqrt(mean_squared_error(y_test_s, y_pred_s)))
print("R² Score:", r2_score(y_test_s, y_pred_s))
