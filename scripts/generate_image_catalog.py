import os
import pandas as pd
import random

# === 1. SETUP PATHS (DO NOT CHANGE IF YOUR PATHS ARE CORRECT) ===
SOURCE_DIR = r"C:\Users\MSI-CYBORG\OneDrive\Bureau\9raya\Big Data\Project\Project\data\raw\kaggle\images\PlantVillage"
OUTPUT_FILE = r"C:\Users\MSI-CYBORG\OneDrive\Bureau\9raya\Big Data\Project\Project\data\handoff\image_catalog.csv"

data = []

print("Scanning image folders...")

# === 2. SCAN EVERY FILE ===
for root, dirs, files in os.walk(SOURCE_DIR):
    for filename in files:
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            # Get folder name (e.g., Potato___Early_blight)
            folder_name = os.path.basename(root)
            
            # Extract Plant and Disease names
            if "___" in folder_name:
                parts = folder_name.split("___")
                plant = parts[0].replace("_", " ")
                disease = parts[1].replace("_", " ")
            else:
                plant = folder_name
                disease = "Unknown"

            # Save the full path so Person 2 can load it into HDFS
            full_path = os.path.join(root, filename)

            data.append({
                "filename": filename,
                "plant_name": plant,
                "disease_type": disease,
                "file_path": full_path
            })

# === 3. SAVE AS CSV ===
df = pd.DataFrame(data)

# Assign Train/Test split for Person 4 (Machine Learning)
def get_split(x):
    r = random.random()
    if r < 0.7: return "train"
    elif r < 0.85: return "validation"
    else: return "test"

df['dataset_split'] = df['filename'].apply(get_split)

# Ensure folder exists
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

df.to_csv(OUTPUT_FILE, index=False)
print(f"✅ DONE! Created {OUTPUT_FILE}")
print(f"Total Images Found: {len(df)}")