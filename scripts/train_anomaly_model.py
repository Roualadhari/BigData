import os
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
import joblib
import json

DATA_PATH = os.path.join("data", "handoff", "sensor_data.csv")
MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

def load_data(path):
    df = pd.read_csv(path)
    return df

def preprocess(df):
    # Drop timestamp (not numeric)
    df = df.copy()
    
    if 'timestamp' in df.columns:
        df = df.drop(columns=['timestamp'])

    # Encode sensor_id
    if 'sensor_id' in df.columns:
        le = LabelEncoder()
        df['sensor_id'] = le.fit_transform(df['sensor_id'])

    # Fill missing numeric values
    for c in df.select_dtypes(include=[np.number]).columns:
        df[c] = df[c].fillna(df[c].median())

    return df

def train_isolation_forest(X):
    model = IsolationForest(
        n_estimators=200,
        contamination=0.02,
        random_state=42
    )
    model.fit(X)
    return model

def main():
    df = load_data(DATA_PATH)
    X = preprocess(df)

    model = train_isolation_forest(X)

    model_path = os.path.join(MODEL_DIR, "isolation_forest.joblib")
    joblib.dump(model, model_path)

    preds = model.predict(X)  # 1 = normal, -1 = anomaly

    df_output = df.copy()
    df_output["anomaly"] = preds

    output_path = os.path.join(MODEL_DIR, "anomaly_results.csv")
    df_output.to_csv(output_path, index=False)

    report = {
        "total_readings": len(df),
        "anomalies_detected": int(np.sum(preds == -1)),
        "contamination_rate": float(np.mean(preds == -1))
    }

    report_path = os.path.join(MODEL_DIR, "anomaly_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print("Model trained. Report saved to:", report_path)

if __name__ == "__main__":
    main()
