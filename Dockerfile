# Dockerfile
# This file defines the environment for the Python/Flask application container.

# --- Base Image ---
# Start with an official Python runtime as a parent image.
# Using a specific version ensures consistency.
FROM python:3.11-slim

# --- Environment Variables ---
# Set environment variables to prevent Python from writing pyc files to disc
# and to keep the output from being buffered.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# --- Working Directory ---
# Set the working directory in the container. All subsequent commands
# will be run from this directory.
WORKDIR /app

# --- Install Dependencies ---
# First, install system dependencies including postgresql-client for database connectivity checks
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Copy over the requirements file.
COPY requirements.txt .

# Install the Python dependencies specified in requirements.txt.
# --no-cache-dir: Disables the cache, which reduces the image size.
# -r requirements.txt: Specifies the file to install from.
RUN pip install --no-cache-dir -r requirements.txt

# --- Copy Application Code ---
# Copy the rest of the application's code into the container's working directory.
# This includes app.py, init_database.py, templates/, static/, etc.
COPY . .

# --- Expose Port ---
# Make port 5000 available to the host. This is the port Flask will run on.
EXPOSE 5000

# --- Command to Run the Application ---
# Define the command to run when the container starts.
# We use gunicorn as a production-ready WSGI server.
# The 'app:app' refers to the Flask application instance named 'app'
# inside the 'app.py' file.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
