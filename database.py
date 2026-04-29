import pandas as pd
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_csv(name):
    path = os.path.join(BASE_DIR, name)
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path)

def save_csv(df, name):
    path = os.path.join(BASE_DIR, name)
    df.to_csv(path, index=False)

# ================= COURSES =================

def get_all_courses(filters=None):
    df = load_csv("courses.csv")

    if filters:
        if "category" in filters:
            df = df[df["category"] == filters["category"]]
        if "level" in filters:
            df = df[df["level"] == filters["level"]]

    return df

def get_course_by_id(course_id):
    df = load_csv("courses.csv")
    course = df[df["course_id"] == int(course_id)]
    return course.iloc[0] if not course.empty else None

def get_categories():
    df = load_csv("courses.csv")
    return df["category"].dropna().unique().tolist()

# ================= USERS =================

def get_user_by_email(email):
    df = load_csv("users.csv")
    user = df[df["email"] == email]
    return user.iloc[0] if not user.empty else None

def create_user(name, email, password):
    df = load_csv("users.csv")
    new_id = len(df) + 1

    new_user = pd.DataFrame([{
        "user_id": new_id,
        "name": name,
        "email": email,
        "password": password
    }])

    df = pd.concat([df, new_user], ignore_index=True)
    save_csv(df, "users.csv")

    return new_id

# ================= ORDERS =================

def create_order(user_id, course_id, price):
    df = load_csv("orders.csv")
    new_id = len(df) + 1

    new_order = pd.DataFrame([{
        "order_id": new_id,
        "user_id": user_id,
        "course_id": course_id,
        "price": price,
        "status": "Ongoing",
        "purchase_date": datetime.now().strftime("%Y-%m-%d")
    }])

    df = pd.concat([df, new_order], ignore_index=True)
    save_csv(df, "orders.csv")

    return new_id

def get_user_orders(user_id):
    orders = load_csv("orders.csv")
    courses = load_csv("courses.csv")

    merged = orders.merge(courses, on="course_id", how="left")
    return merged[merged["user_id"] == user_id]

def update_order_status(order_id, status):
    df = load_csv("orders.csv")
    df.loc[df["order_id"] == order_id, "status"] = status
    save_csv(df, "orders.csv")

# ================= REVIEWS =================

def get_course_reviews(course_id):
    df = load_csv("reviews.csv")
    return df[df["course_id"] == int(course_id)]

def add_review(user_id, course_id, rating, review_text):
    df = load_csv("reviews.csv")
    new_id = len(df) + 1

    new_review = pd.DataFrame([{
        "review_id": new_id,
        "user_id": user_id,
        "course_id": course_id,
        "rating": rating,
        "review_text": review_text,
        "created_at": datetime.now().strftime("%Y-%m-%d")
    }])

    df = pd.concat([df, new_review], ignore_index=True)
    save_csv(df, "reviews.csv")

# ================= INTERACTIONS (DUMMY) =================

def add_user_interaction(user_id, course_id, action):
    pass

