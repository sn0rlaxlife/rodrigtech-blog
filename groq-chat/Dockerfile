FROM cgr.dev/chainguard/python:latest

# Install dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev \
    musl-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the application code
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create a user and group to run the app
RUN addgroup -S app && adduser -S app -G app

# Change ownership of the application directory
RUN chown -R app:app /app

# Switch to the new user
USER app

# Expose the port the app runs on
EXPOSE 8000

# Define the entry point for the application
CMD ["chainlit","run","app.py","-w"]