# 🤝 Candidate ↔ Job Matching Demo

A lightweight **candidate-job matching system** for small recruitment agencies.  
It parses resumes & job descriptions, creates embeddings with [SentenceTransformers](https://www.sbert.net/), and ranks candidates using semantic similarity with [FAISS](https://faiss.ai/).  
A **Streamlit UI** makes it easy for recruiters to upload documents and view top matches instantly.  

---

## 🚀 Features
- Upload resumes (TXT, PDF, DOCX).  
- Upload a job description (TXT, PDF, DOCX).  
- Get top candidate matches ranked by similarity.  
- View similarity scores + overlapping keywords.  
- Run locally, with Docker, or deploy to Render.  

---

## 📂 Project Structure
candidate-job-matching/
│
├── data/ # sample resumes & job descriptions
│ ├── resumes/
│ └── jobs/
│
├── app.py # Streamlit UI
├── requirements.txt # dependencies
├── Dockerfile # for container deployment
└── README.md # this file