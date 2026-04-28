"""
Streamlit Frontend - Course Recommendation Web App
Pages: Home, Login/Register, Browse, Course Details, Dashboard, Orders
"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# API Base URL
API_URL = "http://localhost:5000/api"

# Page configuration
st.set_page_config(
    page_title="CourseRecommender - Learn Smarter",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .course-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #dee2e6;
    }
    .skill-badge {
        display: inline-block;
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        margin: 2px;
    }
    .price-tag {
        font-size: 1.3rem;
        font-weight: bold;
        color: #2e7d32;
    }
    .rating-stars {
        color: #ffc107;
        font-size: 1.1rem;
    }
    .career-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .job-role {
        background-color: rgba(255,255,255,0.15);
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Session State Management
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "home"
if "selected_course" not in st.session_state:
    st.session_state.selected_course = None

def get_auth_headers():
    """Get headers with auth token"""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}

def make_request(method, endpoint, **kwargs):
    """Make API request with error handling"""
    try:
        url = f"{API_URL}{endpoint}"
        headers = get_auth_headers()
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))
        
        response = requests.request(method, url, headers=headers, timeout=10, **kwargs)
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot connect to backend server. Please make sure `python api.py` is running.")
        return None
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")
        return None

# ==================== SIDEBAR NAVIGATION ====================

def render_sidebar():
    """Render sidebar navigation"""
    with st.sidebar:
        st.markdown("## 🎓 CourseRecommender")
        
        if st.session_state.user:
            st.success(f"👤 {st.session_state.user['name']}")
            st.caption(f"📧 {st.session_state.user['email']}")
        else:
            st.info("👋 Welcome, Guest!")
        
        st.divider()
        
        # Navigation
        pages = {
            "🏠 Home": "home",
            "📚 Browse Courses": "browse",
            "🔍 Search": "search",
        }
        
        if st.session_state.user:
            pages["👤 Dashboard"] = "dashboard"
            pages["🛒 My Orders"] = "orders"
        else:
            pages["🔐 Login / Register"] = "auth"
        
        for label, page_key in pages.items():
            if st.button(label, use_container_width=True, key=f"nav_{page_key}"):
                st.session_state.page = page_key
                st.rerun()
        
        st.divider()
        
        if st.session_state.user:
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.token = None
                st.session_state.user = None
                st.session_state.page = "home"
                st.rerun()
        
        st.caption("© 2024 CourseRecommender")

# ==================== HOME PAGE ====================

def render_home():
    """Render home page with recommendations and trending"""
    st.markdown('<div class="main-header">🎓 CourseRecommender</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Discover personalized courses and accelerate your career</div>', unsafe_allow_html=True)
    
    # Hero section
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📚 Courses", "1,200+")
    with col2:
        st.metric("🎯 Categories", "8+")
    with col3:
        st.metric("🤖 AI Powered", "Yes")
    
    st.divider()
    
    # Personalized Recommendations
    if st.session_state.user:
        st.subheader("🎯 Recommended For You")
        result = make_request("GET", "/recommend?limit=8")
        
        if result and result.get("success"):
            courses = result["courses"]
            if courses:
                cols = st.columns(4)
                for idx, course in enumerate(courses):
                    with cols[idx % 4]:
                        render_course_card(course, prefix="rec_")
            else:
                st.info("Start enrolling in courses to get personalized recommendations!")
        
        st.divider()
    
    # Trending Courses
    st.subheader("🔥 Trending Courses")
    result = make_request("GET", "/trending?limit=8")
    
    if result and result.get("success"):
        courses = result["courses"]
        cols = st.columns(4)
        for idx, course in enumerate(courses):
            with cols[idx % 4]:
                render_course_card(course, prefix="trend_")
    
    # Categories
    st.divider()
    st.subheader("📂 Browse by Category")
    result = make_request("GET", "/categories")
    
    if result and result.get("success"):
        categories = result["categories"]
        cols = st.columns(4)
        for idx, cat in enumerate(categories):
            with cols[idx % 4]:
                if st.button(f"📁 {cat}", use_container_width=True, key=f"cat_{idx}"):
                    st.session_state.page = "browse"
                    st.session_state.selected_category = cat
                    st.rerun()

def render_course_card(course, prefix=""):
    """Render a course card"""
    with st.container():
        st.markdown(f"""
        <div class="course-card">
            <h4>{course['title']}</h4>
            <p><strong>📂</strong> {course['category']} | <strong>📊</strong> {course['level']}</p>
            <p><strong>👤</strong> {course['instructor']} | <strong>🏢</strong> {course['platform']}</p>
            <p><span class="rating-stars">{'⭐' * int(course['rating'])}</span> {course['rating']}</p>
            <p><span class="price-tag">${course['price']}</span></p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("View Details", key=f"{prefix}btn_{course['course_id']}", use_container_width=True):
            st.session_state.selected_course = course["course_id"]
            st.session_state.page = "course_detail"
            st.rerun()

