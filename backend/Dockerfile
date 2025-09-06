FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Elastic Beanstalk expects this)
EXPOSE 8000

# Run the FastAPI application (production mode)
CMD ["sh", "-c", "uvicorn application:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
