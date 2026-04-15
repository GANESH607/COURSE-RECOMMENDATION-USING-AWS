from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from boto3.dynamodb.conditions import Attr
import uuid
from datetime import datetime
import numpy as np
import pandas as pd
import boto3
import io
from fastapi.middleware.cors import CORSMiddleware

from models import UserSignup
from database import (
    users_table,
    load_courses_from_s3,
    load_embeddings,
    course_interactions_table
)
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)
from ai_interview import (
    generate_interview_questions,
    extract_preferences,
    generate_explanation
)

app = FastAPI(title="Course Recommendation System API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Health Check
# -----------------------------
@app.get("/")
def root():
    return {"message": "Backend is running successfully 🚀"}

# -----------------------------
# Signup
# -----------------------------
@app.post("/signup")
def signup(user: UserSignup):

    response = users_table.scan(
        FilterExpression=Attr("email").eq(user.email)
    )

    if response["Items"]:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = hash_password(user.password)
    user_id = str(uuid.uuid4())

    users_table.put_item(
        Item={
            "user_id": user_id,
            "email": user.email,
            "password": hashed_password,
            "full_name": user.full_name
        }
    )

    return {
        "message": "User created successfully",
        "user_id": user_id
    }

# -----------------------------
# Login
# -----------------------------
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):

    response = users_table.scan(
        FilterExpression=Attr("email").eq(form_data.username)
    )

    if not response["Items"]:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    db_user = response["Items"][0]

    if not verify_password(form_data.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": db_user["user_id"]}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# -----------------------------
# Hybrid Recommendation Engine
# -----------------------------
@app.get("/recommendations")
def get_recommendations(user_id: str = Depends(get_current_user)):

    user_factors, item_factors, user_mapping, course_mapping = load_embeddings()
    courses_df = load_courses_from_s3()

    user_row = user_mapping[user_mapping["user_id"] == user_id]

    # -----------------------------------
    # COLD START
    # -----------------------------------
    if user_row.empty:

        user_data = users_table.get_item(Key={"user_id": user_id})
        preferences = user_data.get("Item", {}).get("preferences")

        filtered = courses_df

        if preferences:
            subject = preferences.get("subject")
            level = preferences.get("level")

            if subject:
                filtered = filtered[
                    filtered["subject"].str.contains(subject, case=False, na=False)
                ]

            if level:
                filtered = filtered[
                    filtered["level"].str.contains(level, case=False, na=False)
                ]

        if filtered.empty:
            filtered = courses_df

        top_courses = filtered.sort_values(
            by="popularity_score",
            ascending=False
        ).head(10)

        final_output = []

        for _, row in top_courses.iterrows():
            explanation = generate_explanation(
                preferences,
                row["course_title"],
                row["subject"],
                row["level"]
            )

            final_output.append({
                "course_id": row["course_id"],
                "course_title": row["course_title"],
                "subject": row["subject"],
                "level": row["level"],
                "explanation": explanation
            })

        return {
            "user_id": user_id,
            "cold_start": True,
            "recommendations": final_output
        }

    # -----------------------------------
    # COLLABORATIVE + CONTENT HYBRID
    # -----------------------------------

    user_index = user_row["userIndex"].values[0]
    user_vector = user_factors[
        user_factors["id"] == user_index
    ]["features"].values[0]

    # Collaborative score
    item_factors["collab_score"] = item_factors["features"].apply(
        lambda item_vec: np.dot(user_vector, item_vec)
    )

    merged = item_factors.merge(
        course_mapping,
        left_on="id",
        right_on="courseIndex"
    ).merge(
        courses_df,
        on="course_id"
    )

    user_data = users_table.get_item(Key={"user_id": user_id})
    preferences = user_data.get("Item", {}).get("preferences")

    def content_score(row):
        score = 0
        if preferences:
            subject = preferences.get("subject")
            level = preferences.get("level")

            if subject and subject.lower() in str(row["subject"]).lower():
                score += 1

            if level and level.lower() in str(row["level"]).lower():
                score += 1

        return score / 2

    merged["content_score"] = merged.apply(content_score, axis=1)

    merged["final_score"] = (
        0.6 * merged["collab_score"] +
        0.4 * merged["content_score"]
    )

    top_courses = merged.sort_values(
        by="final_score",
        ascending=False
    ).head(10)

    final_output = []

    for _, row in top_courses.iterrows():
        explanation = generate_explanation(
            preferences,
            row["course_title"],
            row["subject"],
            row["level"]
        )

        final_output.append({
            "course_id": row["course_id"],
            "course_title": row["course_title"],
            "subject": row["subject"],
            "level": row["level"],
            "explanation": explanation
        })

    return {
        "user_id": user_id,
        "hybrid": True,
        "recommendations": final_output
    }

# -----------------------------
# Store Course Rating
# -----------------------------
@app.post("/rate-course")
def rate_course(
    course_id: str,
    rating: int,
    user_id: str = Depends(get_current_user)
):

    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    course_interactions_table.put_item(
        Item={
            "user_id": user_id,
            "course_id": course_id,
            "rating": rating,
            "timestamp": str(datetime.utcnow())
        }
    )

    return {"message": "Rating stored successfully"}

# -----------------------------
# AI Interview Questions
# -----------------------------
@app.get("/cold-start-questions")
def cold_start_questions(user_id: str = Depends(get_current_user)):

    questions = generate_interview_questions()

    return {
        "user_id": user_id,
        "questions": questions
    }

# -----------------------------
# Submit Interview Answers
# -----------------------------
@app.post("/submit-interview")
def submit_interview(
    answers: str,
    user_id: str = Depends(get_current_user)
):

    preferences = extract_preferences(answers)

    users_table.update_item(
        Key={"user_id": user_id},
        UpdateExpression="SET preferences = :p",
        ExpressionAttributeValues={":p": preferences}
    )

    return {
        "message": "Preferences saved",
        "preferences": preferences
    }


@app.post("/export-interactions")
def export_interactions():

    # Fetch all ratings
    response = course_interactions_table.scan()
    items = response.get("Items", [])

    if not items:
        return {"message": "No interactions found"}

    df = pd.DataFrame(items)

    # Keep required columns
    df = df[["user_id", "course_id", "rating"]]

    # Save locally
    df.to_csv("interactions.csv", index=False)

    # Upload to S3
    s3 = boto3.client("s3")
    s3.upload_file("interactions.csv", "course-recommendation-ganesh", "interactions.csv")

    return {
        "message": "Interactions exported to S3 successfully",
        "total_records": len(df)
    }

from retrain import retrain_model

@app.post("/retrain-model")
def retrain():

    message = retrain_model()

    return {"status": message}

from mangum import Mangum
handler=Mangum(app)