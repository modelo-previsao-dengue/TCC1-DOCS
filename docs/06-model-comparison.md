# Model Comparison: XGBoost vs SARIMA

## 1. Overview

This repository implements two educational forecasting baselines for weekly dengue cases in Brasilia: an `XGBoost` regressor and a `SARIMA` time-series model. Both notebooks use the same unified dataset, but they represent different modeling philosophies.

The XGBoost notebook builds a supervised learning pipeline with lagged dengue counts, rolling statistics, seasonal indicators, and climate covariates such as rainfall, temperature, humidity, and pressure. The SARIMA notebook models the dengue count series as a univariate seasonal process and does not include exogenous climate variables in its current implementation.

For the TCC objective described in `README.md`, the key question is not only which notebook reports lower error, but which approach is better aligned with forecasting dengue outbreaks using both temporal dynamics and climate information across multiple municipalities.

## 2. XGBoost Model

### How it works in this project

The notebook `notebooks/examples/02_xgboost_model_educativo.ipynb` treats forecasting as a regression problem. It loads the unified weekly dataset, checks temporal alignment, and keeps epidemiological and climate variables in the feature space.

The main preprocessing and modeling steps are:

- Creation of lags from 1 to 12 weeks for dengue cases and climate variables.
- Creation of derived features such as moving averages, rolling standard deviations, percentage changes, season indicators, week-of-year, and interaction terms.
- Chronological split into training, validation, and test sets (`60% / 20% / 20%`) to reduce information leakage.
- Training of `XGBRegressor` with early stopping.
- Additional hyperparameter tuning with `GridSearchCV` and `TimeSeriesSplit`, although the reported final metrics are computed with `xgb_model`, not with `xgb_model_tuned`.
- Basic interpretability through feature importance and SHAP.

### Strengths

- Directly supports the project objective of combining dengue history with climate data.
- Captures nonlinear relationships and interactions that are difficult to express in classical linear time-series models.
- Includes explicit feature engineering for seasonality and short-term temporal memory.
- Provides practical interpretability through feature importance and SHAP.
- Is more adaptable to a multi-municipality setting because the same feature pipeline can be reused across datasets.
- Already includes a reusable class (`ModeloPreditoXGBoost`) intended for extension to multiple cities.

### Weaknesses

- Depends heavily on feature engineering quality.
- Reported validation performance is weak, suggesting instability or overfitting despite excellent training fit.
- The notebook does not yet implement the rolling-window validation recommended in the `README.md`.
- Tree-based models are usually less transparent than classical statistical models at the parameter level.

## 3. SARIMA Model

### How it works in this project

The notebook `notebooks/examples/03_sarima_model_educativo.ipynb` models dengue incidence as a univariate weekly seasonal series. It resamples the data to weekly frequency, decomposes the series, runs an ADF stationarity test, inspects ACF/PACF, and trains a `SARIMAX` object configured as a SARIMA model with order `(1,1,1)` and seasonal order `(1,1,0,52)`.

The main steps are:

- Weekly aggregation of dengue cases only.
- Stationarity check with ADF, which indicates non-stationarity before differencing.
- Manual specification of SARIMA orders based on time-series diagnostics.
- Chronological split into training and test sets (`80% / 20%`).
- Forecast generation for the test period.
- Residual diagnostics, with a manual fallback because the default diagnostic plot is not supported by the available sample size and lag structure.

### Strengths

- Strong baseline for seasonal univariate forecasting.
- More statistically interpretable at the model-parameter level.
- Requires fewer engineered predictors than XGBoost.
- Useful as a benchmark to quantify how much value climate covariates add.

### Weaknesses

- Current notebook ignores climate variables, which makes it misaligned with the central TCC objective.
- Assumes a relatively stable linear seasonal structure and is more sensitive to specification choices.
- Scaling to many municipalities usually requires repeated manual order selection or automated SARIMA search.
- Is less flexible for modeling nonlinear climate-dengue interactions.
- The notebook itself suggests SARIMAX as the next step, indicating that plain SARIMA is not yet the intended final model.

## 4. Quantitative Comparison

The notebooks do not use exactly the same evaluation protocol, so the metrics below should be interpreted with caution. XGBoost uses a `60/20/20` train/validation/test split with 30 test observations after dropping 12 initial lag rows. SARIMA uses an `80/20` train/test split with 32 test observations on the full weekly series.

