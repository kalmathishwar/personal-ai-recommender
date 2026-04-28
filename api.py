"""
Flask REST API Backend
All API endpoints for the Course Recommendation System
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import auth as auth_module
from database import (
    get_all_courses, get_course_by_id, get_user_orders,
    get_course_reviews, create_order, add_review,
    add_user_interaction, get_categories, get_skills_list,
    update_order_status
)
from recommender import get_recommendations_for_user, recommender
from career_mapper import get_career_guidance

app = Flask(__name__)
CORS(app)

def token_required(f):
    """Decorator to protect routes with JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
        
        if not token:
            return jsonify({"success": False, "message": "Token is missing"}), 401
        
        decoded = auth_module.decode_token(token)
        if not decoded:
            return jsonify({"success": False, "message": "Token is invalid or expired"}), 401
        
        return f(decoded["user_id"], *args, **kwargs)
    return decorated

# ==================== AUTH ROUTES ====================

@app.route("/api/register", methods=["POST"])
def register():
    """User registration"""
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    
    if not all([name, email, password]):
        return jsonify({"success": False, "message": "All fields are required"}), 400
    
    if len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters"}), 400
    
    result = auth_module.register_user(name, email, password)
    return jsonify(result), 200 if result["success"] else 409

@app.route("/api/login", methods=["POST"])
def login():
    """User login"""
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    if not all([email, password]):
        return jsonify({"success": False, "message": "Email and password are required"}), 400
    
    result = auth_module.login_user(email, password)
    return jsonify(result), 200 if result["success"] else 401

@app.route("/api/me", methods=["GET"])
@token_required
def get_me(user_id):
    """Get current user info"""
    user = auth_module.get_user_by_id(user_id)
    if user:
        return jsonify({"success": True, "user": user})
    return jsonify({"success": False, "message": "User not found"}), 404

# ==================== COURSE ROUTES ====================

@app.route("/api/courses", methods=["GET"])
def courses():
    """Get all courses with optional filters"""
    filters = {
        "category": request.args.get("category"),
        "level": request.args.get("level"),
        "search": request.args.get("search"),
        "skills": request.args.get("skills"),
        "min_price": request.args.get("min_price", type=float),
        "max_price": request.args.get("max_price", type=float)
    }
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    df = get_all_courses(filters)
    return jsonify({
        "success": True,
        "count": len(df),
        "courses": df.to_dict("records")
    })

@app.route("/api/course/<course_id>", methods=["GET"])
def course_detail(course_id):
    """Get single course details"""
    course = get_course_by_id(course_id)
    if course is not None:
        # Log view interaction if user is authenticated
        token = None
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
        
        if token:
            decoded = auth_module.decode_token(token)
            if decoded:
                add_user_interaction(decoded["user_id"], course_id, "view")
        
        return jsonify({
            "success": True,
            "course": course.to_dict()
        })
    return jsonify({"success": False, "message": "Course not found"}), 404

@app.route("/api/categories", methods=["GET"])
def categories():
    """Get all unique categories"""
    cats = get_categories()
    return jsonify({"success": True, "categories": cats})

@app.route("/api/skills", methods=["GET"])
def skills():
    """Get all unique skills"""
    skills_list = get_skills_list()
    return jsonify({"success": True, "skills": skills_list})

@app.route("/api/trending", methods=["GET"])
def trending():
    """Get trending courses"""
    top_n = request.args.get("limit", 10, type=int)
    trending_courses = recommender.get_trending_courses(top_n)
    return jsonify({
        "success": True,
        "courses": trending_courses.to_dict("records")
    })

# ==================== RECOMMENDATION ROUTES ====================

@app.route("/api/recommend", methods=["GET"])
@token_required
def recommend(user_id):
    """Get personalized recommendations for user"""
    top_n = request.args.get("limit", 10, type=int)
    recommendations = get_recommendations_for_user(user_id, top_n)
    return jsonify({
        "success": True,
        "courses": recommendations.to_dict("records")
    })

