"""
Hybrid Recommendation Engine
Content-Based (TF-IDF + Cosine Similarity) + Collaborative Filtering
"""
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from database import get_connection, get_user_interactions, get_all_courses
import random

class HybridRecommender:
    def __init__(self):
        self.courses_df = None
        self.tfidf_matrix = None
        self.cosine_sim = None
        self.vectorizer = None
        self.load_courses()
    
    def load_courses(self):
        """Load courses and compute TF-IDF matrix"""
        self.courses_df = get_all_courses()
        
        # Create combined text for TF-IDF
        self.courses_df["combined_text"] = (
            self.courses_df["title"].fillna("") + " " +
            self.courses_df["description"].fillna("") + " " +
            self.courses_df["skills"].fillna("") + " " +
            self.courses_df["category"].fillna("")
        )
        
        # TF-IDF Vectorization
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=5000,
            ngram_range=(1, 2)
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(self.courses_df["combined_text"])
        
        # Compute cosine similarity matrix
        self.cosine_sim = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)
        
        print(f"✅ Recommender loaded with {len(self.courses_df)} courses")
    
    def content_based_recommendations(self, course_ids, top_n=10):
        """
        Get content-based recommendations based on course IDs
        Uses TF-IDF + Cosine Similarity
        """
        if not course_ids or len(course_ids) == 0:
            return pd.DataFrame()
        
        # Get indices of input courses
        indices = []
        for cid in course_ids:
            idx = self.courses_df[self.courses_df["course_id"] == cid].index
            if len(idx) > 0:
                indices.append(idx[0])
        
        if not indices:
            return pd.DataFrame()
        
        # Calculate mean similarity scores
        sim_scores = np.mean(self.cosine_sim[indices], axis=0)
        
        # Get top similar courses (excluding input courses)
        sim_indices = sim_scores.argsort()[::-1]
        recommended_indices = []
        
        for idx in sim_indices:
            if idx not in indices and len(recommended_indices) < top_n:
                recommended_indices.append(idx)
        
        recommendations = self.courses_df.iloc[recommended_indices].copy()
        recommendations["similarity_score"] = sim_scores[recommended_indices]
        recommendations["rec_type"] = "Content-Based"
        
        return recommendations
    
    def collaborative_recommendations(self, user_id, top_n=10):
        """
        Collaborative filtering based on user interactions
        Uses implicit feedback (views, purchases, ratings)
        """
        conn = get_connection()
        
        # Get all user interactions
        interactions_df = pd.read_sql_query("""
            SELECT user_id, course_id, action_type, COUNT(*) as count
            FROM user_interactions
            GROUP BY user_id, course_id, action_type
        """, conn)
        
        if len(interactions_df) == 0:
            conn.close()
            return pd.DataFrame()
        
        # Create user-item matrix with implicit ratings
        # Assign weights: purchase=5, rate=4, view=2
        weight_map = {"purchase": 5, "rate": 4, "view": 2}
        interactions_df["weight"] = interactions_df["action_type"].map(weight_map).fillna(1)
        interactions_df["implicit_rating"] = interactions_df["count"] * interactions_df["weight"]
        
        # Get user's courses
        user_courses = interactions_df[interactions_df["user_id"] == user_id]["course_id"].tolist()
        
        if not user_courses:
            conn.close()
            return pd.DataFrame()
        
        # Find similar users (users who interacted with same courses)
        similar_users = interactions_df[
            (interactions_df["course_id"].isin(user_courses)) &
            (interactions_df["user_id"] != user_id)
        ]["user_id"].unique()
        
        if len(similar_users) == 0:
            conn.close()
            return pd.DataFrame()
        
        # Get courses from similar users that target user hasn't seen
        similar_user_courses = interactions_df[
            (interactions_df["user_id"].isin(similar_users)) &
            (~interactions_df["course_id"].isin(user_courses))
        ].groupby("course_id")["implicit_rating"].sum().reset_index()
        
        similar_user_courses = similar_user_courses.sort_values(
            "implicit_rating", ascending=False
        ).head(top_n)
        
        conn.close()
        
        # Get course details
        recommended_courses = self.courses_df[
            self.courses_df["course_id"].isin(similar_user_courses["course_id"])
        ].copy()
        
        # Merge with scores
        recommended_courses = recommended_courses.merge(
            similar_user_courses, on="course_id", how="left"
        )
        recommended_courses["rec_type"] = "Collaborative"
        
        return recommended_courses
    
    def hybrid_recommendations(self, user_id, top_n=10):
        """
        Hybrid recommendation combining content-based and collaborative
        Weight: 60% content-based + 40% collaborative
        """
        # Get user's enrolled/completed courses
        conn = get_connection()
        user_orders = pd.read_sql_query(
            "SELECT course_id FROM orders WHERE user_id = ?",
            conn, params=(user_id,)
        )
        conn.close()
        
        user_course_ids = user_orders["course_id"].tolist()
        
        # Content-based recommendations
        content_recs = self.content_based_recommendations(user_course_ids, top_n=top_n*2)
        
        # Collaborative recommendations
        collab_recs = self.collaborative_recommendations(user_id, top_n=top_n*2)
        
        # If no collaborative data, return content-based
        if len(collab_recs) == 0:
            return content_recs.head(top_n) if len(content_recs) > 0 else self.get_trending_courses(top_n)
        
        # Normalize scores
        if len(content_recs) > 0:
            content_recs["norm_score"] = content_recs["similarity_score"] / content_recs["similarity_score"].max()
        else:
            content_recs["norm_score"] = 0
        
        if len(collab_recs) > 0:
            collab_recs["norm_score"] = collab_recs["implicit_rating"] / collab_recs["implicit_rating"].max()
        else:
            collab_recs["norm_score"] = 0
        
        # Combine scores with weights
        content_recs["hybrid_score"] = content_recs["norm_score"] * 0.6
        collab_recs["hybrid_score"] = collab_recs["norm_score"] * 0.4
        
        # Merge and deduplicate
        all_recs = pd.concat([content_recs, collab_recs], ignore_index=True)
        all_recs = all_recs.sort_values("hybrid_score", ascending=False)
        all_recs = all_recs.drop_duplicates(subset=["course_id"], keep="first")
        
        return all_recs.head(top_n)
    
    def get_trending_courses(self, top_n=10):
        """Get trending courses based on ratings and reviews"""
        trending = self.courses_df.nlargest(top_n, ["rating", "num_reviews"]).copy()
        trending["rec_type"] = "Trending"
        trending["hybrid_score"] = trending["rating"] / 5.0
        return trending
    
    def get_cold_start_recommendations(self, top_n=10):
        """Recommendations for new users - popular across categories"""
        # Pick top-rated courses from each category
        categories = self.courses_df["category"].unique()
        recommendations = []
        
        for cat in categories:
            cat_courses = self.courses_df[self.courses_df["category"] == cat]
            top_course = cat_courses.nlargest(1, "rating")
            if len(top_course) > 0:
                recommendations.append(top_course)
        
        # Fill with overall trending if needed
        if len(recommendations) < top_n:
            remaining = top_n - len(recommendations)
            trending = self.courses_df.nlargest(remaining, ["rating", "num_reviews"])
            recommendations.append(trending)
        
        result = pd.concat(recommendations, ignore_index=True).drop_duplicates("course_id")
        result["rec_type"] = "Popular"
        result["hybrid_score"] = result["rating"] / 5.0
        return result.head(top_n)
    
    def get_similar_courses(self, course_id, top_n=5):
        """Get courses similar to a specific course"""
        return self.content_based_recommendations([course_id], top_n=top_n)
    
    def search_courses(self, query, top_n=20):
        """Search courses using TF-IDF similarity"""
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        top_indices = similarities.argsort()[::-1][:top_n]
        results = self.courses_df.iloc[top_indices].copy()
        results["search_score"] = similarities[top_indices]
        return results[results["search_score"] > 0.01]

# Global recommender instance
recommender = HybridRecommender()

def get_recommendations_for_user(user_id, top_n=10):
    """Get personalized recommendations for a user"""
    # Check if user has any interactions
    conn = get_connection()
    user_orders = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM orders WHERE user_id = ?",
        conn, params=(user_id,)
    )
    user_interactions = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM user_interactions WHERE user_id = ?",
        conn, params=(user_id,)
    )
    conn.close()
    
    has_history = user_orders.iloc[0]["count"] > 0 or user_interactions.iloc[0]["count"] > 0
    
    if has_history:
        return recommender.hybrid_recommendations(user_id, top_n)
    else:
        return recommender.get_cold_start_recommendations(top_n)

if __name__ == "__main__":
    # Test the recommender
    rec = HybridRecommender()
    
    print("\n--- Trending Courses ---")
    trending = rec.get_trending_courses(5)
    print(trending[["title", "category", "rating"]].to_string())
    
    print("\n--- Cold Start Recommendations ---")
    cold = rec.get_cold_start_recommendations(5)
    print(cold[["title", "category", "rating"]].to_string())

