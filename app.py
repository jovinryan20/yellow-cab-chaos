import streamlit as st
import pandas as pd
import xgboost as xgb
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt


# Load the saved model
MODEL_PATH = "models/my_taxi_model.json"

if not os.path.exists(MODEL_PATH):
    st.error(f"Model file not found: {MODEL_PATH}")
    st.stop()

model = xgb.XGBRegressor()
model.load_model(MODEL_PATH)

# Load only the zone lookup (small file, no big parquet)
ZONE_FILE = "data/external/taxi_zone_lookup.csv"

try:
    zones = pd.read_csv(ZONE_FILE)
    # Make sure column names are consistent
    zones = zones[["LocationID", "Zone", "Borough"]].drop_duplicates()
    zones = zones.sort_values("Zone")
    zones["LocationID"] = zones["LocationID"].astype(int)
except FileNotFoundError:
    st.error(f"Zone lookup file not found: {ZONE_FILE}")
    st.stop()
except Exception as e:
    st.error(f"Error loading zone file: {e}")
    st.stop()


# Streamlit UI

st.title("Yellow Cab Chaos - NYC Taxi Demand Forecast")
st.write("Select a zone and starting time to see a 24-hour prediction")

# Zone selector
zone_list = zones["Zone"].tolist()
selected_zone = st.selectbox("Select a taxi zone", zone_list)

# Get selected zone info
zone_row = zones[zones["Zone"] == selected_zone].iloc[0]
location_id = int(zone_row["LocationID"])
borough = zone_row["Borough"]

st.markdown(
    f"**Zone**: {selected_zone}  •  **Borough**: {borough}  •  **ID**: {location_id}"
)

# Date & time input
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start date", value=datetime(2026, 3, 21))
with col2:
    start_hour = st.slider("Start hour", 0, 23, 8)

start_time = datetime(start_date.year, start_date.month, start_date.day, start_hour)

# Forecast button

if st.button("Generate 24-hour Forecast", type="primary"):

    with st.spinner("Generating forecast..."):

        predictions = []
        current_time = start_time

        # Dummy starting value (since we don't have historical df anymore)
        # For demo purposes this is acceptable – real version would use last known value
        last_trips = 5.0  # reasonable fallback

        for i in range(24):
            current_time += timedelta(hours=1)

            # Create feature row
            new_row = pd.DataFrame(
                [
                    {
                        "pickup_hour": current_time.hour,
                        "pickup_dayofweek": current_time.weekday(),
                        "pickup_month": current_time.month,
                        "is_weekend": 1 if current_time.weekday() >= 5 else 0,
                        "is_rush_hour": (
                            1 if current_time.hour in [7, 8, 9, 16, 17, 18] else 0
                        ),
                        "is_holiday": 0,
                        "trip_count_lag_1h": (
                            predictions[-1] if predictions else last_trips
                        ),
                        "trip_count_lag_24h": last_trips,
                        "trip_count_lag_168h": last_trips,
                        "trip_count_roll_mean_24h": last_trips,
                        "trip_count_roll_max_24h": last_trips,
                        "Borough": borough,
                    }
                ]
            )

            # One-hot encode Borough
            dummies = pd.get_dummies(new_row["Borough"], prefix="boro")
            X = pd.concat([new_row.drop("Borough", axis=1), dummies], axis=1)

            # Align columns exactly with training (fill missing with 0)
            try:
                X = X.reindex(columns=model.feature_names_in_, fill_value=0)
            except AttributeError:
                st.warning(
                    "Model does not have feature_names_in_ attribute. Using fallback."
                )
                # Fallback if model was saved without feature names
                expected_cols = [
                    "pickup_hour",
                    "pickup_dayofweek",
                    "pickup_month",
                    "is_weekend",
                    "is_rush_hour",
                    "is_holiday",
                    "trip_count_lag_1h",
                    "trip_count_lag_24h",
                    "trip_count_lag_168h",
                    "trip_count_roll_mean_24h",
                    "trip_count_roll_max_24h",
                ] + [c for c in X.columns if c.startswith("boro_")]
                X = X.reindex(columns=expected_cols, fill_value=0)

            # Predict
            pred = model.predict(X)[0]
            pred_value = max(0, round(float(pred), 1))
            predictions.append(pred_value)

        # Create result dataframe
        result = pd.DataFrame(
            {
                "Time": [start_time + timedelta(hours=i + 1) for i in range(24)],
                "Predicted Trips": predictions,
            }
        )

        st.success("Forecast ready!")

        # Show table
        st.subheader(f"24-hour forecast for **{selected_zone}**")
        st.dataframe(
            result.style.format({"Predicted Trips": "{:.1f}"}),
            use_container_width=True,
            hide_index=True,
        )

        # Show chart
        fig, ax = plt.subplots(figsize=(10, 4.5))
        ax.plot(
            result["Time"],
            result["Predicted Trips"],
            marker="o",
            color="#ff8c00",
            linewidth=2,
        )
        ax.set_title(f"Predicted hourly trips – {selected_zone}")
        ax.set_xlabel("Time")
        ax.set_ylabel("Trips")
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

# Footer
st.markdown("---")
st.caption(
    "Very simple demo version • Lags are approximated • Portfolio project only • March 2026"
)
