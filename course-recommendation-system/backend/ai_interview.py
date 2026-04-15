# from groq import Groq
# import os

# GROQ_API_KEY = "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"

# client = Groq(api_key=GROQ_API_KEY)

# def generate_interview_questions():
#     prompt = """
#     Generate 5 short questions to understand a user's online course preferences.
#     Ask about:
#     - Preferred subjects
#     - Skill level
#     - Career goals
#     - Learning duration preference
#     - Budget preference
#     Keep questions short and numbered.
#     """

#     response = client.chat.completions.create(
#         model="llama-3.1-8b-instant",
#         messages=[{"role": "user", "content": prompt}]
#     )

#     return response.choices[0].message.content


# import json

# def extract_preferences(user_answers):
#     prompt = f"""
#     Based on the following answers, extract structured preferences.

#     Answers:
#     {user_answers}

#     Return ONLY valid JSON like:
#     {{
#         "subject": "...",
#         "level": "...",
#         "duration_preference": "...",
#         "budget_preference": "..."
#     }}
#     """

#     response = client.chat.completions.create(
#         model="llama-3.1-8b-instant",
#         messages=[{"role": "user", "content": prompt}]
#     )

#     content = response.choices[0].message.content

#     try:
#         return json.loads(content)
#     except:
#         return {"subject": None, "level": None}


# def generate_explanation(user_preferences, course_title, subject, level):
#     prompt = f"""
#     User preferences:
#     {user_preferences}

#     Course:
#     Title: {course_title}
#     Subject: {subject}
#     Level: {level}

#     Explain in 1–2 sentences why this course is recommended.
#     """

#     response = client.chat.completions.create(
#         model="llama-3.1-8b-instant",
#         messages=[{"role": "user", "content": prompt}]
#     )

#     return response.choices[0].message.content

from groq import Groq
import os

GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)

def generate_interview_questions(): 
    prompt = """
    Generate 5 short questions to understand a user's online course preferences.
    Ask about:
    - Preferred subjects
    - Skill level
    - Career goals
    - Learning duration preference
    - Budget preference
    Keep questions short and numbered.
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


import json

def extract_preferences(user_answers):
    prompt = f"""
    Based on the following answers, extract structured preferences.

    Answers:
    {user_answers}

    Return ONLY pure JSON.
    Do NOT add explanation.
    Do NOT wrap in markdown.
    Do NOT write anything else.

    Format:
    {{
        "subject": "...",
        "level": "...",
        "duration_preference": "...",
        "budget_preference": "..."
    }}
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    content = response.choices[0].message.content.strip()

    # Remove markdown if present
    if content.startswith("```"):
        content = content.split("```")[1]

    try:
        return json.loads(content)
    except Exception as e:
        print("JSON Parse Error:", content)
        return {
            "subject": None,
            "level": None,
            "duration_preference": None,
            "budget_preference": None
        }



def generate_explanation(user_preferences, course_title, subject, level):
    prompt = f"""
    User preferences:
    {user_preferences}

    Course:
    Title: {course_title}
    Subject: {subject}
    Level: {level}

    Explain in 1–2 sentences why this course is recommended.
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content