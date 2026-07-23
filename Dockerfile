# ==============================
# Base Image
# ==============================
FROM python:3.12-slim

# ==============================
# Environment Variables
# ==============================
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ==============================
# Working Directory
# ==============================
WORKDIR /app

# ==============================
# Install Dependencies
# ==============================
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ==============================
# Copy Project Files
# ==============================
COPY . .

# ==============================
# Expose FastAPI Port
# ==============================
EXPOSE 8080

# ==============================
# Start FastAPI
# ==============================
CMD ["python", "-m", "backend.main"]