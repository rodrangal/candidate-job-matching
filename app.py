import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
import re
import pdfplumber

# Download NLTK stopwords (only first time)
nltk.download("stopwords", quiet=True)
STOPWORDS = set(stopwords.words("english"))

# ----------- Text Preprocessing -----------
def preprocess(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z\s]", "", text)  # keep only letters
    tokens = [word for word in text.split() if word not in STOPWORDS]
    return " ".join(tokens)

# ----------- PDF Reader -----------
def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.strip()

# ----------- Data Loaders -----------
def load_job(file):
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
        if "description" not in df.columns:
            st.error("CSV for job must have a 'description' column.")
            return pd.DataFrame()
        return df
    elif file.name.endswith(".txt"):
        text = file.read().decode("utf-8")
        return pd.DataFrame({"job_id": [1], "description": [text]})
    elif file.name.endswith(".pdf"):
        text = read_pdf(file)
        return pd.DataFrame({"job_id": [1], "description": [text]})
    else:
        st.error("Unsupported job file type (use CSV, TXT, or PDF).")
        return pd.DataFrame()

def load_candidates(files):
    records = []
    for idx, file in enumerate(files, start=1):
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
            if "resume" not in df.columns:
                st.error(f"{file.name}: CSV must have a 'resume' column.")
                continue
            for _, row in df.iterrows():
                records.append({"candidate_id": idx, "resume": row["resume"], "name": row.get("name", file.name)})
        elif file.name.endswith(".txt"):
            text = file.read().decode("utf-8")
            records.append({"candidate_id": idx, "resume": text, "name": file.name})
        elif file.name.endswith(".pdf"):
            text = read_pdf(file)
            records.append({"candidate_id": idx, "resume": text, "name": file.name})
        else:
            st.error(f"{file.name}: Unsupported file type (use CSV, TXT, or PDF).")
    return pd.DataFrame(records)

# ----------- Matching Logic -----------
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
            "candidate": cand.get("name", f"Candidate {cand['candidate_id']}"),
            "best_job": jobs.iloc[best_idx].get("title", f"Job {jobs.iloc[best_idx]['job_id']}"),
            "similarity": round(best_score, 2)
        })
    return pd.DataFrame(results)

# ----------- Streamlit UI -----------
def main():
    st.title("📂 Candidate–Job Matching (Multiple Resumes)")

    st.sidebar.header("Upload Data")
    job_file = st.sidebar.file_uploader("Upload Job Description (CSV/TXT/PDF)", type=["csv", "txt", "pdf"])
    cand_files = st.sidebar.file_uploader("Upload Candidate Resumes (CSV/TXT/PDF)", type=["csv", "txt", "pdf"], accept_multiple_files=True)

    if job_file and cand_files:
        jobs = load_job(job_file)
        candidates = load_candidates(cand_files)

        if not jobs.empty and not candidates.empty:
            if st.button("🔍 Run Matching"):
                results = match_candidates(jobs, candidates)
                st.subheader("Best Matches")
                st.dataframe(results)

                # Option to download results
                csv = results.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Download Results as CSV", csv, "matches.csv", "text/csv")

    else:
        st.info("Upload 1 job description file + multiple resume files to proceed.")

if __name__ == "__main__":
    main()