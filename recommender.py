import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from database import get_all_courses, get_user_orders

class HybridRecommender:
    def __init__(self):
        self.courses_df = None
        self.tfidf_matrix = None
        self.cosine_sim = None
        self.vectorizer = None
        self.load_courses()

    def load_courses(self):
        self.courses_df = get_all_courses()

        # Handle missing column
        if "num_reviews" not in self.courses_df.columns:
            self.courses_df["num_reviews"] = 0

        self.courses_df["combined_text"] = (
            self.courses_df["title"].fillna("") + " " +
            self.courses_df["description"].fillna("") + " " +
            self.courses_df["skills"].fillna("") + " " +
            self.courses_df["category"].fillna("")
        )

        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.tfidf_matrix = self.vectorizer.fit_transform(self.courses_df["combined_text"])
        self.cosine_sim = cosine_similarity(self.tfidf_matrix)

    # ================= CONTENT BASED =================
    def content_based_recommendations(self, course_ids, top_n=10):
        if not course_ids:
            return pd.DataFrame()

        indices = []
        for cid in course_ids:
            idx = self.courses_df[self.courses_df["course_id"] == cid].index
            if len(idx) > 0:
                indices.append(idx[0])

        if not indices:
            return pd.DataFrame()

        sim_scores = np.mean(self.cosine_sim[indices], axis=0)
        top_indices = sim_scores.argsort()[::-1]

        results = []
        for i in top_indices:
            if i not in indices and len(results) < top_n:
                results.append(i)

        recs = self.courses_df.iloc[results].copy()
        return recs

    # ================= TRENDING =================
    def get_trending_courses(self, top_n=10):
        return self.courses_df.sort_values(by="rating", ascending=False).head(top_n)

    # ================= SIMILAR =================
    def get_similar_courses(self, course_id, top_n=5):
        return self.content_based_recommendations([course_id], top_n)

    # ================= HYBRID =================
    def hybrid_recommendations(self, user_id, top_n=10):
        orders = get_user_orders(user_id)

        if orders.empty:
            return self.get_trending_courses(top_n)

        user_courses = orders["course_id"].tolist()

        content_recs = self.content_based_recommendations(user_courses, top_n)

        if content_recs.empty:
            return self.get_trending_courses(top_n)

        return content_recs.head(top_n)

# Global instance
recommender = HybridRecommender()

def get_recommendations_for_user(user_id, top_n=10):
    return recommender.hybrid_recommendations(user_id, top_n)

