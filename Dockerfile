
FROM python:3.11-slim

WORKDIR /app

# Copy requirements terlebih dahulu
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh source code aplikasi
COPY . .

# Port aplikasi FastAPI
EXPOSE 8000

# Jalankan aplikasi menggunakan Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
