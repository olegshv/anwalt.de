# Use slim Python base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy sync script into container
COPY remote_env_sync.py .

# Install required Python packages
RUN pip install requests

# Run the sync script in an infinite loop with a 10-second interval
CMD ["sh", "-c", "while true; do python remote_env_sync.py; sleep 10; done"]
