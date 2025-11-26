import requests
import pandas as pd
import random
from datetime import datetime

# === CONFIGURATION ===
# Coordinates for a farm in Gafsa, Tunisia (Example)
LAT = 34.425
LON = 8.784
# We fetch past 7 days of data to simulate "collected" history
API_URL = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": LAT,
    "longitude": LON,
    "hourly": "temperature_2m,relative_humidity_2m,soil_temperature_0cm,soil_moisture_0_to_1cm",
    "past_days": 7,
    "forecast_days": 1
}

print("📡 Connecting to Open-Meteo API...")
response = requests.get(API_URL, params=params)

if response.status_code == 200:
    data = response.json()
    hourly = data['hourly']
    
    # Create lists to hold our data
    records = []
    
    for i in range(len(hourly['time'])):
        # REAL DATA from API
        timestamp = hourly['time'][i]
        temp = hourly['temperature_2m'][i]
        humidity = hourly['relative_humidity_2m'][i]
        soil_temp = hourly['soil_temperature_0cm'][i]
        soil_moisture = hourly['soil_moisture_0_to_1cm'][i]
        
        # SIMULATED DATA (Because no API exists for this)
        # pH is usually stable, random fluctuation between 6.0 and 7.0
        soil_ph = round(random.uniform(6.0, 7.0), 2)
        
        records.append({
            "timestamp": timestamp,
            "sensor_id": "SENSOR_01_GAFSA",
            "air_temperature": temp,
            "air_humidity": humidity,
            "soil_temperature": soil_temp,
            "soil_moisture": soil_moisture, # Volumetric fraction
            "soil_ph": soil_ph
        })
    
    # Save to CSV
    df = pd.DataFrame(records)
    output_path = "../data/handoff/sensor_data.csv"
    df.to_csv(output_path, index=False)
    print(f"✅ Success! Fetched {len(df)} records.")
    print(f"saved to: {output_path}")

else:
    print("❌ Error fetching data:", response.status_code)