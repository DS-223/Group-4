
# Machine Learning Models

This project includes predictive models trained to estimate:

- Rent prices (monthly)
- Sale prices (full property value)

## Inputs (Features)

- Property area (in square meters)
- Number of rooms
- Location
- Property type

## Algorithms Used

- Linear Regression
- Ensemble models (e.g., Random Forest)

Both models are trained using historical and generated property data and saved as `.pkl` files in the `model/models/` directory.

## Output

```json
{
  "predicted_rent": 200000,
  "predicted_sale": 23000000
}
```

## Evaluation

- MAE: Approx. 250,000 AMD
- RMSE: Approx. 400,000 AMD
- Evaluation done using holdout validation and cross-checks with manual pricing.

These metrics show that our model provides reliable ballpark estimates for price prediction.
