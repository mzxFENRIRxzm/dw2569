FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir django clickhouse-connect pillow

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py seed_data && python manage.py setup_clickhouse && python manage.py seed_movies && python manage.py sync_clickhouse && python manage.py runserver 0.0.0.0:8000"]
