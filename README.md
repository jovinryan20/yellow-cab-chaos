# Yellow Cab Chaos – NYC Taxi Demand Prediction

**Predicting hourly yellow taxi trips per zone in New York City using historical patterns**

## Quick Overview

This project tries to forecast how many yellow taxi trips will happen in each NYC taxi zone every hour — using only calendar features, lags and simple rolling statistics (no weather, no events, no real-time traffic).

Final model (XGBoost) gets:
- MAE ≈ 5.3 trips per hour per zone on future months
- MAPE ≈ 47–48% (sounds high but actually decent for zone-level hourly data)

The live demo app lets you pick any zone and see a 24-hour forecast.

**Live demo** → https://yellow-cab-chaos-yourusername.streamlit.app  

## Project Structure

yellow-cab-chaos/
├── app.py                        # Simple Streamlit forecast app
├── requirements.txt              # Packages needed to run everything
├── .gitignore
├── README.md                    
│
├── notebooks/
│   ├── download_and_clean.ipynb        # Data cleaning
│   ├── patterns_and_features.ipynb     # EDA + feature engineering
│   └── predicting_and_modelling.ipynb  # Modeling, evaluation, results
│
├── data/
│   ├── external/                 # raw lookup files (taxi zones etc.)
│   ├── processed/                # hourly_demand_features.parquet
│   └── raw/                      # original data
│
├── models/
│   └── my_taxi_model.json        # Trained XGBoost model (saved as JSON)
│
├── documentation/
│   ├── EDA Plots explanation.pdf
│   └── Modelling Documentation.pdf
│
├── viz/
│   └── figures/                  # Important plots saved as PNG
│
└── outputs/
    └── zone_performance_summary.csv   # Final per-zone metrics

## What I Actually Did

1. Cleaned and aggregated raw taxi data into hourly counts per zone
2. Added time-based features (hour, dayofweek, weekend, rush hour, holidays)
3. Created lags (1h / 24h / 168h) and rolling stats (24h mean/max)
4. Did time-based train/val/test split (no random shuffle!)
5. Trained XGBoost → tuned a bit manually
6. Evaluated with MAE, RMSE, MAPE
7. Made per-zone performance table + actual vs predicted plots
8. Built very basic Streamlit app for interactive forecasts
9. Saved model in JSON format (safe & portable)

## Results Summary

**Test set (future months – Sep 2025 onward)**

- MAE: **5.28** trips  
- RMSE: **12.31**  
- MAPE: **47.6%** 

**What this actually means**

- On average the model is wrong by ~5 trips per hour per zone → pretty usable number
- Percentage error looks high because quiet zones (0–10 trips) create huge % when you're off by 3–5
- Airports (JFK, LaGuardia) and Midtown usually get much better MAPE (25–40%)
- Quiet residential zones pull the average up (sometimes 80–150% MAPE)

**Top important features** (from XGBoost importance)

1. trip_count_lag_168h (same hour last week)
2. trip_count_lag_24h (same hour yesterday)
3. pickup_hour
4. trip_count_roll_mean_24h
5. is_weekend / is_rush_hour

→ Weekly and daily seasonality are doing most of the work — makes sense for taxi demand.

## How to Run Locally

1. Clone the repo
   ```bash
   git clone https://github.com/yourusername/yellow-cab-chaos.git
   cd yellow-cab-chaos

(Recommended) Create virtual environmentBashpython -m venv .venv

### Windows:
.venv\Scripts\activate

### macOS/Linux:
source .venv/bin/activate
Install packagesBashpip install -r requirements.txt
Run the Streamlit appBashstreamlit run app.py
(Optional) Open notebooks in Jupyter / VS Code

## Limitations & Honest Thoughts

Forecast function in app is very naive (lags are approximated, not recursively proper)
Single global model → separate models per borough or high-volume zones would probably be better
No external data (weather, holidays are basic, no events/traffic/strikes)
MAPE high on low-volume zones — this is expected and hard to fix without more features
Not production-ready (no monitoring, no retraining pipeline)

Still — I think it's a decent baseline and good learning project.

## What I Learned

Time-based split is super important (random split would cheat badly)
Lags and rolling features beat fancy calendar stuff in this case
MAPE can be misleading when many zeros/low counts exist
Saving model as JSON is much safer than pickle
Making a simple Streamlit app

## Next Possible Steps (if I continue)

Train per-borough or per-zone models
Add sin/cos cyclical encoding for hour/day
Pull in basic weather data (even historical)
Improve recursive forecasting in app
Add confidence intervals (quantile regression)

License
MIT License — feel free to use anything for learning/portfolio.
Made with ❤️ in March 2026
Questions? Open an issue or reach out!