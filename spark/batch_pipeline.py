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

    # --- READ INPUT DATA (from Step 2 handoff) ---
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
        (col("humidity") >= 0) & (col("humidity") <= 100)
    )

    # --- CLEAN IMAGE METADATA ---
    image_df = image_df.dropDuplicates()

    image_df = image_df.withColumn(
        "plant", lower(trim(col("plant")))
    ).withColumn(
        "disease", lower(trim(col("disease")))
    )

    print("Data cleaning completed")

    # --- TRANSFORMATIONS ---
    sensor_df = sensor_df.withColumn(
        "date", to_date(col("timestamp"))
    )

    print("Transformations completed")

    # --- AGGREGATION 1: DAILY SENSOR STATISTICS ---
    daily_stats_df = sensor_df.groupBy("date", "field_id").agg(
        avg("humidity").alias("avg_humidity"),
        avg("soil_temp").alias("avg_soil_temp"),
        avg("air_temp").alias("avg_air_temp"),
        avg("ph").alias("avg_ph")
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
