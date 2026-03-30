FROM python:3.12-slim

# Security: run as non-root
RUN groupadd -r vulnreport && useradd -r -g vulnreport vulnreport

WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Security: don't run as root
USER vulnreport

EXPOSE 8000

CMD ["gunicorn", "vulnreport.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
