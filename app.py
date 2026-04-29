import streamlit as st
import pandas as pd

# 🔥 IMPORT BACKEND LOGIC DIRECTLY
import auth as auth_module
from database import (
    get_all_courses, get_course_by_id, get_user_orders,
    get_course_reviews, create_order, add_review,
    add_user_interaction, get_categories, update_order_status
)
from recommender import get_recommendations_for_user, recommender
from career_mapper import get_career_guidance

# ================= CONFIG =================
st.set_page_config(page_title="CourseRecommender", layout="wide")

# ================= SESSION =================
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "home"
if "selected_course" not in st.session_state:
    st.session_state.selected_course = None

# ================= SIDEBAR =================
def sidebar():
    with st.sidebar:
        st.title("🎓 CourseRecommender")

        if st.session_state.user:
            st.success(st.session_state.user["name"])
        else:
            st.info("Guest")

        if st.button("🏠 Home"):
            st.session_state.page = "home"

        if st.button("📚 Browse"):
            st.session_state.page = "browse"

        if st.session_state.user:
            if st.button("👤 Dashboard"):
                st.session_state.page = "dashboard"
        else:
            if st.button("🔐 Login"):
                st.session_state.page = "auth"

        if st.session_state.user:
            if st.button("Logout"):
                st.session_state.user = None
                st.session_state.page = "home"

# ================= HOME =================
def home():
    st.title("🎓 CourseRecommender")

    st.subheader("🔥 Trending Courses")
    courses = recommender.get_trending_courses(8).to_dict("records")

    cols = st.columns(4)
    for i, c in enumerate(courses):
        with cols[i % 4]:
            course_card(c)

    if st.session_state.user:
        st.subheader("🎯 Recommended")
        recs = get_recommendations_for_user(
            st.session_state.user["id"], 6
        ).to_dict("records")

        cols = st.columns(3)
        for i, c in enumerate(recs):
            with cols[i % 3]:
                course_card(c)

# ================= COURSE CARD =================
def course_card(course):
    st.markdown(f"**{course['title']}**")
    st.write(course["category"], "|", course["level"])
    st.write(f"⭐ {course['rating']}  💲{course['price']}")

    if st.button("View", key=course["course_id"]):
        st.session_state.selected_course = course["course_id"]
        st.session_state.page = "detail"

# ================= AUTH =================
def auth():
    st.title("Login / Register")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            result = auth_module.login_user(email, password)
            if result["success"]:
                st.session_state.user = {
                    "id": result["user_id"],
                    "name": result["name"]
                }
                st.success("Logged in")
                st.session_state.page = "home"

    with tab2:
        name = st.text_input("Name")
        email = st.text_input("Email", key="r_email")
        password = st.text_input("Password", type="password", key="r_pass")

        if st.button("Register"):
            result = auth_module.register_user(name, email, password)
            if result["success"]:
                st.success("Registered! Login now")

# ================= BROWSE =================
def browse():
    st.title("Browse Courses")

    categories = ["All"] + get_categories()
    cat = st.selectbox("Category", categories)

    filters = {}
    if cat != "All":
        filters["category"] = cat

    df = get_all_courses(filters)
    courses = df.to_dict("records")

    cols = st.columns(3)
    for i, c in enumerate(courses):
        with cols[i % 3]:
            course_card(c)

# ================= DETAIL =================
def detail():
    cid = st.session_state.selected_course
    course = get_course_by_id(cid)

    st.title(course["title"])
    st.write(course["description"])
    st.write("💲", course["price"])

    if st.session_state.user:
        if st.button("Enroll"):
            create_order(
                st.session_state.user["id"],
                cid,
                course["price"]
            )
            st.success("Enrolled!")

    st.subheader("Similar Courses")
    sim = recommender.get_similar_courses(cid, 3).to_dict("records")
    for s in sim:
        st.write("-", s["title"])

# ================= DASHBOARD =================
def dashboard():
    st.title("Dashboard")

    orders = get_user_orders(st.session_state.user["id"])

    for _, o in orders.iterrows():
        st.write(o["title"], "-", o["status"])

# ================= MAIN =================
def main():
    sidebar()

    page = st.session_state.page

    if page == "home":
        home()
    elif page == "auth":
        auth()
    elif page == "browse":
        browse()
    elif page == "detail":
        detail()
    elif page == "dashboard":
        dashboard()

main()

