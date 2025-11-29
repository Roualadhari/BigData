import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, year, month, dayofmonth, hour, trim

# =========================================================================
# 🛑 CRITICAL FIX: Setting HADOOP_HOME environment variable on Windows 
# This helps resolve the "UnsupportedOperationException" during Spark startup 
# by telling Spark where to find necessary Hadoop client binaries.
# Ensure 'C:\hadoop' contains your winutils.exe files.
# =========================================================================
os.environ['HADOOP_HOME'] = "C:\\hadoop" 
# You may also need: os.environ['HADOOP_USER_NAME'] = "yassmine"

# --- 1. CONFIGURATION ---
# IMPORTANT: Update these settings to match your actual cluster and database environment!
MONGO_HOST = "localhost" 
MONGO_PORT = "27017" 
DATABASE_NAME = "smart_agriculture" 

# Define paths relative to the project structure
SENSOR_CSV_PATH = "C:/BigData/data/handoff/sensor_data.csv"
CATALOG_CSV_PATH = "C:/BigData/data/handoff/image_catalog.csv"
# We use a local file path with 'file:///' to bypass the fatal HDFS configuration error on Windows.
HDFS_OUTPUT_PATH = "file:///C:/BigData/data/processed/sensor_readings_processed" 

# --- 2. INITIALIZE SPARK SESSION ---
MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/{DATABASE_NAME}"

# Configure Spark to use the MongoDB connector
spark = SparkSession.builder \
    .appName("Person2_DataPreprocessingAndStorage") \
    .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
    .config("spark.mongodb.output.uri", MONGO_URI) \
    .getOrCreate()

print("--- Spark Session Initialized. Starting Data Pipeline ---")


# =================================================================
# PIPELINE 1: Sensor Data Processing (for Analysis/Reporting)
# =================================================================
print("\n[SENSOR DATA] Loading and processing sensor_data.csv...")

# 1. Load Data
raw_sensor_df = spark.read.csv(SENSOR_CSV_PATH, header=True, inferSchema=True)

# 2. Cleaning and Transformation (Schema Enforcement, Date/Time Normalization)
processed_sensor_df = raw_sensor_df.dropDuplicates() \
    .withColumn("timestamp", to_timestamp(col("timestamp"))) \
    .withColumn("reading_year", year(col("timestamp"))) \
    .withColumn("reading_month", month(col("timestamp"))) \
    .withColumn("reading_day", dayofmonth(col("timestamp"))) \
    .withColumn("reading_hour", hour(col("timestamp"))) 

# Filter out any rows where key sensor data might be null (a form of data cleaning)
processed_sensor_df = processed_sensor_df.na.drop(subset=['air_temperature', 'soil_moisture'])

# 3. Storage in "HDFS" (using local path for Windows compatibility)
# This step is essential for Data Analyst (Person 3) to perform large-scale batch analysis
processed_sensor_df.write \
    .mode("overwrite") \
    .partitionBy("reading_year", "reading_month") \
    .parquet(HDFS_OUTPUT_PATH)

print(f"✅ [SENSOR DATA] Stored in local HDFS path at: {HDFS_OUTPUT_PATH}")

# 4. Storage in MongoDB (for User Access/Research)
processed_sensor_df.write \
    .format("com.mongodb.spark.sql.connector") \
    .mode("overwrite") \
    .option("collection", "sensor_readings") \
    .save()

print(f"✅ [SENSOR DATA] Loaded into MongoDB collection: {DATABASE_NAME}.sensor_readings")


# =================================================================
# PIPELINE 2: Image Catalog Processing (for ML/Prediction)
# =================================================================
print("\n[IMAGE CATALOG] Loading and storing image_catalog.csv...")

# 1. Load Data
raw_catalog_df = spark.read.csv(CATALOG_CSV_PATH, header=True, inferSchema=True)

# 2. Cleaning and Transformation
processed_catalog_df = raw_catalog_df \
    .withColumn("plant_name", trim(col("plant_name"))) \
    .withColumn("disease_type", trim(col("disease_type")))

# 3. Storage in MongoDB (Crucial metadata for ML Model - Person 4)
processed_catalog_df.write \
    .format("com.mongodb.spark.sql.connector") \
    .mode("overwrite") \
    .option("collection", "disease_metadata") \
    .save()

print(f"✅ [IMAGE CATALOG] Loaded into MongoDB collection: {DATABASE_NAME}.disease_metadata")

# --- 5. CLEANUP ---
spark.stop()
print("\n--- Pipeline Complete. Spark Session Closed ---")