@app.route("/api/similar/<course_id>", methods=["GET"])
def similar_courses(course_id):
    """Get courses similar to given course"""
    top_n = request.args.get("limit", 5, type=int)
    similar = recommender.get_similar_courses(course_id, top_n)
    return jsonify({
        "success": True,
        "courses": similar.to_dict("records")
    })

@app.route("/api/search", methods=["GET"])
def search():
    """Search courses"""
    query = request.args.get("q", "")
    top_n = request.args.get("limit", 20, type=int)
    
    if not query:
        return jsonify({"success": False, "message": "Query parameter 'q' is required"}), 400
    
    results = recommender.search_courses(query, top_n)
    return jsonify({
        "success": True,
        "count": len(results),
        "courses": results.to_dict("records")
    })

# ==================== PURCHASE / ORDER ROUTES ====================

@app.route("/api/purchase", methods=["POST"])
@token_required
def purchase(user_id):
    """Purchase/enroll in a course"""
    data = request.get_json()
    course_id = data.get("course_id")
    
    if not course_id:
        return jsonify({"success": False, "message": "course_id is required"}), 400
    
    course = get_course_by_id(course_id)
    if course is None:
        return jsonify({"success": False, "message": "Course not found"}), 404
    
    # Check if already purchased
    orders = get_user_orders(user_id)
    if course_id in orders["course_id"].values:
        return jsonify({"success": False, "message": "Already enrolled in this course"}), 409
    
    # Create order
    order_id = create_order(user_id, course_id, course["price"])
    
    # Log interaction
    add_user_interaction(user_id, course_id, "purchase")
    
    return jsonify({
        "success": True,
        "message": "Enrollment successful",
        "order_id": order_id
    })

@app.route("/api/orders", methods=["GET"])
@token_required
def orders(user_id):
    """Get user's order history"""
    orders_df = get_user_orders(user_id)
    return jsonify({
        "success": True,
        "count": len(orders_df),
        "orders": orders_df.to_dict("records")
    })

@app.route("/api/orders/<int:order_id>/complete", methods=["POST"])
@token_required
def complete_order(user_id, order_id):
    """Mark order as completed"""
    update_order_status(order_id, "Completed")
    return jsonify({"success": True, "message": "Course marked as completed"})

# ==================== REVIEW ROUTES ====================

@app.route("/api/reviews", methods=["GET"])
def get_reviews():
    """Get reviews for a course"""
    course_id = request.args.get("course_id")
    if not course_id:
        return jsonify({"success": False, "message": "course_id is required"}), 400
    
    reviews_df = get_course_reviews(course_id)
    return jsonify({
        "success": True,
        "count": len(reviews_df),
        "reviews": reviews_df.to_dict("records")
    })

@app.route("/api/reviews", methods=["POST"])
@token_required
def create_review(user_id):
    """Add a review"""
    data = request.get_json()
    course_id = data.get("course_id")
    rating = data.get("rating")
    review_text = data.get("review_text", "")
    
    if not all([course_id, rating]):
        return jsonify({"success": False, "message": "course_id and rating are required"}), 400
    
    rating = int(rating)
    if not (1 <= rating <= 5):
        return jsonify({"success": False, "message": "Rating must be between 1 and 5"}), 400
    
    add_review(user_id, course_id, rating, review_text)
    add_user_interaction(user_id, course_id, "rate")
    
    return jsonify({"success": True, "message": "Review added successfully"})

# ==================== CAREER GUIDANCE ROUTES ====================

@app.route("/api/career/<course_id>", methods=["GET"])
def career_guidance(course_id):
    """Get career guidance for a course"""
    course = get_course_by_id(course_id)
    if course is None:
        return jsonify({"success": False, "message": "Course not found"}), 404
    
    category = course["category"]
    guidance = get_career_guidance(category)
    
    return jsonify({
        "success": True,
        "category": category,
        "roles": guidance["roles"],
        "top_skills": guidance["top_skills"]
    })

# ==================== HEALTH CHECK ====================

@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "Course Recommendation API"})

if __name__ == "__main__":
    print("🚀 Starting Flask API server...")
    print("📡 API endpoints available at http://localhost:5000/api/")
    app.run(host="0.0.0.0", port=5000, debug=True)