| Model | Train RMSE | Validation RMSE | Test RMSE | Train MAE | Validation MAE | Test MAE | Train MAPE | Validation MAPE | Test MAPE | Train R² | Validation R² | Test R² |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| XGBoost | 5.50 | 11144.50 | 243.72 | 2.24 | 7910.77 | 230.16 | 0.20 | 51.65 | 53.00 | 1.00 | -0.68 | 0.35 |
| SARIMA | not reported | not reported | 1976.18 | not reported | not reported | 1693.90 | not reported | not reported | not reported | not reported | not reported | -7.432 |

Key observations:

- On the reported test split, XGBoost clearly outperforms SARIMA in RMSE, MAE, and R².
- SARIMA does not report MAPE in the notebook.
- XGBoost shows a large gap between training and validation performance, which indicates the current setup still needs stronger temporal validation before any final empirical claim.
- Even with that caveat, the SARIMA test results are substantially weaker in the current repository state.

## 5. Qualitative Comparison

### Time series handling

SARIMA is a native time-series model and handles trend and yearly seasonality directly through differencing and seasonal terms. XGBoost handles time dependence indirectly through lagged and rolling features. In practice, both approaches can model temporal structure, but SARIMA is more natural for pure univariate seasonality, while XGBoost is more flexible once richer predictors are available.

### Climate variables integration

This is the decisive point for the TCC. The `README.md` defines the project as forecasting dengue outbreaks using time series combined with climate data. XGBoost already does this. The SARIMA notebook does not; it only models dengue counts. To match the project goal, SARIMA would need to evolve into SARIMAX with exogenous regressors.

### Complexity

SARIMA is simpler to specify conceptually but can become difficult to tune when seasonal orders must be selected for many municipalities. XGBoost has a more complex preprocessing pipeline, yet this complexity is programmatic and easier to automate once standardized.

### Interpretability

SARIMA is more interpretable in a classical statistical sense because its coefficients directly describe autoregressive and moving-average structure. XGBoost is less transparent internally, but the notebook compensates with feature importance and SHAP, which are often more useful for applied decision support when many predictors are involved.

### Scalability

XGBoost is more scalable for a national or multi-municipality workflow. The repository already includes a modular class for reuse, and the feature-engineering pipeline can be standardized across cities. SARIMA is viable as a baseline, but maintaining and tuning many municipality-specific seasonal models would be more labor-intensive.

### Ease of maintenance and extension

XGBoost is easier to extend with new variables, new lags, or alternative targets such as outbreak risk classes. SARIMA is harder to extend beyond the univariate setting unless the project explicitly migrates to SARIMAX or another multivariate time-series framework.

### Robustness to missing or noisy data

The XGBoost notebook explicitly checks missing values and applies linear interpolation when needed. Tree-based methods also tend to be more tolerant of heterogeneous predictors and imperfect nonlinear patterns. SARIMA generally requires a cleaner and more stable time series, and its assumptions make it more sensitive to missingness, structural breaks, and misspecified seasonal structure.

## 6. Final Recommendation

The most suitable model for the current TCC objective is **XGBoost**.

The recommendation is based on two layers of evidence. First, XGBoost is better aligned with the stated project goal in `README.md`, which explicitly emphasizes dengue forecasting with climate data. The notebook already integrates rainfall, temperature, humidity, and pressure together with temporal features. Second, the currently reported quantitative results are substantially better than the SARIMA baseline on the available test evaluations: XGBoost achieves `RMSE = 243.72`, `MAE = 230.16`, and `R² = 0.35`, while SARIMA reports `RMSE = 1976.18`, `MAE = 1693.90`, and `R² = -7.432`.

This does not mean SARIMA should be discarded. It remains a useful statistical baseline and a strong reference point for seasonality-driven forecasting. However, in its current form it is not the best final candidate for this TCC because it does not yet incorporate exogenous climate variables, which are central to the problem definition.

## 7. Next Steps

- Re-evaluate XGBoost with rolling-window or walk-forward validation, as recommended in `README.md`, to obtain more reliable temporal generalization estimates.
- Evaluate the tuned XGBoost model (`xgb_model_tuned`) on the held-out test set, since the notebook currently reports final metrics for the untuned `xgb_model`.
- Add explicit outbreak-classification metrics later if the project converts forecasts into alert levels (`AUC`, `Precision`, `Recall`, `F1-score`).
- Keep SARIMA as a baseline, but implement **SARIMAX** to test whether adding climate regressors closes the gap.
- Compare XGBoost against a hybrid benchmark, for example:
  - `SARIMAX` with exogenous climate variables.
  - `XGBoost` with alternative lag windows and multi-horizon targets.
  - `XGBoost + SARIMA/SARIMAX` residual modeling.
  - `LSTM` or other sequence models once the validation protocol is stable.

In summary, the repository should treat **SARIMA as a baseline** and **XGBoost as the primary model candidate** for the next phase of the TCC.
