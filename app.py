# STEAMLIT APP 

# Very simple Streamlit app for taxi demand prediction
# I made this after finishing my XGBoost model in the notebook

import streamlit as st
import pandas as pd
import xgboost as xgb
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Load the model I saved earlier
model = xgb.XGBRegressor()
model.load_model("models/my_taxi_model.json")   # change path if needed

# Load the data just to get the list of zones
df = pd.read_parquet("data/processed/hourly_demand_features.parquet")
zones = df[["zone_id", "Zone", "Borough"]].drop_duplicates()
zones = zones.sort_values("Zone")

st.title("Yellow Cab Chaos Taxi Demand - Simple Forecast")
st.write("Choose a zone and a starting time to see 24 hour prediction")

# Pick zone
zone_list = zones["Zone"].tolist()
selected_zone = st.selectbox("Pick a zone", zone_list)

# Get zone_id and borough
zone_row = zones[zones["Zone"] == selected_zone].iloc[0]
zone_id = int(zone_row["zone_id"])
borough = zone_row["Borough"]

st.write(f"Zone: **{selected_zone}** ({borough}) – ID {zone_id}")

# Pick date and hour
col1, col2 = st.columns(2)
with col1:
    pick_date = st.date_input("Start date", value=datetime(2026, 3, 21))
with col2:
    pick_hour = st.slider("Start hour", 0, 23, 0)

start_time = datetime(pick_date.year, pick_date.month, pick_date.day, pick_hour)

# Button
if st.button("Make 24-hour prediction"):
    st.write("Calculating...")

    # Very basic forecast loop
    predictions = []
    current_time = start_time

    # I need some last known value (taking the very last row of this zone as starting point)
    last_row = df[df["zone_id"] == zone_id].sort_values("pickup_datetime").tail(1)

    if last_row.empty:
        st.error("No data for this zone :(")
    else:
        last_trips = float(last_row["trip_count"].iloc[0])

        for i in range(24):
            current_time += timedelta(hours=1)

            # make fake row with new time
            new_row = last_row.copy()
            new_row["pickup_hour"] = current_time.hour
            new_row["pickup_dayofweek"] = current_time.dayofweek
            new_row["pickup_month"] = current_time.month
            new_row["is_weekend"] = 1 if current_time.weekday() >= 5 else 0
            new_row["is_rush_hour"] = 1 if current_time.hour in [7,8,9,16,17,18] else 0
            new_row["is_holiday"] = 0  # lazy for now

            # lags - very rough (using last prediction or last real value)
            new_row["trip_count_lag_1h"] = predictions[-1] if predictions else last_trips
            new_row["trip_count_lag_24h"] = last_trips
            new_row["trip_count_lag_168h"] = last_trips

            # rolling - using same value (not accurate but ok for demo)
            new_row["trip_count_roll_mean_24h"] = last_trips
            new_row["trip_count_roll_max_24h"] = last_trips

            # prepare columns for model
            features_used = [
                "pickup_hour", "pickup_dayofweek", "pickup_month",
                "is_weekend", "is_rush_hour", "is_holiday",
                "trip_count_lag_1h", "trip_count_lag_24h", "trip_count_lag_168h",
                "trip_count_roll_mean_24h", "trip_count_roll_max_24h", "Borough"
            ]

            X = new_row[features_used].copy()

            # one-hot borough (like in training)
            dummies = pd.get_dummies(X["Borough"], prefix="boro")
            X = pd.concat([X.drop("Borough", axis=1), dummies], axis=1)

            # fill missing columns with 0 (if borough not in training dummies)
            # (you can get real column names from notebook if you want to be exact)
            X = X.reindex(columns=model.feature_names_in_, fill_value=0)

            # predict
            p = model.predict(X)[0]
            pred_value = max(0, round(float(p), 1))   # no negative trips
            predictions.append(pred_value)

        # show results
        result = pd.DataFrame({
            "time": [start_time + timedelta(hours=i+1) for i in range(24)],
            "predicted_trips": predictions
        })

        st.subheader("24 hour forecast")
        st.dataframe(result)

        # small chart
        fig, ax = plt.subplots()
        ax.plot(result["time"], result["predicted_trips"], marker="o", color="orange")
        ax.set_title(f"Forecast - {selected_zone}")
        ax.set_xlabel("Time")
        ax.set_ylabel("Trips")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

st.write("---")
st.caption("Very basic demo • lags are approximated • for portfolio only")