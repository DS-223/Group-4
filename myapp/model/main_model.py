import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.impute import SimpleImputer
import joblib
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, '../etl/data/property_ml_ready.csv')

try:
    df = pd.read_csv(csv_path)
    print(f"Successfully loaded data from {csv_path}")
    print(f"Data shape: {df.shape}")
except Exception as e:
    print(f"Error loading CSV file: {str(e)}")
    raise

# Data preparation
df['event'] = df['sell_date'].notna().astype(int)  # 1=sold, 0=not sold
df['post_date'] = pd.to_datetime(df['post_date'])
df['sell_date'] = pd.to_datetime(df['sell_date'])
df['days_on_market'] = (df['sell_date'] - df['post_date']).dt.days

# Handle unsold properties
last_date = df['post_date'].max()
df.loc[df['event'] == 0, 'days_on_market'] = (last_date - df.loc[df['event'] == 0, 'post_date']).dt.days

# Feature engineering
categorical_cols = ['type_name', 'district', 'renovation_status', 'deal_type', 'user_type']
df_encoded = pd.get_dummies(df, columns=categorical_cols, drop_first=True)
bool_cols = df_encoded.select_dtypes(include=['bool']).columns
df_encoded[bool_cols] = df_encoded[bool_cols].astype(int)

# Features to exclude - fixed
exclude_columns = [
    'estimated_rentprice', 'estimated_saleprice', 
    'property_id', 'sell_date', 'post_date',
    'event', 'days_on_market'
]
feature_columns = [col for col in df_encoded.columns if col not in exclude_columns]

# Verify all features are numeric
non_numeric = df_encoded[feature_columns].select_dtypes(exclude=['number']).columns
if not non_numeric.empty:
    raise ValueError(f"Non-numeric columns found in features: {list(non_numeric)}")

# Train-test split
X = df_encoded[feature_columns]
y_sell = df_encoded['event']
X_train, X_test, y_train, y_test = train_test_split(X, y_sell, test_size=0.2, random_state=42)

# Train will-it-sell classifier
sell_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
sell_classifier.fit(X_train, y_train)

# Train days-on-market regressor (only on sold properties)
sold_df = df_encoded[df_encoded['event'] == 1]
X_sold = sold_df[feature_columns]
y_days = sold_df['days_on_market']
days_regressor = RandomForestRegressor(n_estimators=100, random_state=42)
days_regressor.fit(X_sold, y_days)

# Train price prediction models
model_rent = RandomForestRegressor(n_estimators=100, random_state=42)
model_sales = RandomForestRegressor(n_estimators=100, random_state=42)

X_rent = df_encoded[feature_columns]
y_rent = df_encoded['estimated_rentprice'].fillna(df_encoded['estimated_rentprice'].median())
model_rent.fit(X_rent, y_rent)

X_sales = df_encoded[feature_columns]
y_sales = df_encoded['estimated_saleprice'].fillna(df_encoded['estimated_saleprice'].median())
model_sales.fit(X_sales, y_sales)

# Prediction function
def predict_property(property_data):
    """Predict all required outputs for a single property"""
    if isinstance(property_data, pd.Series):
        property_data = property_data.values.reshape(1, -1)
    elif isinstance(property_data, np.ndarray):
        property_data = property_data.reshape(1, -1)
    
    # Predict prices
    rent_price = model_rent.predict(property_data)[0]
    sale_price = model_sales.predict(property_data)[0]
    
    # Predict sale probability and timing
    will_sell = sell_classifier.predict(property_data)[0]
    sell_prob = sell_classifier.predict_proba(property_data)[0][1]
    days_to_sale = days_regressor.predict(property_data)[0] if will_sell else np.nan
    
    return {
        'predicted_rent_price': rent_price,
        'predicted_sales_price': sale_price,
        'will_sell': will_sell,
        'sell_probability': sell_prob,
        'days_to_sale': days_to_sale
    }