# ==================== AUTH PAGE ====================

def render_auth():
    """Render login/register page"""
    st.markdown('<div class="main-header">🔐 Welcome</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            st.subheader("Login to Your Account")
            email = st.text_input("📧 Email", placeholder="your@email.com")
            password = st.text_input("🔑 Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if not all([email, password]):
                    st.error("Please fill in all fields")
                else:
                    result = make_request("POST", "/login", json={"email": email, "password": password})
                    if result and result.get("success"):
                        st.session_state.token = result["token"]
                        st.session_state.user = {
                            "id": result["user_id"],
                            "name": result["name"],
                            "email": result["email"]
                        }
                        st.success("Login successful!")
                        st.session_state.page = "home"
                        st.rerun()
                    else:
                        st.error(result.get("message", "Login failed"))
    
    with tab2:
        with st.form("register_form"):
            st.subheader("Create New Account")
            name = st.text_input("👤 Full Name", placeholder="John Doe")
            email = st.text_input("📧 Email", placeholder="your@email.com")
            password = st.text_input("🔑 Password", type="password", help="Min 6 characters")
            confirm_password = st.text_input("🔑 Confirm Password", type="password")
            submit = st.form_submit_button("Register", use_container_width=True)
            
            if submit:
                if not all([name, email, password, confirm_password]):
                    st.error("Please fill in all fields")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    result = make_request("POST", "/register", json={
                        "name": name, "email": email, "password": password
                    })
                    if result and result.get("success"):
                        st.session_state.token = result["token"]
                        st.session_state.user = {
                            "id": result["user_id"],
                            "name": result["name"],
                            "email": result["email"]
                        }
                        st.success("Registration successful!")
                        st.session_state.page = "home"
                        st.rerun()
                    else:
                        st.error(result.get("message", "Registration failed"))

# ==================== BROWSE PAGE ====================

def render_browse():
    """Render course browsing page with filters"""
    st.markdown('<div class="main-header">📚 Browse Courses</div>', unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        result = make_request("GET", "/categories")
        categories = ["All"] + (result["categories"] if result and result.get("success") else [])
        selected_category = st.selectbox("📂 Category", categories, index=0)
    
    with col2:
        levels = ["All", "Beginner", "Intermediate", "Advanced"]
        selected_level = st.selectbox("📊 Level", levels)
    
    with col3:
        price_ranges = ["All", "Under $50", "$50 - $100", "$100 - $150", "Over $150"]
        selected_price = st.selectbox("💰 Price", price_ranges)
    
    with col4:
        sort_options = ["Rating", "Price: Low to High", "Price: High to Low", "Most Reviewed"]
        sort_by = st.selectbox("Sort By", sort_options)
    
    # Build filters
    filters = {}
    if selected_category != "All":
        filters["category"] = selected_category
    if selected_level != "All":
        filters["level"] = selected_level
    
    if selected_price == "Under $50":
        filters["max_price"] = 50
    elif selected_price == "$50 - $100":
        filters["min_price"] = 50
        filters["max_price"] = 100
    elif selected_price == "$100 - $150":
        filters["min_price"] = 100
        filters["max_price"] = 150
    elif selected_price == "Over $150":
        filters["min_price"] = 150
    
    # Fetch courses
    query_params = "&".join([f"{k}={v}" for k, v in filters.items()])
    result = make_request("GET", f"/courses?{query_params}")
    
    if result and result.get("success"):
        courses = result["courses"]
        
        # Sort
        if sort_by == "Price: Low to High":
            courses = sorted(courses, key=lambda x: x["price"])
        elif sort_by == "Price: High to Low":
            courses = sorted(courses, key=lambda x: x["price"], reverse=True)
        elif sort_by == "Most Reviewed":
            courses = sorted(courses, key=lambda x: x["num_reviews"], reverse=True)
        else:
            courses = sorted(courses, key=lambda x: x["rating"], reverse=True)
        
        st.write(f"Found {len(courses)} courses")
        
        # Display courses in grid
        cols = st.columns(3)
        for idx, course in enumerate(courses):
            with cols[idx % 3]:
                render_course_card(course, prefix="browse_")
    else:
        st.info("No courses found matching your criteria")

# ==================== SEARCH PAGE ====================

def render_search():
    """Render search page"""
    st.markdown('<div class="main-header">🔍 Search Courses</div>', unsafe_allow_html=True)
    
    query = st.text_input("Search for courses, skills, or topics...", placeholder="e.g., Python, Machine Learning, Web Development")
    
    if query:
        result = make_request("GET", f"/search?q={query}&limit=30")
        
        if result and result.get("success"):
            courses = result["courses"]
            st.write(f"Found {len(courses)} results for '{query}'")
            
            cols = st.columns(3)
            for idx, course in enumerate(courses):
                with cols[idx % 3]:
                    render_course_card(course, prefix="search_")
        else:
            st.info("No results found")
    else:
        st.info("Enter a search term to find courses")

# ==================== COURSE DETAIL PAGE ====================

def render_course_detail():
    """Render detailed course page"""
    course_id = st.session_state.selected_course
    
    result = make_request("GET", f"/course/{course_id}")
    if not result or not result.get("success"):
        st.error("Course not found")
        return
    
    course = result["course"]
    
    # Back button
    if st.button("← Back to Browse"):
        st.session_state.page = "browse"
        st.rerun()
    
    st.markdown(f'<div class="main-header">{course["title"]}</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📖 About This Course")
        st.write(course["description"])
        
        st.subheader("🛠️ Skills You'll Gain")
        skills = [s.strip() for s in course["skills"].split(",")]
        skills_html = " ".join([f'<span class="skill-badge">{skill}</span>' for skill in skills])
        st.markdown(skills_html, unsafe_allow_html=True)
        
        st.subheader("📊 Course Details")
        details_col1, details_col2, details_col3 = st.columns(3)
        with details_col1:
            st.metric("Level", course["level"])
        with details_col2:
            st.metric("Duration", course["duration"])
        with details_col3:
            st.metric("Rating", f"{course['rating']} ⭐")
        
        st.write(f"**Instructor:** {course['instructor']}")
        st.write(f"**Platform:** {course['platform']}")
        st.write(f"**Category:** {course['category']}")
        
        # External link
        st.markdown(f"[🔗 View on {course['platform']}]({course['course_link']})")
    
    with col2:
        st.subheader("💰 Enroll Now")
        st.markdown(f'<div class="price-tag">${course["price"]}</div>', unsafe_allow_html=True)
        
        if st.session_state.user:
            if st.button("🛒 Enroll Now", use_container_width=True, type="primary"):
                result = make_request("POST", "/purchase", json={"course_id": course_id})
                if result and result.get("success"):
                    st.success("🎉 Enrollment successful!")
                else:
                    st.error(result.get("message", "Enrollment failed"))
        else:
            st.info("Please login to enroll")
            if st.button("Login to Enroll", use_container_width=True):
                st.session_state.page = "auth"
                st.rerun()
        
        # Similar courses
        st.divider()
        st.subheader("📚 Similar Courses")
        similar_result = make_request("GET", f"/similar/{course_id}?limit=3")
        if similar_result and similar_result.get("success"):
            for sim_course in similar_result["courses"]:
                st.write(f"• **{sim_course['title']}**")
                st.caption(f"{sim_course['category']} | ${sim_course['price']}")
    
    # Career Guidance
    st.divider()
    st.subheader("💼 Career Opportunities")
    career_result = make_request("GET", f"/career/{course_id}")
    
    if career_result and career_result.get("success"):
        guidance = career_result
        
        st.write(f"**Category:** {guidance['category']}")
        st.write("**Top Skills in this field:**")
        for skill in guidance['top_skills']:
            st.markdown(f'<span class="skill-badge">{skill}</span>', unsafe_allow_html=True)
        
        st.write("\n**Jobs you can apply for:**")
        cols = st.columns(len(guidance['roles']))
        for idx, role in enumerate(guidance['roles']):
            with cols[idx]:
                st.markdown(f"""
                <div class="career-card">
                    <h4>{role['title']}</h4>
                    <div class="job-role">
                        <p>💰 {role['salary']}</p>
                        <p>📈 Growth: {role['growth']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Reviews
    st.divider()
    st.subheader("⭐ Reviews")
    
    reviews_result = make_request("GET", f"/reviews?course_id={course_id}")
    if reviews_result and reviews_result.get("success"):
        reviews = reviews_result["reviews"]
        if reviews:
            for review in reviews:
                with st.container():
                    st.write(f"**{review['user_name']}** - {'⭐' * review['rating']}")
                    st.write(review['review_text'])
                    st.caption(f"Posted on {review['created_at']}")
                    st.divider()
        else:
            st.info("No reviews yet. Be the first to review!")
    
    # Add Review
    if st.session_state.user:
        with st.expander("Write a Review"):
            with st.form("review_form"):
                rating = st.slider("Rating", 1, 5, 5)
                review_text = st.text_area("Your Review")
                submit = st.form_submit_button("Submit Review")
                
                if submit:
                    result = make_request("POST", "/reviews", json={
                        "course_id": course_id,
                        "rating": rating,
                        "review_text": review_text
                    })
                    if result and result.get("success"):
                        st.success("Review submitted!")
                        st.rerun()
                    else:
                        st.error("Failed to submit review")

# ==================== DASHBOARD PAGE ====================

def render_dashboard():
    """Render user dashboard"""
    if not st.session_state.user:
        st.warning("Please login to view dashboard")
        st.session_state.page = "auth"
        st.rerun()
        return
    
    st.markdown('<div class="main-header">👤 My Dashboard</div>', unsafe_allow_html=True)
    
    # Get user orders
    orders_result = make_request("GET", "/orders")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_orders = len(orders_result["orders"]) if orders_result and orders_result.get("success") else 0
        st.metric("📚 Enrolled Courses", total_orders)
    
    with col2:
        completed = sum(1 for o in orders_result["orders"] if o["status"] == "Completed") if orders_result and orders_result.get("success") else 0
        st.metric("✅ Completed", completed)
    
    with col3:
        ongoing = sum(1 for o in orders_result["orders"] if o["status"] == "Ongoing") if orders_result and orders_result.get("success") else 0
        st.metric("🔄 In Progress", ongoing)
    
    st.divider()
    
    # Recommendations
    st.subheader("🎯 Recommended For You")
    rec_result = make_request("GET", "/recommend?limit=6")
    
    if rec_result and rec_result.get("success"):
        courses = rec_result["courses"]
        if courses:
            cols = st.columns(3)
            for idx, course in enumerate(courses):
                with cols[idx % 3]:
                    render_course_card(course, prefix="dash_")
        else:
            st.info("Enroll in courses to get personalized recommendations!")
    
    # Enrolled courses
    st.divider()
    st.subheader("📚 My Courses")
    
    if orders_result and orders_result.get("success"):
        orders = orders_result["orders"]
        if orders:
            for order in orders:
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"**{order['title']}**")
                        st.caption(f"{order['category']} | Enrolled: {order['purchase_date']}")
                    with col2:
                        status_color = "🟢" if order['status'] == "Completed" else "🟡"
                        st.write(f"{status_color} {order['status']}")
                    with col3:
                        if order['status'] == "Ongoing":
                            if st.button("Complete", key=f"complete_{order['id']}"):
                                make_request("POST", f"/orders/{order['id']}/complete")
                                st.success("Marked as completed!")
                                st.rerun()
                    st.divider()
        else:
            st.info("You haven't enrolled in any courses yet. Browse our catalog!")
            if st.button("Browse Courses"):
                st.session_state.page = "browse"
                st.rerun()

# ==================== ORDERS PAGE ====================

def render_orders():
    """Render order history page"""
    if not st.session_state.user:
        st.warning("Please login to view orders")
        st.session_state.page = "auth"
        st.rerun()
        return
    
    st.markdown('<div class="main-header">🛒 Order History</div>', unsafe_allow_html=True)
    
    result = make_request("GET", "/orders")
    
    if result and result.get("success"):
        orders = result["orders"]
        
        if orders:
            total_spent = sum(o["price"] for o in orders)
            st.metric("Total Spent", f"${total_spent:.2f}")
            
            st.divider()
            
            for order in orders:
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    with col1:
                        st.write(f"**{order['title']}**")
                        st.caption(f"Skills: {order['skills']}")
                    with col2:
                        st.write(f"${order['price']}")
                    with col3:
                        st.write(f"{order['purchase_date']}")
                    with col4:
                        status_color = "🟢" if order['status'] == "Completed" else "🟡"
                        st.write(f"{status_color} {order['status']}")
                    st.divider()
        else:
            st.info("No orders yet")
            if st.button("Start Learning"):
                st.session_state.page = "browse"
                st.rerun()

# ==================== MAIN APP ====================

def main():
    """Main application entry point"""
    render_sidebar()
    
    page = st.session_state.page
    
    if page == "home":
        render_home()
    elif page == "auth":
        render_auth()
    elif page == "browse":
        render_browse()
    elif page == "search":
        render_search()
    elif page == "course_detail":
        render_course_detail()
    elif page == "dashboard":
        render_dashboard()
    elif page == "orders":
        render_orders()
    else:
        render_home()

if __name__ == "__main__":
    main()

