# Install pyspark directly (no manual download)
!pip install pyspark
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("KafkaStreaming") \
    .config("spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true") \
    .getOrCreate()
from google.colab import drive
drive.mount('/content/drive')

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_replace, expr

spark = SparkSession.builder.appName("EcommerceProject").getOrCreate()

# Load dataset
file_path = "/content/drive/MyDrive/Big Data Project/electronics_product.csv"

df = spark.read.csv(file_path, header=True, inferSchema=True)

df.show(5)
df.printSchema()
df = df.select(
    col("name").alias("Name"),
    col("main_category").alias("Category"),
    col("sub_category").alias("Sub_Category"),
    col("ratings").alias("Rating"),
    col("no_of_ratings").alias("Rating_Count"),
    col("discount_price").alias("Price")
)
#Cleaning the Data
df = df.withColumn(
    "price_num",
    expr("try_cast(regexp_replace(Price, '[^0-9.]', '') as double)")
)
df = df.withColumn(
    "rating_num",
    expr("try_cast(regexp_replace(Rating, '[^0-9.]', '') as double)")
)
df = df.withColumn(
    "rating_count_num",
    expr("try_cast(regexp_replace(Rating_Count, '[^0-9]', '') as int)")
)
df = df.dropna(subset=["price_num", "rating_num"])
df.select("Name", "Category", "price_num", "rating_num", "rating_count_num").show(10)
#Analysis
#Top expensive products
df.orderBy("price_num", ascending=False).show(10)
#Top rated products
df.orderBy("rating_num", ascending=False).show(10)
#Category-wise average price
df.groupBy("Category").avg("price_num").show()
#Kafka
!wget https://archive.apache.org/dist/kafka/3.5.1/kafka_2.13-3.5.1.tgz
!tar -xzf kafka_2.13-3.5.1.tgz
!kafka_2.13-3.5.1/bin/zookeeper-server-start.sh -daemon kafka_2.13-3.5.1/config/zookeeper.properties
!kafka_2.13-3.5.1/bin/kafka-server-start.sh -daemon kafka_2.13-3.5.1/config/server.properties
!apt-get install openjdk-11-jdk -y
!kafka_2.13-3.5.1/bin/kafka-topics.sh --create \
--topic ecommerce-topic \
--bootstrap-server localhost:9092 \
--partitions 1 \
--replication-factor 1
import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 pyspark-shell'
#Sending Data to Kafka
!pip install kafka-python
df_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "ecommerce-topic") \
    .option("startingOffsets", "latest") \
    .load()
from pyspark.sql.functions import col

df_stream = df_stream.selectExpr("CAST(value AS STRING)")
query = df_stream.writeStream \
    .format("console") \
    .outputMode("append") \
    .start()

query.awaitTermination()
from kafka import KafkaProducer
import json
import pandas as pd

# Load dataset
pdf = df.toPandas()

# Kafka producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Send limited fast data
for index, row in pdf.head(200).iterrows():
    data = row.to_dict()
    producer.send('ecommerce-topic', value=data)

producer.flush()
print("✅ Data Sent Successfully")
