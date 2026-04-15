import boto3
import subprocess

BUCKET_NAME = "course-recommendation-ganesh"

def retrain_model():

    s3 = boto3.client("s3")

    # Download latest interactions
    s3.download_file(BUCKET_NAME, "interactions.csv", "../ml-training/interactions.csv")

    # Run Spark training script
    subprocess.run(["python", "../ml-training/spark_training.py"])

    # Upload new embeddings to S3
    s3.upload_file("../ml-training/embeddings/user_factors.csv",
                   BUCKET_NAME,
                   "embeddings/user_factors.csv")

    s3.upload_file("../ml-training/embeddings/item_factors.csv",
                   BUCKET_NAME,
                   "embeddings/item_factors.csv")

    s3.upload_file("../ml-training/embeddings/user_index_mapping.csv",
                   BUCKET_NAME,
                   "embeddings/user_index_mapping.csv")

    s3.upload_file("../ml-training/embeddings/course_index_mapping.csv",
                   BUCKET_NAME,
                   "embeddings/course_index_mapping.csv")

    return "Retraining completed successfully"