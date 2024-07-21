# ---- Base Python ----
FROM python:3.10-slim AS base
WORKDIR /app

# Install system dependencies for mysqlclient
RUN apt-get update && apt-get install -y \
default-libmysqlclient-dev \
gcc \
pkg-config \
&& apt-get clean && rm -rf /var/lib/apt/lists/*

# Now install your Python packages
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install gunicorn

# Copy the entrypoint script and give it the necessary permissions
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Copy the rest of your application's code
COPY . .
RUN chmod +x /app/entrypoint.sh

# Set the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]

# ---- Release with Gunicorn ----
FROM base AS release
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]