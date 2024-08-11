# Stage 1: Build the application
FROM python:3.10-slim AS build

# Set the working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the application code
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Run the application on a minimal image
FROM cgr.dev/chainguard/python:latest

# Set the working directory
WORKDIR /app

# Copy only the necessary files from the build stage
COPY --from=build /app /app

# Optionally, create a non-root user if needed
# Uncomment the following lines if Chainguard image requires manual user creation
RUN addgroup -S app && adduser -S app -G app
RUN chown -R app:app /app
USER app

# Expose the port the app runs on
EXPOSE 8000

# Define the entry point for the application
CMD ["chainlit", "run", "app.py", "-w"]