# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies (needed for psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    # libpq-dev \
    # netcat-openbsd \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
# Copy only requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entrypoint script
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy project code
COPY . .

# Expose port 8000 to the Docker host, so we can access it
# (though Nginx will be the primary access point)
EXPOSE 8000

# Run entrypoint script
ENTRYPOINT ["/entrypoint.sh"]

# Default command can be overridden (e.g., in docker-compose)
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] is now handled by entrypoint 

# Final stage for production
FROM base AS production

# Copy application code
COPY . /app/

# Set working directory
WORKDIR /app

# Expose the port Gunicorn will run on
EXPOSE 8000

# Collect static files (if you decide to serve them via Nginx)
# RUN python manage.py collectstatic --noinput

# Set the entrypoint script as executable
# RUN chmod +x /app/entrypoint.sh
# ENTRYPOINT ["/app/entrypoint.sh"]

# Start Gunicorn
# Adjust the number of workers (-w) based on your VPS resources (e.g., 2 * number_of_cores + 1)
# Bind to 0.0.0.0 to accept connections from Nginx container
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "core.wsgi:application"] 