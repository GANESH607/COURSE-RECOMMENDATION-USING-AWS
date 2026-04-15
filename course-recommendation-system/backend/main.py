# from fastapi import FastAPI, HTTPException, Depends
# from fastapi.security import OAuth2PasswordRequestForm
# from boto3.dynamodb.conditions import Attr
# import uuid
# from datetime import datetime
# import numpy as np
# import pandas as pd
# import boto3
# import io
# from fastapi.middleware.cors import CORSMiddleware

# from models import UserSignup
# from database import (
#     users_table,
#     load_courses_from_s3,
#     load_embeddings,
#     course_interactions_table
# )
# from auth import (
#     hash_password,
#     verify_password,
#     create_access_token,
#     get_current_user
# )
# from ai_interview import (
#     generate_interview_questions,
#     extract_preferences,
#     generate_explanation
# )

# app = FastAPI(title="Course Recommendation System API")
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:5173"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # -----------------------------
# # Health Check
# # -----------------------------
# @app.get("/")
# def root():
#     return {"message": "Backend is running successfully 🚀"}

# # -----------------------------
# # Signup
# # -----------------------------
# @app.post("/signup")
# def signup(user: UserSignup):

#     response = users_table.scan(
#         FilterExpression=Attr("email").eq(user.email)
#     )

#     if response["Items"]:
#         raise HTTPException(status_code=400, detail="User already exists")

#     hashed_password = hash_password(user.password)
#     user_id = str(uuid.uuid4())

#     users_table.put_item(
#         Item={
#             "user_id": user_id,
#             "email": user.email,
#             "password": hashed_password,
#             "full_name": user.full_name
#         }
#     )

#     return {
#         "message": "User created successfully",
#         "user_id": user_id
#     }

# # -----------------------------
# # Login
# # -----------------------------
# @app.post("/login")
# def login(form_data: OAuth2PasswordRequestForm = Depends()):

#     response = users_table.scan(
#         FilterExpression=Attr("email").eq(form_data.username)
#     )

#     if not response["Items"]:
#         raise HTTPException(status_code=400, detail="Invalid credentials")

#     db_user = response["Items"][0]

#     if not verify_password(form_data.password, db_user["password"]):
#         raise HTTPException(status_code=400, detail="Invalid credentials")

#     access_token = create_access_token(
#         data={"sub": db_user["user_id"]}
#     )

#     return {
#         "access_token": access_token,
#         "token_type": "bearer"
#     }

# # -----------------------------
# # Hybrid Recommendation Engine
# # -----------------------------
# @app.get("/recommendations")
# def get_recommendations(user_id: str = Depends(get_current_user)):

#     user_factors, item_factors, user_mapping, course_mapping = load_embeddings()
#     courses_df = load_courses_from_s3()

#     user_row = user_mapping[user_mapping["user_id"] == user_id]

#     # -----------------------------------
#     # COLD START
#     # -----------------------------------
#     if user_row.empty:

#         user_data = users_table.get_item(Key={"user_id": user_id})
#         preferences = user_data.get("Item", {}).get("preferences")

#         filtered = courses_df

#         if preferences:
#             subject = preferences.get("subject")
#             level = preferences.get("level")

#             if subject:
#                 filtered = filtered[
#                     filtered["subject"].str.contains(subject, case=False, na=False)
#                 ]

#             if level:
#                 filtered = filtered[
#                     filtered["level"].str.contains(level, case=False, na=False)
#                 ]

#         if filtered.empty:
#             filtered = courses_df

#         top_courses = filtered.sort_values(
#             by="popularity_score",
#             ascending=False
#         ).head(10)

#         final_output = []

#         for _, row in top_courses.iterrows():
#             explanation = generate_explanation(
#                 preferences,
#                 row["course_title"],
#                 row["subject"],
#                 row["level"]
#             )

#             final_output.append({
#                 "course_id": row["course_id"],
#                 "course_title": row["course_title"],
#                 "subject": row["subject"],
#                 "level": row["level"],
#                 "explanation": explanation
#             })

#         return {
#             "user_id": user_id,
#             "cold_start": True,
#             "recommendations": final_output
#         }

#     # -----------------------------------
#     # COLLABORATIVE + CONTENT HYBRID
#     # -----------------------------------

#     user_index = user_row["userIndex"].values[0]
#     user_vector = user_factors[
#         user_factors["id"] == user_index
#     ]["features"].values[0]

