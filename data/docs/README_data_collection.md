# Data Collection - Person 1

## Overview
This folder contains the raw data collected for the Smart Agriculture System.
It includes a full catalog of disease images and environmental sensor data fetched via API.

## 1. Image Dataset (PlantVillage)
- **Source**: Kaggle (PlantVillage)
- **File**: `image_catalog.csv`
- **Description**: A full index of every image file available on the disk.
- **Columns**: 
  - `filename`: Name of the image.
  - `plant_name`: (e.g., Tomato, Potato).
  - `disease_type`: (e.g., Bacterial_spot, Healthy).
  - `file_path`: Absolute path for loading into HDFS.
  - `dataset_split`: Recommended split (train/validation/test).

## 2. Environmental Data (IoT/Weather)
- **Source**: Open-Meteo API + Simulation
- **File**: `sensor_data.csv`
- **Description**: Hourly environmental readings for the farm location (Gafsa, Tunisia).
- **Methodology**:
  - Air Temp, Humidity, Soil Moisture, Soil Temp: **Fetched real data from Open-Meteo API**.
  - Soil pH: **Simulated** (values 6.0-7.0) as no public API exists for this.
- **Columns**: `timestamp`, `air_temperature`, `air_humidity`, `soil_temperature`, `soil_moisture`, `soil_ph`.

## Scripts Used
1. `generate_image_catalog.py`: Scans folders to build the CSV catalog.
2. `fetch_sensor_data.py`: Calls Open-Meteo API to generate sensor logs.

## Notes for Team
- **Person 2 (Data Engineer)**: Use `image_catalog.csv` to load images into HDFS. Use `sensor_data.csv` to populate MongoDB.
- **Person 4 (Data Scientist)**: Use the `dataset_split` column in the image catalog to train your models.