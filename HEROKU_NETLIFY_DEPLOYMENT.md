# Deploying to Heroku and Netlify

This guide provides step-by-step instructions for deploying the Agilent Support Assistant application with:
- Backend on Heroku
- Frontend on Netlify

## Prerequisites

- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed
- [Netlify CLI](https://docs.netlify.com/cli/get-started/) installed (optional, you can also deploy via the Netlify website)
- Git for version control
- GitHub account (for connecting to Netlify)

## 1. Preparing the Backend for Heroku

### 1.1 Create a Heroku Account and Application

1. Sign up for a Heroku account at [heroku.com](https://heroku.com) if you don't have one
2. Create a new Heroku application:
   ```bash
   heroku create azure-ragilent-backend
   ```
   Note: Replace `agilent-support-assistant-backend` with your preferred app name

### 1.2 Configure Environment Variables on Heroku

Set up all the required environment variables from your `.env` file:

```bash
heroku config:set OPENAI_ENDPOINT=https://your-openai-endpoint.openai.azure.com/
heroku config:set OPENAI_KEY=your-openai-key
heroku config:set EMBEDDING_DEPLOYMENT=your-embedding-deployment
heroku config:set CHAT_DEPLOYMENT=your-chat-deployment
heroku config:set SEARCH_ENDPOINT=your-search-endpoint
heroku config:set SEARCH_INDEX=your-search-index
heroku config:set SEARCH_KEY=your-search-key
heroku config:set VECTOR_FIELD=your-vector-field
heroku config:set FLASK_ENV=production
heroku config:set PORT=5001
heroku config:set NETLIFY_DOMAIN=your-netlify-app.netlify.app
```

### 1.3 Configure CORS for the Backend

The backend has been updated to automatically configure CORS based on the environment:

- In development mode, it allows requests from all origins
- In production mode, it only allows requests from the Netlify domain specified in the `NETLIFY_DOMAIN` environment variable

This is already implemented in the `api.py` file:

```python
# Configure CORS based on environment
if os.getenv('FLASK_ENV') == 'production':
    # For production, only allow requests from the Netlify domain
    netlify_domain = os.getenv('NETLIFY_DOMAIN', 'your-netlify-app.netlify.app')
    logger.info(f"Configuring CORS for production, allowing origin: {netlify_domain}")
    CORS(app, resources={r"/*": {"origins": f"https://{netlify_domain}"}})
else:
    # For development, allow all origins
    logger.info("Configuring CORS for development, allowing all origins")
    CORS(app)
```

Make sure to set the `NETLIFY_DOMAIN` environment variable in Heroku to match your Netlify app's domain.

## 2. Deploying the Backend to Heroku

### 2.1 Push to Heroku

From your project root directory:

```bash
git init
git add .
git commit -m "Prepare for Heroku deployment"
git push heroku main
```

### 2.2 Verify the Backend Deployment

Check if your backend is running:

```bash
heroku open
```

This should open your browser to your Heroku app URL. You should see a response from your API (possibly the health check endpoint).

## 3. Preparing the Frontend for Netlify

### 3.1 Update the netlify.toml File

Edit the `netlify.toml` file to replace `your-heroku-app-name` with your actual Heroku app name:

```toml
[[redirects]]
  from = "/api/*"
  to = "https://agilent-support-assistant-backend.herokuapp.com/api/:splat"
  status = 200
  force = true
```

Update all the redirect rules with your actual Heroku app name.

## 4. Deploying the Frontend to Netlify

### 4.1 Push Your Code to GitHub

If your code isn't already on GitHub:

1. Create a new GitHub repository
2. Push your code to the repository:
   ```bash
   git remote add origin https://github.com/yourusername/your-repo-name.git
   git push -u origin main
   ```

### 4.2 Deploy to Netlify

#### Option 1: Deploy via Netlify Website

1. Go to [app.netlify.com](https://app.netlify.com/)
2. Click "New site from Git"
3. Select GitHub and authorize Netlify
4. Select your repository
5. Netlify will automatically detect the `netlify.toml` file and use its settings
6. Click "Deploy site"

#### Option 2: Deploy via Netlify CLI

```bash
netlify login
netlify init
# Follow the prompts to connect to your GitHub repository
netlify deploy --prod
```

## 5. Testing the Deployment

1. Visit your Netlify site URL
2. Test the application functionality
3. Check the browser console for any API errors

## 6. Troubleshooting

### Common Issues

1. **CORS Errors**: If you see CORS errors in the browser console, ensure your backend is properly configured to accept requests from your Netlify domain.

2. **API Connection Issues**: Verify that the redirects in `netlify.toml` are correctly pointing to your Heroku app.

3. **Environment Variables**: Make sure all required environment variables are set in Heroku.

4. **Build Errors on Netlify**: Check the Netlify build logs for any errors during the build process.

### Logs

To check logs on Heroku:

```bash
heroku logs --tail
```

To check logs on Netlify, go to the Netlify dashboard, select your site, and navigate to the "Deploys" tab.

## 7. Additional Considerations

### Custom Domain

You can configure custom domains for both your Heroku and Netlify deployments:

- [Heroku Custom Domains](https://devcenter.heroku.com/articles/custom-domains)
- [Netlify Custom Domains](https://docs.netlify.com/domains-https/custom-domains/)

### Continuous Deployment

Both Heroku and Netlify support continuous deployment from GitHub:

- Heroku: Connect your GitHub repository in the Heroku dashboard
- Netlify: Already set up if you deployed via the Netlify website

### Database Setup with Heroku Postgres

The application now uses PostgreSQL for the feedback system. To set up the database:

1. Add the Heroku Postgres add-on to your application:
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

2. Verify that the DATABASE_URL environment variable has been set:
   ```bash
   heroku config | grep DATABASE_URL
   ```

3. The application is already configured to use the DATABASE_URL environment variable provided by Heroku.

4. If you need to migrate existing data from SQLite to PostgreSQL, you can use a tool like `pgloader`:
   ```bash
   # Install pgloader
   sudo apt-get install pgloader  # For Ubuntu/Debian
   # or
   brew install pgloader  # For macOS with Homebrew

   # Run the migration (replace with your actual Heroku DATABASE_URL)
   pgloader votes.db postgres://username:password@host:port/database
   ```

5. To connect to your Heroku Postgres database directly:
   ```bash
   heroku pg:psql
   ```