#     # Collaborative score
#     item_factors["collab_score"] = item_factors["features"].apply(
#         lambda item_vec: np.dot(user_vector, item_vec)
#     )

#     merged = item_factors.merge(
#         course_mapping,
#         left_on="id",
#         right_on="courseIndex"
#     ).merge(
#         courses_df,
#         on="course_id"
#     )

#     user_data = users_table.get_item(Key={"user_id": user_id})
#     preferences = user_data.get("Item", {}).get("preferences")

#     def content_score(row):
#         score = 0
#         if preferences:
#             subject = preferences.get("subject")
#             level = preferences.get("level")

#             if subject and subject.lower() in str(row["subject"]).lower():
#                 score += 1

#             if level and level.lower() in str(row["level"]).lower():
#                 score += 1

#         return score / 2

#     merged["content_score"] = merged.apply(content_score, axis=1)

#     merged["final_score"] = (
#         0.6 * merged["collab_score"] +
#         0.4 * merged["content_score"]
#     )

#     top_courses = merged.sort_values(
#         by="final_score",
#         ascending=False
#     ).head(10)

#     final_output = []

#     for _, row in top_courses.iterrows():
#         explanation = generate_explanation(
#             preferences,
#             row["course_title"],
#             row["subject"],
#             row["level"]
#         )

#         final_output.append({
#             "course_id": row["course_id"],
#             "course_title": row["course_title"],
#             "subject": row["subject"],
#             "level": row["level"],
#             "explanation": explanation
#         })

#     return {
#         "user_id": user_id,
#         "hybrid": True,
#         "recommendations": final_output
#     }

# # -----------------------------
# # Store Course Rating
# # -----------------------------
# @app.post("/rate-course")
# def rate_course(
#     course_id: str,
#     rating: int,
#     user_id: str = Depends(get_current_user)
# ):

#     if rating < 1 or rating > 5:
#         raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

#     course_interactions_table.put_item(
#         Item={
#             "user_id": user_id,
#             "course_id": course_id,
#             "rating": rating,
#             "timestamp": str(datetime.utcnow())
#         }
#     )

#     return {"message": "Rating stored successfully"}

# # -----------------------------
# # AI Interview Questions
# # -----------------------------
# @app.get("/cold-start-questions")
# def cold_start_questions(user_id: str = Depends(get_current_user)):

#     questions = generate_interview_questions()

#     return {
#         "user_id": user_id,
#         "questions": questions
#     }

# # -----------------------------
# # Submit Interview Answers
# # -----------------------------
# @app.post("/submit-interview")
# def submit_interview(
#     answers: str,
#     user_id: str = Depends(get_current_user)
# ):

#     preferences = extract_preferences(answers)

#     users_table.update_item(
#         Key={"user_id": user_id},
#         UpdateExpression="SET preferences = :p",
#         ExpressionAttributeValues={":p": preferences}
#     )

#     return {
#         "message": "Preferences saved",
#         "preferences": preferences
#     }


# @app.post("/export-interactions")
# def export_interactions():

#     # Fetch all ratings
#     response = course_interactions_table.scan()
#     items = response.get("Items", [])

#     if not items:
#         return {"message": "No interactions found"}

#     df = pd.DataFrame(items)

#     # Keep required columns
#     df = df[["user_id", "course_id", "rating"]]

#     # Save locally
#     df.to_csv("interactions.csv", index=False)

#     # Upload to S3
#     s3 = boto3.client("s3")
#     s3.upload_file("interactions.csv", "course-recommendation-ganesh", "interactions.csv")

#     return {
#         "message": "Interactions exported to S3 successfully",
#         "total_records": len(df)
#     }

# from retrain import retrain_model

# @app.post("/retrain-model")
# def retrain():

#     message = retrain_model()

#     return {"status": message}

# from mangum import Mangum
# handler=Mangum(app)

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from boto3.dynamodb.conditions import Attr
import uuid
from datetime import datetime
from pydantic import BaseModel
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
class UserSignup(BaseModel):
    full_name: str
    email: str
    password: str


