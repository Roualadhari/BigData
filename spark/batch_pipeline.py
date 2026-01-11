from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, avg, count, to_date, lower, trim
)


def main():
    spark = SparkSession.builder \
        .appName("Smart Agriculture - Spark Batch Pipeline") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")
    print("Spark session started")

    # --- READ INPUT DATA ---
    sensor_df = spark.read \
        .option("header", True) \
        .option("inferSchema", True) \
        .csv("data/handoff/sensor_data.csv")

    image_df = spark.read \
        .option("header", True) \
        .option("inferSchema", True) \
        .csv("data/handoff/image_catalog.csv")

    print("Input data loaded")

    print("Sensor schema:")
    sensor_df.printSchema()

    print("Image catalog schema:")
    image_df.printSchema()

    # --- CLEAN SENSOR DATA ---
    sensor_df = sensor_df.dropna(subset=["timestamp"])

    sensor_df = sensor_df.filter(
        (col("air_humidity") >= 0) & (col("air_humidity") <= 100)
    )

    # --- CLEAN IMAGE METADATA ---
    image_df = image_df.dropDuplicates()

    image_df = image_df.withColumn(
        "plant", lower(trim(col("plant_name")))
    ).withColumn(
        "disease", lower(trim(col("disease_type")))
    )

    print("Data cleaning completed")

    # --- TRANSFORMATIONS ---
    sensor_df = sensor_df.withColumn(
        "date", to_date(col("timestamp"))
    )

    print("Transformations completed")

    # --- AGGREGATION 1: DAILY SENSOR STATISTICS ---
    daily_stats_df = sensor_df.groupBy("date", "sensor_id").agg(
        avg("air_humidity").alias("avg_air_humidity"),
        avg("air_temperature").alias("avg_air_temperature"),
        avg("soil_temperature").alias("avg_soil_temperature"),
        avg("soil_ph").alias("avg_soil_ph")
    )

    print("Daily sensor statistics computed")

    # --- AGGREGATION 2: DISEASE FREQUENCY BY PLANT ---
    disease_freq_df = image_df.groupBy("plant", "disease").agg(
        count("*").alias("cases")
    )

    print("Disease frequency computed")

    # --- WRITE OUTPUTS ---
    daily_stats_df.write \
        .mode("overwrite") \
        .option("header", True) \
        .csv("output/aggregates/daily_sensor_stats")

    disease_freq_df.write \
        .mode("overwrite") \
        .option("header", True) \
        .csv("output/aggregates/disease_frequency")

    print("Outputs written to output/aggregates/")

    spark.stop()
    print("Spark session stopped")


if __name__ == "__main__":
    main()
