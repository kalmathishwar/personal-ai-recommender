# 🎓 CourseRecommender - AI-Powered Course Recommendation System

A full-stack web application with personalized course recommendations, career guidance, and e-commerce functionality for online learning.

## ✨ Features

- **🔐 Secure Authentication** — User registration & login with bcrypt password hashing and JWT sessions
- **📚 1,200+ Courses** — Rich dataset across 8 categories: Data Science, AI, Web Dev, Mobile Dev, Cloud, Cybersecurity, Business, and Design
- **🤖 Hybrid Recommendation Engine** — Combines Content-Based Filtering (TF-IDF + Cosine Similarity) with Collaborative Filtering for personalized suggestions
- **💼 Career Guidance** — Skills-to-job mapping with salary ranges and growth projections
- **🛒 Course Purchase System** — Enroll in courses with order tracking
- **⭐ Ratings & Reviews** — Community-driven course feedback
- **🔍 Smart Search & Filters** — Find courses by category, level, price, or skills
- **👤 User Dashboard** — Track enrolled/completed courses and gained skills

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Streamlit (Python-native UI) |
| **Backend** | Flask REST API |
| **Database** | SQLite |
| **ML/NLP** | scikit-learn (TF-IDF, Cosine Similarity) |
| **Auth** | bcrypt + JWT |

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Dataset & Initialize Database
```bash
python data_generator.py   # Generates 1200+ courses
python database.py         # Creates SQLite tables and seeds data
```

### 3. Start the Backend API
```bash
python api.py
```
API will run at `http://localhost:5000`

### 4. Launch the Frontend (in a new terminal)
```bash
streamlit run app.py
```
Streamlit will open at `http://localhost:8501`

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/register` | POST | User signup |
| `/api/login` | POST | User login |
| `/api/me` | GET | Current user info |
| `/api/courses` | GET | List/filter courses |
| `/api/course/<id>` | GET | Course details |
| `/api/recommend` | GET | Personalized recommendations |
| `/api/trending` | GET | Trending courses |
| `/api/search` | GET | Search courses |
| `/api/purchase` | POST | Enroll in course |
| `/api/orders` | GET | Order history |
| `/api/reviews` | GET/POST | Get/add reviews |
| `/api/career/<id>` | GET | Career guidance |

## 🗄️ Database Schema

```sql
users (id, name, email, password_hash, created_at)
courses (id, course_id, title, category, description, instructor, platform, course_link, price, rating, duration, level, skills, num_reviews)
orders (id, user_id, course_id, price, purchase_date, status)
reviews (id, user_id, course_id, rating, review_text, created_at)
user_interactions (id, user_id, course_id, action_type, timestamp)
```

## 🤖 Recommendation System

### Content-Based Filtering
- **TF-IDF Vectorizer** on course titles, descriptions, skills, and categories
- **Cosine Similarity** matrix for finding related courses
- Recommends courses similar to user's enrolled/purchased courses

### Collaborative Filtering
- **Implicit feedback** from user interactions (views, ratings, purchases)
- Weighted scoring: purchase=5, rate=4, view=2
- Finds similar users and recommends their preferred courses

### Hybrid Merge
- **60% Content-Based + 40% Collaborative**
- Cold-start fallback: trending/popular courses for new users

## 💼 Career Guidance

Each course category maps to real-world job roles:

| Category | Sample Roles | Salary Range |
|----------|-------------|--------------|
| Data Science | Data Analyst, ML Engineer | $65k - $160k |
| AI | AI Engineer, Research Scientist | $120k - $200k |
| Web Development | Frontend, Full Stack Developer | $70k - $140k |
| Cloud Computing | Cloud Architect, DevOps | $100k - $190k |
| Cybersecurity | Security Analyst, Penetration Tester | $75k - $190k |

## 📁 Project Structure

```
project/
├── app.py                  # Streamlit frontend
├── api.py                  # Flask REST API
├── database.py             # Database models & operations
├── auth.py                 # Authentication helpers
├── recommender.py          # Hybrid recommendation engine
├── career_mapper.py        # Skills → Jobs mapping
├── data_generator.py       # Synthetic dataset generator
├── requirements.txt        # Python dependencies
├── models/
│   ├── course_dataset.csv  # 1200+ courses
│   └── courses.db          # SQLite database
└── README.md
```

## 🎯 Future Enhancements

- [ ] Wishlist / Save for later
- [ ] Email notifications after purchase
- [ ] Payment gateway integration
- [ ] Admin dashboard
- [ ] Mobile app (React Native)

## 📄 License

MIT License — feel free to use and modify for your projects.

---

Built with ❤️ for learners everywhere.

