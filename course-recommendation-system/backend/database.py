import boto3
import os

dynamodb = boto3.resource(
    'dynamodb',
    region_name='us-east-1'
)
import boto3
import pandas as pd
import io

s3 = boto3.client('s3', region_name='ap-south-1')

BUCKET_NAME = "course-recommendation-ganesh"

def load_courses_from_s3():
    response = s3.get_object(Bucket=BUCKET_NAME, Key="cleaned_courses.csv")
    csv_content = response["Body"].read()
    df = pd.read_csv(io.BytesIO(csv_content))
    return df

users_table = dynamodb.Table('users')
course_interactions_table = dynamodb.Table('CourseInteractions')

import pandas as pd
import numpy as np
import io

# -----------------------------
# Load CSV from S3
# -----------------------------

import time
import io
import pandas as pd
from botocore.exceptions import ResponseStreamingError

def load_csv_from_s3(key, retries=3):
    for attempt in range(retries):
        try:
            response = s3.get_object(Bucket=BUCKET_NAME, Key=key)
            csv_content = response["Body"].read()
            return pd.read_csv(io.BytesIO(csv_content))
        except ResponseStreamingError as e:
            print(f"S3 read failed (attempt {attempt+1}), retrying...")
            time.sleep(2)

    raise Exception("Failed to download file from S3 after multiple attempts")

# -----------------------------
# Load Embeddings
# -----------------------------

def load_embeddings():
    user_factors = load_csv_from_s3("embeddings/user_factors.csv")
    item_factors = load_csv_from_s3("embeddings/item_factors.csv")
    user_mapping = load_csv_from_s3("embeddings/user_index_mapping.csv")
    course_mapping = load_csv_from_s3("embeddings/course_index_mapping.csv")

    # Convert string list to numpy array
    user_factors["features"] = user_factors["features"].apply(
        lambda x: np.array(eval(x))
    )

    item_factors["features"] = item_factors["features"].apply(
        lambda x: np.array(eval(x))
    )

    return user_factors, item_factors, user_mapping, course_mapping