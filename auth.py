import jwt
import datetime
from database import get_user_by_email, create_user
import pandas as pd

SECRET_KEY = "secret123"

# ================= REGISTER =================
def register_user(name, email, password):
    existing = get_user_by_email(email)
    if existing is not None:
        return {"success": False, "message": "User already exists"}

    user_id = create_user(name, email, password)

    token = jwt.encode({
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }, SECRET_KEY, algorithm="HS256")

    return {
        "success": True,
        "token": token,
        "user_id": user_id,
        "name": name,
        "email": email
    }

# ================= LOGIN =================
def login_user(email, password):
    user = get_user_by_email(email)

    if user is None or user["password"] != password:
        return {"success": False, "message": "Invalid credentials"}

    token = jwt.encode({
        "user_id": int(user["user_id"]),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }, SECRET_KEY, algorithm="HS256")

    return {
        "success": True,
        "token": token,
        "user_id": int(user["user_id"]),
        "name": user["name"],
        "email": user["email"]
    }

# ================= GET USER =================
def get_user_by_id(user_id):
    df = pd.read_csv("users.csv")
    user = df[df["user_id"] == user_id]
    return user.iloc[0] if not user.empty else None

# ================= TOKEN =================
def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except:
        return None