# Make predictions for all properties
imputer = SimpleImputer(strategy='median')
X_imputed = imputer.fit_transform(df_encoded[feature_columns])

predictions = []
for i in range(X_imputed.shape[0]):
    pred = predict_property(X_imputed[i])
    predictions.append(pred)

# Create final output DataFrame
output_df = df[['property_id', 'post_date']].copy()
output_df['actual_rent_price'] = df['estimated_rentprice']
output_df['actual_sales_price'] = df['estimated_saleprice']
output_df['actual_sold'] = df['event']
output_df['actual_days_on_market'] = df['days_on_market']
output_df['predicted_rent_price'] = [p['predicted_rent_price'] for p in predictions]
output_df['predicted_sales_price'] = [p['predicted_sales_price'] for p in predictions]
output_df['will_sell'] = [p['will_sell'] for p in predictions]
output_df['sell_probability'] = [p['sell_probability'] for p in predictions]
output_df['predicted_days_to_sale'] = [p['days_to_sale'] for p in predictions]
def format_sale_date(row):
    if row['will_sell'] == 1:
        sale_date = (pd.to_datetime(row['post_date']) + 
                   pd.to_timedelta(row['predicted_days_to_sale'], unit='D'))
        return sale_date.date()
    else:
        return "The probability of being sold is very low"

# Apply the formatting
output_df['predicted_sale_date'] = output_df.apply(format_sale_date, axis=1)



# 1. Evaluate the Sale Classifier
print("\n=== Sale Classifier Evaluation ===")
# Cross-validation
cv_scores = cross_val_score(sell_classifier, X, y_sell, cv=5, scoring='accuracy')
print(f"Cross-validation accuracy: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")

