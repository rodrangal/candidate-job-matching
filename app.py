import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
import re

# Download NLTK stopwords at runtime (only first time)
nltk.download("stopwords", quiet=True)
STOPWORDS = set(stopwords.words("english"))

# Text preprocessing
def preprocess(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z\s]", "", text)  # keep only letters
    tokens = [word for word in text.split() if word not in STOPWORDS]
    return " ".join(tokens)

# Load sample data
@st.cache_data
def load_data():
    jobs = pd.DataFrame({
        "job_id": [1, 2],
        "title": ["Data Scientist", "HR Manager"],
        "description": [
            "Looking for data scientist with Python and ML experience",
            "HR manager with recruitment and communication skills"
        ]
    })
    candidates = pd.DataFrame({
        "candidate_id": [101, 102],
        "name": ["Alice", "Bob"],
        "resume": [
            "Experienced in Python, machine learning, and statistics",
            "Skilled in human resources, recruitment, and people management"
        ]
    })
    return jobs, candidates

# Candidate-job matching
def match_candidates(jobs, candidates):
    jobs["cleaned"] = jobs["description"].apply(preprocess)
    candidates["cleaned"] = candidates["resume"].apply(preprocess)

    combined = pd.concat([jobs["cleaned"], candidates["cleaned"]])
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform(combined)

    job_tfidf = tfidf[: len(jobs)]
    cand_tfidf = tfidf[len(jobs) :]

    similarity = cosine_similarity(cand_tfidf, job_tfidf)

    results = []
    for i, cand in candidates.iterrows():
        best_idx = similarity[i].argmax()
        best_score = similarity[i][best_idx]
        results.append({
            "candidate": cand["name"],
            "best_job": jobs.iloc[best_idx]["title"],
            "similarity": round(best_score, 2)
        })
    return pd.DataFrame(results)

# Streamlit UI
def main():
    st.title("Candidate–Job Matching Demo (Lightweight)")
    jobs, candidates = load_data()

    if st.button("Run Matching"):
        results = match_candidates(jobs, candidates)
        st.subheader("Best Matches")
        st.dataframe(results)

if __name__ == "__main__":
    main()