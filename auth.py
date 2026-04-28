"""
Authentication Module - bcrypt + JWT
"""
import bcrypt
import jwt
import datetime
from functools import wraps
from database import get_connection

SECRET_KEY = "course_recommender_secret_key_2024"

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password, hashed):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

def generate_token(user_id, email):
    """Generate JWT token"""
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def decode_token(token):
    """Decode and verify JWT token"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def register_user(name, email, password):
    """Register new user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if email exists
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return {"success": False, "message": "Email already registered"}
    
    # Hash password and insert
    password_hash = hash_password(password)
    cursor.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (name, email, password_hash)
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    
    token = generate_token(user_id, email)
    return {
        "success": True,
        "message": "Registration successful",
        "user_id": user_id,
        "name": name,
        "email": email,
        "token": token
    }

def login_user(email, password):
    """Authenticate user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, email, password_hash FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return {"success": False, "message": "Invalid email or password"}
    
    user_id, name, user_email, password_hash = user
    
    if not verify_password(password, password_hash):
        return {"success": False, "message": "Invalid email or password"}
    
    token = generate_token(user_id, user_email)
    return {
        "success": True,
        "message": "Login successful",
        "user_id": user_id,
        "name": name,
        "email": user_email,
        "token": token
    }

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, created_at FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "created_at": user[3]
        }
    return None

def token_required(f):
    """Decorator for protected routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
        
        if not token:
            return {"success": False, "message": "Token is missing"}, 401
        
        decoded = decode_token(token)
        if not decoded:
            return {"success": False, "message": "Token is invalid or expired"}, 401
        
        return f(decoded["user_id"], *args, **kwargs)
    return decorated