@app.post("/signup")
def signup(user: UserSignup):

    # Check if user already exists
    response = users_table.scan(
        FilterExpression=Attr("email").eq(user.email)
    )

    if response["Items"]:
        raise HTTPException(status_code=400, detail="User already exists")

    # Hash password
    hashed_password = hash_password(user.password)

    # Generate unique user id
    user_id = str(uuid.uuid4())

    # Store user in DynamoDB
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
        # -----------------------------------
    # COLD START (SMART SCORING)
    # -----------------------------------
    if user_row.empty:

        user_data = users_table.get_item(Key={"user_id": user_id})
        preferences = user_data.get("Item", {}).get("preferences")

        df = courses_df.copy()

        # If no preferences saved yet → fallback to popular courses
        if not preferences:
            top_courses = df.sort_values(
                by="popularity_score",
                ascending=False
            ).head(10)

        else:
            subject_pref = preferences.get("subject")
            level_pref = preferences.get("level")
            duration_pref = preferences.get("duration_preference")
            budget_pref = preferences.get("budget_preference")

            def compute_score(row):
                score = 0

                # Subject match (weight 3)
                if subject_pref and subject_pref.lower() in str(row["subject"]).lower():
                    score += 3

                # Level match (weight 2)
                if level_pref and level_pref.lower() in str(row["level"]).lower():
                    score += 2

                # Budget match (weight 1)
                if budget_pref:
                    if budget_pref.lower() == "free" and row["is_paid"] == False:
                        score += 1
                    elif budget_pref.lower() == "paid" and row["is_paid"] == True:
                        score += 1

                # Duration match (weight 1)
                if duration_pref:
                    try:
                        duration_hours = float(str(row["content_duration"]).split()[0])
                    except:
                        duration_hours = 0

                    if duration_pref.lower() == "short" and duration_hours < 5:
                        score += 1
                    elif duration_pref.lower() == "medium" and 5 <= duration_hours <= 15:
                        score += 1
                    elif duration_pref.lower() == "long" and duration_hours > 15:
                        score += 1

                return score

            df["preference_score"] = df.apply(compute_score, axis=1)

            # Normalize popularity
            max_pop = df["popularity_score"].max()
            if max_pop == 0:
                df["popularity_norm"] = 0
            else:
                df["popularity_norm"] = df["popularity_score"] / max_pop

            # Final weighted score
            df["final_score"] = (
                0.7 * df["preference_score"] +
                0.3 * df["popularity_norm"]
            )

            top_courses = df.sort_values(
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

@app.post("/chat-recommendation")
def chat_recommendation(
    message: str,
    user_id: str = Depends(get_current_user)
):

    courses_df = load_courses_from_s3()

    user_data = users_table.get_item(Key={"user_id": user_id})
    preferences = user_data.get("Item", {}).get("preferences")

    if not preferences:
        raise HTTPException(status_code=400, detail="User preferences not found")

    # Reuse cold start scoring logic
    subject_pref = preferences.get("subject")
    level_pref = preferences.get("level")

    df = courses_df.copy()

    if subject_pref:
        df = df[df["subject"].str.contains(subject_pref, case=False, na=False)]

    if level_pref:
        df = df[df["level"].str.contains(level_pref, case=False, na=False)]

    if df.empty:
        df = courses_df

    best_course = df.sort_values(
        by="popularity_score",
        ascending=False
    ).iloc[0]

    explanation = generate_explanation(
        preferences,
        best_course["course_title"],
        best_course["subject"],
        best_course["level"]
    )

    return {
    "recommended_course": {
        "course_id": int(best_course["course_id"]),
        "course_title": str(best_course["course_title"]),
        "subject": str(best_course["subject"]),
        "level": str(best_course["level"]),
        "url": str(best_course["url"]),
        "price": float(best_course["price"]) if best_course["price"] is not None else 0,
        "is_paid": bool(best_course["is_paid"])
    },
    "explanation": explanation
}

@app.get("/course-details/{course_id}")
def get_course_details(
    course_id: str,
    user_id: str = Depends(get_current_user)
):

    courses_df = load_courses_from_s3()

    course = courses_df[courses_df["course_id"] == int(course_id)]

    if course.empty:
        raise HTTPException(status_code=404, detail="Course not found")

    row = course.iloc[0]

    return {
    "course_id": int(row["course_id"]),
    "course_title": str(row["course_title"]),
    "subject": str(row["subject"]),
    "level": str(row["level"]),
    "price": float(row["price"]) if row["price"] is not None else 0,
    "is_paid": bool(row["is_paid"]),
    "num_lectures": int(row["num_lectures"]),
    "content_duration": str(row["content_duration"]),
    "url": str(row["url"])
}


from mangum import Mangum
handler=Mangum(app)