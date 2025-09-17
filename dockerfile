# Use slim Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system deps (needed for some Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source code
COPY . .

# Streamlit needs this for headless mode on Render
ENV STREAMLIT_SERVER_HEADLESS=true

# Expose the port Streamlit will run on
EXPOSE 8501

# Default command to run the app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]