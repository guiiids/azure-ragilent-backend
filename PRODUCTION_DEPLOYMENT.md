# Production Deployment Guide

This guide provides instructions for deploying the Agilent Support Assistant application in a production environment.

## Prerequisites

- Docker and Docker Compose installed
- Git for cloning the repository
- Basic understanding of Docker and containerization

## Deployment Steps

### 1. Clone the Repositories

```bash
# Clone the backend repository
git clone https://github.com/guiiids/azure-ragilent.git
cd azure-ragilent

# Clone the frontend repository
git clone https://github.com/guiiids/azure-ragilent-frontend.git evalui
```

### 2. Configure Environment Variables

Create a `.env` file based on the provided template:

```bash
cp .env.template .env
```

Edit the `.env` file and fill in all required values:

```
# Azure OpenAI Configuration
OPENAI_ENDPOINT=https://your-openai-endpoint.openai.azure.com/
OPENAI_KEY=your-openai-key
EMBEDDING_DEPLOYMENT=your-embedding-deployment
CHAT_DEPLOYMENT=your-chat-deployment

# Azure Cognitive Search Configuration
SEARCH_ENDPOINT=your-search-endpoint
SEARCH_INDEX=your-search-index
SEARCH_KEY=your-search-key
VECTOR_FIELD=your-vector-field

# Application Settings
FEEDBACK_DIR=feedback_data
FLASK_ENV=production
PORT=5001

# Database Configuration (for PostgreSQL)
DATABASE_URL=postgres://username:password@host:port/database
```

### 3. Build and Start the Application

Use Docker Compose to build and start the application:

```bash
docker-compose up -d
```

This will:
- Build the Docker image
- Start the application in detached mode
- Map ports 5001 (API) and 3000 (Frontend) to your host
- Mount volumes for logs and feedback data

### 4. Verify Deployment

Check if the containers are running:

```bash
docker-compose ps
```

Verify the application is working by accessing:
- Frontend: http://localhost:3000
- API Health Check: http://localhost:5001/health

### 5. View Logs

To view application logs:

```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View specific service logs
docker-compose logs agilent-support-assistant
```

You can also check the logs directory:

```bash
ls -la logs/
```

### 6. Stopping the Application

To stop the application:

```bash
docker-compose down
```

## Production Considerations

### SSL/TLS Configuration

For production deployment, you should configure SSL/TLS. You can:

1. Use a reverse proxy like Nginx or Traefik
2. Configure with Let's Encrypt for free SSL certificates
3. Update the Docker Compose file to include the SSL configuration

### Scaling

For higher load scenarios:

1. Increase the number of Gunicorn workers in `start_app.sh`
2. Consider using a load balancer for multiple instances
3. Implement a Redis cache for session management

### Monitoring

The application includes a `/health` endpoint that can be used with monitoring tools like:

- Prometheus
- Grafana
- AWS CloudWatch
- Azure Monitor

### Database Configuration

The application now uses PostgreSQL for the feedback system:

1. Set up a PostgreSQL database server
2. Configure the DATABASE_URL environment variable in your .env file:
   ```
   DATABASE_URL=postgres://username:password@host:port/database
   ```
3. Ensure the PostgreSQL server is accessible from the Docker container

### Backup Strategy

Regularly backup:

1. The PostgreSQL database (using pg_dump):
   ```bash
   # Example backup command
   pg_dump -h hostname -U username -d database_name -F c -f backup.dump
   ```
2. The feedback data directory
3. Configuration files

## Troubleshooting

### Common Issues

1. **Application not starting**: Check Docker logs and ensure all environment variables are set correctly.
2. **API errors**: Verify Azure OpenAI and Cognitive Search credentials.
3. **Frontend not loading**: Check if the build process completed successfully.

### Getting Help

For additional assistance, please contact the development team or refer to the project documentation.
