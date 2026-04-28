"""
Database Layer - SQLite with all required tables
"""
import sqlite3
import pandas as pd
import os
from datetime import datetime

DB_PATH = "models/courses.db"

def get_connection():
    """Get database connection"""
    os.makedirs("models", exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_database():
    """Initialize all tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Courses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            instructor TEXT,
            platform TEXT,
            course_link TEXT,
            price REAL,
            rating REAL,
            duration TEXT,
            level TEXT,
            skills TEXT,
            num_reviews INTEGER DEFAULT 0
        )
    """)
    
    # Orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            course_id TEXT NOT NULL,
            price REAL NOT NULL,
            purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Ongoing',
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (course_id) REFERENCES courses(course_id)
        )
    """)
    
    # Reviews table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            course_id TEXT NOT NULL,
            rating INTEGER NOT NULL,
            review_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (course_id) REFERENCES courses(course_id)
        )
    """)
    
    # User interactions table (for collaborative filtering)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            course_id TEXT NOT NULL,
            action_type TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (course_id) REFERENCES courses(course_id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")

def seed_courses_from_csv(csv_path="models/course_dataset.csv"):
    """Seed courses from generated dataset"""
    conn = get_connection()
    
    # Check if already seeded
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM courses")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"📚 Courses already seeded ({count} courses)")
        conn.close()
        return
    
    df = pd.read_csv(csv_path)
    df.to_sql("courses", conn, if_exists="append", index=False)
    
    print(f"✅ Seeded {len(df)} courses into database")
    conn.close()

def get_all_courses(filters=None):
    """Get courses with optional filters"""
    conn = get_connection()
    query = "SELECT * FROM courses WHERE 1=1"
    params = []
    
    if filters:
        if filters.get("category"):
            query += " AND category = ?"
            params.append(filters["category"])
        if filters.get("level"):
            query += " AND level = ?"
            params.append(filters["level"])
        if filters.get("min_price") is not None:
            query += " AND price >= ?"
            params.append(filters["min_price"])
        if filters.get("max_price") is not None:
            query += " AND price <= ?"
            params.append(filters["max_price"])
        if filters.get("search"):
            query += " AND (title LIKE ? OR description LIKE ? OR skills LIKE ?)"
            search_term = f"%{filters['search']}%"
            params.extend([search_term, search_term, search_term])
        if filters.get("skills"):
            query += " AND skills LIKE ?"
            params.append(f"%{filters['skills']}%")
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def get_course_by_id(course_id):
    """Get single course details"""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM courses WHERE course_id = ?", conn, params=(course_id,))
    conn.close()
    return df.iloc[0] if len(df) > 0 else None

def get_user_orders(user_id):
    """Get user's order history"""
    conn = get_connection()
    query = """
        SELECT o.*, c.title, c.category, c.skills 
        FROM orders o 
        JOIN courses c ON o.course_id = c.course_id 
        WHERE o.user_id = ? 
        ORDER BY o.purchase_date DESC
    """
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    return df

def get_course_reviews(course_id):
    """Get reviews for a course"""
    conn = get_connection()
    query = """
        SELECT r.*, u.name as user_name 
        FROM reviews r 
        JOIN users u ON r.user_id = u.id 
        WHERE r.course_id = ? 
        ORDER BY r.created_at DESC
    """
    df = pd.read_sql_query(query, conn, params=(course_id,))
    conn.close()
    return df

def get_user_interactions(user_id):
    """Get user interactions for collaborative filtering"""
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM user_interactions WHERE user_id = ?",
        conn, params=(user_id,)
    )
    conn.close()
    return df

def add_user_interaction(user_id, course_id, action_type):
    """Log user interaction"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_interactions (user_id, course_id, action_type)
        VALUES (?, ?, ?)
    """, (user_id, course_id, action_type))
    conn.commit()
    conn.close()

def create_order(user_id, course_id, price):
    """Create new order"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO orders (user_id, course_id, price, status)
        VALUES (?, ?, ?, 'Ongoing')
    """, (user_id, course_id, price))
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()
    return order_id

def add_review(user_id, course_id, rating, review_text):
    """Add course review"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reviews (user_id, course_id, rating, review_text)
        VALUES (?, ?, ?, ?)
    """, (user_id, course_id, rating, review_text))
    conn.commit()
    conn.close()

def update_order_status(order_id, status):
    """Update order status"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    conn.commit()
    conn.close()

def get_user_skills(user_id):
    """Get all skills from user's enrolled courses"""
    conn = get_connection()
    query = """
        SELECT c.skills FROM orders o
        JOIN courses c ON o.course_id = c.course_id
        WHERE o.user_id = ? AND o.status = 'Completed'
    """
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    
    all_skills = []
    for skills_str in df["skills"]:
        all_skills.extend([s.strip() for s in skills_str.split(",")])
    return list(set(all_skills))

def get_categories():
    """Get all unique categories"""
    conn = get_connection()
    df = pd.read_sql_query("SELECT DISTINCT category FROM courses", conn)
    conn.close()
    return df["category"].tolist()

def get_skills_list():
    """Get all unique skills"""
    conn = get_connection()
    df = pd.read_sql_query("SELECT skills FROM courses", conn)
    conn.close()
    
    all_skills = set()
    for skills_str in df["skills"]:
        all_skills.update([s.strip() for s in skills_str.split(",")])
    return sorted(list(all_skills))

if __name__ == "__main__":
    init_database()
    if os.path.exists("models/course_dataset.csv"):
        seed_courses_from_csv()
    else:
        print("⚠️ Run data_generator.py first to create the dataset")

