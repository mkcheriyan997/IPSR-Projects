FROM python:3.11-slim

# Install system dependencies (openssh client for ssh connection, sshpass for password auth)
RUN apt-get update && apt-get install -y --no-install-recommends \
    sshpass \
    openssh-client \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install ansible-core for running playbooks
RUN pip install --no-cache-dir ansible-core

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure PYTHONPATH is set to current directory so app module imports work
ENV PYTHONPATH=/app

# Expose app port
EXPOSE 5000

# Run the flask application
CMD ["python", "-m", "app.app"]
