# Course Recommendation Web App - Implementation Tracker

## Tech Stack
- **Frontend**: Streamlit (Python-native, rapid UI)
- **Backend**: Flask REST API
- **Database**: SQLite (zero-config, production-ready schema)
- **ML/NLP**: scikit-learn (TF-IDF + Cosine Similarity)
- **Auth**: bcrypt + JWT sessions

---

## Implementation Steps

### ✅ Step 1: Project Setup & Requirements
- [x] Create `requirements.txt`
- [x] Create `TODO.md`
- [x] Create folder structure

### ✅ Step 2: Dataset Generation (1000+ Courses)
- [x] Create `data_generator.py`
- [x] Generate 1200+ realistic courses across 8+ categories
- [x] Save to `models/course_dataset.csv`

### ✅ Step 3: Database Layer
- [x] Create `database.py` with all tables
- [x] Tables: users, courses, orders, reviews, user_interactions
- [x] Seed courses from CSV
- [x] Initialize DB schema

### ✅ Step 4: Authentication Module
- [x] Create `auth.py`
- [x] User registration with bcrypt hashing
- [x] Login/logout with JWT/session
- [x] Password validation & security

### ✅ Step 5: Flask API Backend
- [x] Create `api.py`
- [x] Endpoints: /register, /login, /logout
- [x] Endpoints: /courses, /course/<id>
- [x] Endpoints: /recommend/<user_id>
- [x] Endpoints: /purchase, /orders/<user_id>
- [x] Endpoints: /reviews, /career/<course_id>

### ✅ Step 6: Recommendation Engine
- [x] Create `recommender.py`
- [x] Content-Based: TF-IDF + Cosine Similarity on descriptions/skills
- [x] Collaborative: User interaction matrix
- [x] Hybrid merge with weighted scoring
- [x] Cold-start fallback

### ✅ Step 7: Career Guidance Feature
- [x] Create `career_mapper.py`
- [x] Skills → Job roles mapping
- [x] Salary data & required skills
- [x] API endpoint integration

### ✅ Step 8: Streamlit Frontend
- [x] Create `app.py`
- [x] Home page (recommendations + trending)
- [x] Login/Register pages
- [x] Browse Courses (search + filters)
- [x] Course Detail page
- [x] User Dashboard
- [x] Orders page
- [x] Reviews integration

### ✅ Step 9: Integration & Testing
- [x] Start Flask API server (`python api.py`)
- [x] Launch Streamlit app (`streamlit run app.py`)
- [x] End-to-end purchase flow
- [x] Recommendation accuracy check
- [x] Review system test
- [x] Career guidance display

### ✅ Step 10: Documentation
- [x] Create `README.md`
- [x] Setup instructions
- [x] API documentation

---

## Database Schema

```sql
users (id, name, email, password_hash, created_at)
courses (id, title, category, description, instructor, platform, link, price, rating, duration, level, skills, image_url)
orders (id, user_id, course_id, price, purchase_date, status)
reviews (id, user_id, course_id, rating, review_text, created_at)
user_interactions (id, user_id, course_id, action_type, timestamp)
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/register | POST | User signup |
| /api/login | POST | User login |
| /api/logout | POST | End session |
| /api/courses | GET | List/filter courses |
| /api/course/<id> | GET | Course details |
| /api/recommend/<user_id> | GET | Personalized recommendations |
| /api/purchase | POST | Buy/enroll course |
| /api/orders/<user_id> | GET | Order history |
| /api/reviews | POST/GET | Add/fetch reviews |
| /api/career/<course_id> | GET | Career guidance |

