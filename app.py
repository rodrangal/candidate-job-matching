import streamlit as st
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from io import StringIO
import os
import PyPDF2
import docx

# --------------------------
# Helpers
# --------------------------
def read_txt(file):
    return file.read().decode("utf-8")

def read_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def read_docx(file):
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

def parse_uploaded_file(file):
    if file.name.endswith(".txt"):
        return read_txt(file)
    elif file.name.endswith(".pdf"):
        return read_pdf(file)
    elif file.name.endswith(".docx"):
        return read_docx(file)
    else:
        return None

# --------------------------
# Load model
# --------------------------
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_model()

# --------------------------
# Streamlit UI
# --------------------------
st.set_page_config(page_title="Candidate-Job Matching Demo", layout="wide")
st.title("🤝 Candidate ↔ Job Matching System (MVP Demo)")

# Upload job description
st.subheader("1. Upload Job Description")
jd_file = st.file_uploader("Upload a job description (.txt, .pdf, .docx)", type=["txt", "pdf", "docx"])

# Upload candidate resumes
st.subheader("2. Upload Candidate Resumes")
resume_files = st.file_uploader("Upload multiple resumes", type=["txt", "pdf", "docx"], accept_multiple_files=True)

if jd_file and resume_files:
    jd_text = parse_uploaded_file(jd_file)

    # Parse resumes
    resumes = {}
    for f in resume_files:
        text = parse_uploaded_file(f)
        if text:
            resumes[f.name] = text

    if st.button("🔍 Find Top Matches"):
        # Encode job + resumes
        jd_embedding = model.encode([jd_text], normalize_embeddings=True)
        resume_embeddings = model.encode(list(resumes.values()), normalize_embeddings=True)

        # Build FAISS index
        dim = resume_embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(resume_embeddings)

        # Search
        k = min(5, len(resumes))
        D, I = index.search(jd_embedding, k)

        st.subheader("📊 Top Candidate Matches")
        for rank, idx in enumerate(I[0]):
            name = list(resumes.keys())[idx]
            score = float(D[0][rank])
            st.markdown(f"**{rank+1}. {name}** — score: `{score:.4f}`")
            
            # Highlight overlapping keywords
            jd_words = set(jd_text.lower().split())
            resume_words = set(resumes[name].lower().split())
            overlap = jd_words.intersection(resume_words)
            if overlap:
                st.write("🔑 Matched keywords:", ", ".join(list(overlap)[:10]))

        st.success("Done! You can try uploading different JDs or resumes.")