# Test set evaluation
y_pred = sell_classifier.predict(X_test)
print(f"Test accuracy: {accuracy_score(y_test, y_pred):.3f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.title('Confusion Matrix - Will Sell Classifier')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()

# 2. Evaluate Days-on-Market Regressor (only on sold properties)
print("\n=== Days-on-Market Regressor Evaluation ===")
# Cross-validation
kf = KFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(days_regressor, X_sold, y_days, cv=kf, 
                          scoring='neg_mean_absolute_error')
print(f"Cross-validation MAE: {-cv_scores.mean():.1f} days ± {-cv_scores.std():.1f}")

# Test set evaluation (only sold properties)
sold_test = df_encoded.loc[y_test[y_test == 1].index]
if not sold_test.empty:
    X_sold_test = sold_test[feature_columns]
    y_sold_test = sold_test['days_on_market']
    y_pred_days = days_regressor.predict(X_sold_test)
    
    print("\nTest Set Evaluation (Sold Properties Only):")
    print(f"MAE: {mean_absolute_error(y_sold_test, y_pred_days):.1f} days")
    print(f"RMSE: {np.sqrt(mean_squared_error(y_sold_test, y_pred_days)):.1f} days")
    print(f"R²: {r2_score(y_sold_test, y_pred_days):.3f}")
    
    # Plot actual vs predicted
    plt.figure(figsize=(10, 6))
    plt.scatter(y_sold_test, y_pred_days, alpha=0.5)
    plt.plot([min(y_sold_test), max(y_sold_test)], 
             [min(y_sold_test), max(y_sold_test)], 'r--')
    plt.xlabel('Actual Days on Market')
    plt.ylabel('Predicted Days on Market')
    plt.title('Actual vs Predicted Days on Market')
    plt.show()
else:
    print("No sold properties in test set for evaluation")

# 3. Evaluate Price Prediction Models
def evaluate_price_model(model, X, y, model_name):
    print(f"\n=== {model_name} Price Model Evaluation ===")
    # Cross-validation
    cv_mae = cross_val_score(model, X, y, cv=5, scoring='neg_mean_absolute_error')
    print(f"Cross-validation MAE: {-cv_mae.mean():.2f} ± {-cv_mae.std():.2f}")
    
    # Train-test split evaluation
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model.fit(X_train, y_train)  # Refit on train set
    y_pred = model.predict(X_test)
    
    print("\nTest Set Evaluation:")
    print(f"MAE: {mean_absolute_error(y_test, y_pred):.2f}")
    print(f"RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.2f}")
    print(f"R²: {r2_score(y_test, y_pred):.3f}")
    
    # Plot feature importance
    plt.figure(figsize=(10, 6))
    importances = model.feature_importances_
    indices = np.argsort(importances)[-20:]  # Top 20 features
    plt.title(f'Feature Importances - {model_name}')
    plt.barh(range(len(indices)), importances[indices], align='center')
    plt.yticks(range(len(indices)), [feature_columns[i] for i in indices])
    plt.xlabel('Relative Importance')
    plt.show()

# Evaluate rent price model
evaluate_price_model(RandomForestRegressor(n_estimators=100, random_state=42), 
                    X_rent, y_rent, "Rent Price")

# Evaluate sale price model
evaluate_price_model(RandomForestRegressor(n_estimators=100, random_state=42), 
                    X_sales, y_sales, "Sale Price")

# 4. Check for Data Leakage
print("\n=== Data Leakage Check ===")
# Verify target variables aren't in features
target_cols = ['estimated_rentprice', 'estimated_saleprice', 'event', 'days_on_market']
leakage_check = set(feature_columns) & set(target_cols)
if leakage_check:
    print(f"WARNING: Possible data leakage - these target variables appear in features: {leakage_check}")
else:
    print("No obvious data leakage detected - target variables not in features")

# 5. Temporal Validation (if data has time component)
print("\n=== Temporal Validation ===")
if 'post_date' in df.columns:
    df['post_date'] = pd.to_datetime(df['post_date'])
    df_sorted = df.sort_values('post_date')
    cutoff = int(0.8 * len(df_sorted))
    
    # Split into older (train) and newer (test) properties
    X_train_time = df_encoded.loc[df_sorted.index[:cutoff], feature_columns]
    y_train_time = df_encoded.loc[df_sorted.index[:cutoff], 'estimated_saleprice']
    X_test_time = df_encoded.loc[df_sorted.index[cutoff:], feature_columns]
    y_test_time = df_encoded.loc[df_sorted.index[cutoff:], 'estimated_saleprice']
    
    temporal_model = RandomForestRegressor(n_estimators=100, random_state=42)
    temporal_model.fit(X_train_time, y_train_time)
    y_pred_time = temporal_model.predict(X_test_time)
    
    print("Temporal Validation Results (Sale Price):")
    print(f"MAE: {mean_absolute_error(y_test_time, y_pred_time):.2f}")
    print(f"RMSE: {np.sqrt(mean_squared_error(y_test_time, y_pred_time)):.2f}")
    print(f"R²: {r2_score(y_test_time, y_pred_time):.3f}")
else:
    print("No date column found for temporal validation")

from pathlib import Path

# Get the current script directory
script_dir = Path(__file__).parent

# Create paths for outputs
models_dir = script_dir / "models"
output_dir = script_dir / "output"

# Create directories if they don't exist
models_dir.mkdir(exist_ok=True)
output_dir.mkdir(exist_ok=True)

# Save models
joblib.dump(model_sales, models_dir / "sales_price_model.pkl")
joblib.dump(model_rent, models_dir / "rent_price_model.pkl") 
joblib.dump(sell_classifier, models_dir / "sale_classifier_model.pkl")
joblib.dump(days_regressor, models_dir / "days_on_market_model.pkl")
joblib.dump(imputer, models_dir / "imputer.pkl")

# Save predictions
output_path = output_dir / "property_predictions_final.csv"
output_df.to_csv(output_path, index=False)

print(f"\n✅ Models saved to: {models_dir}")
print(f"✅ Predictions saved to: {output_path}")