import pandas as pd
import numpy as np
import random
import uuid

# -----------------------------
# 1. LOAD DATASET
# -----------------------------

df = pd.read_csv("udemy_courses.csv")

print("Original shape:", df.shape)

# -----------------------------
# 2. CLEAN DATA
# -----------------------------

# Fix column names (remove spaces)
df.columns = df.columns.str.strip()

# Remove duplicates
df = df.drop_duplicates(subset=["course_id"])

# Handle missing values
df = df.dropna()

# Convert duration to numeric (if string like "3 hours")
df["content_duration"] = pd.to_numeric(df["content_duration"], errors="coerce")
df = df.dropna()

# -----------------------------
# 3. CREATE POPULARITY SCORE
# -----------------------------

df["popularity_score"] = (
    0.6 * (df["num_subscribers"] / df["num_subscribers"].max()) +
    0.4 * (df["num_reviews"] / df["num_reviews"].max())
)

# Normalize between 0 and 1
df["popularity_score"] = (
    (df["popularity_score"] - df["popularity_score"].min()) /
    (df["popularity_score"].max() - df["popularity_score"].min())
)

# -----------------------------
# 4. SAVE CLEAN COURSES
# -----------------------------

df.to_csv("cleaned_courses.csv", index=False)

print("Cleaned dataset shape:", df.shape)
print("Saved cleaned_courses.csv")

# -----------------------------
# 5. GENERATE SYNTHETIC USERS
# -----------------------------

subjects = df["subject"].unique()
levels = df["level"].unique()

num_users = 10000
users = []

for i in range(num_users):
    users.append({
        "user_id": f"U{i+1}",
        "preferred_subject": random.choice(subjects),
        "preferred_level": random.choice(levels)
    })

users_df = pd.DataFrame(users)
users_df.to_csv("users.csv", index=False)

print("Generated 10,000 users")

# -----------------------------
# 6. GENERATE INTERACTIONS
# -----------------------------

interactions = []

for _, user in users_df.iterrows():
    # Each user interacts with 10–20 courses
    sample_courses = df.sample(random.randint(10, 20))
    
    for _, course in sample_courses.iterrows():
        
        rating = random.randint(3, 5) if course["subject"] == user["preferred_subject"] else random.randint(1, 4)
        
        interactions.append({
            "user_id": user["user_id"],
            "course_id": course["course_id"],
            "rating": rating
        })

interactions_df = pd.DataFrame(interactions)
interactions_df.to_csv("interactions.csv", index=False)

print("Generated interactions:", interactions_df.shape)