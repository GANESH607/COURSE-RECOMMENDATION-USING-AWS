from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.feature import StringIndexer
import pandas as pd
import shutil
import os

# -----------------------------
# 1. Start Spark Session
# -----------------------------

spark = SparkSession.builder \
    .appName("CourseRecommendationALS") \
    .config("spark.hadoop.hadoop.native.lib", "false") \
    .config("spark.sql.warehouse.dir", "file:///C:/temp") \
    .getOrCreate()

print("Spark Session Started 🚀")

# -----------------------------
# 2. Load Interactions
df = spark.read.csv("interactions.csv", header=True, inferSchema=True)
print("Interactions Loaded ✅")

# -----------------------------
# 3. Convert String IDs to Numeric Index
# -----------------------------

# Fit user indexer
user_indexer = StringIndexer(
    inputCol="user_id",
    outputCol="userIndex",
    handleInvalid="skip"
)

user_indexer_model = user_indexer.fit(df)
df = user_indexer_model.transform(df)

# Fit course indexer
course_indexer = StringIndexer(
    inputCol="course_id",
    outputCol="courseIndex",
    handleInvalid="skip"
)

course_indexer_model = course_indexer.fit(df)
df = course_indexer_model.transform(df)

print("User & Course Indexing Done ✅")

# -----------------------------
# 4. Export Index Mappings
# -----------------------------

os.makedirs("embeddings", exist_ok=True)

# User mapping
user_index_mapping = pd.DataFrame({
    "user_id": user_indexer_model.labels,
    "userIndex": range(len(user_indexer_model.labels))
})

user_index_mapping.to_csv("embeddings/user_index_mapping.csv", index=False)

# Course mapping
course_index_mapping = pd.DataFrame({
    "course_id": course_indexer_model.labels,
    "courseIndex": range(len(course_indexer_model.labels))
})

course_index_mapping.to_csv("embeddings/course_index_mapping.csv", index=False)

print("Index mappings exported ✅")

# -----------------------------
# 5. Train/Test Split
# -----------------------------

(training, test) = df.randomSplit([0.8, 0.2], seed=42)
print("Train/Test Split Done ✅")

# -----------------------------
# 6. Train ALS Model
# -----------------------------

als = ALS(
    maxIter=10,
    regParam=0.1,
    rank=20,
    userCol="userIndex",
    itemCol="courseIndex",
    ratingCol="rating",
    coldStartStrategy="drop",
    nonnegative=True
)

model = als.fit(training)
print("ALS Model Trained ✅")

# -----------------------------
# 7. Evaluate Model
# -----------------------------

predictions = model.transform(test)

evaluator = RegressionEvaluator(
    metricName="rmse",
    labelCol="rating",
    predictionCol="prediction"
)

rmse = evaluator.evaluate(predictions)
print("RMSE:", rmse)

# -----------------------------
# 8. Export User & Item Embeddings
# -----------------------------

# User embeddings
user_factors = model.userFactors.toPandas()
user_factors.to_csv("embeddings/user_factors.csv", index=False)

# Item embeddings
item_factors = model.itemFactors.toPandas()
item_factors.to_csv("embeddings/item_factors.csv", index=False)

print("User and Item embeddings exported ✅")

# -----------------------------
# 9. Stop Spark Session
# -----------------------------

spark.stop()
print("Spark Session Stopped 🔥")