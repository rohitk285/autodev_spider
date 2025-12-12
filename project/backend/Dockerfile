FROM python:3.11

WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
ENV DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/tododb

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
