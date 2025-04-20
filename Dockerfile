FROM node:19 AS frontend-builder

WORKDIR /app/frontend
COPY evalui/package*.json ./
RUN npm install
COPY evalui/ ./
RUN npm run build

FROM python:3.9-slim

WORKDIR /app

# Install system dependencies including PostgreSQL client libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY *.py ./
COPY *.sh ./

# Copy frontend build from the frontend-builder stage
COPY --from=frontend-builder /app/frontend/build ./evalui/build

# Create necessary directories
RUN mkdir -p logs feedback_data

# Make start script executable
RUN chmod +x start_app.sh

# Set environment variables
ENV FLASK_ENV=production
ENV PORT=5001

# Expose ports
EXPOSE 5001
EXPOSE 3000

# Start the application in production mode
CMD ["./start_app.sh", "prod"]
