# Render.com Deployment Guide

## Prerequisites
- Render.com account
- GitHub repository with your TimeTracker code

## Deployment Options

### Option 1: Using render.yaml (Recommended)

1. **Push your code** to GitHub including the `render.yaml` file
2. **Connect to Render**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically read `render.yaml` and configure the service

### Option 2: Manual Configuration

1. **Create New Web Service**:
   - Go to Render Dashboard
   - Click "New" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**:
   - **Name**: `timetracker`
   - **Runtime**: `Docker`
   - **Build Command**: (leave empty)
   - **Start Command**: (leave empty - uses Dockerfile CMD)

3. **Environment Variables**:
   ```
   SECRET_KEY=<generate-random-string>
   SQLALCHEMY_DATABASE_URI=sqlite:///app/instance/timetrack.db
   DAY_START_TIME=08:30
   DAY_END_TIME=17:00
   DEFAULT_ADMIN_USERNAME=admin
   DEFAULT_ADMIN_EMAIL=admin@yourdomain.com
   DEFAULT_ADMIN_PASSWORD=<secure-password>
   ```

## Important Notes

### Database Persistence
⚠️ **SQLite Limitation**: Render's free tier has ephemeral storage - your database will reset on each deployment.

**For Production**: Consider upgrading to:
- **Render PostgreSQL** (recommended)
- **External database service**

### Environment Variables
- `SECRET_KEY`: Use Render's "Generate Value" feature for security
- `DEFAULT_ADMIN_PASSWORD`: Use Render's "Generate Value" or set a strong password
- Database will be created automatically on first run

### Health Checks
The app responds to health checks at the root path `/`

### Logs
View application logs in the Render dashboard under your service's "Logs" tab

## PostgreSQL Migration (Recommended for Production)

1. **Create PostgreSQL Database**:
   - In Render Dashboard: "New" → "PostgreSQL"
   - Note the connection details

2. **Update Environment Variables**:
   ```
   SQLALCHEMY_DATABASE_URI=postgresql://user:pass@host:port/dbname
   ```

3. **Add PostgreSQL Dependencies**:
   ```bash
   # Add to requirements.txt
   psycopg2-binary>=2.9.0
   ```

## Deployment Commands

```bash
# Build and test locally first
docker build -t timetracker .
docker run -p 5000:5000 -e PORT=5000 timetracker

# Push to GitHub to trigger Render deployment
git add .
git commit -m "Deploy to Render"
git push origin main
```

## Troubleshooting

### Common Issues:
1. **Port binding errors**: Ensure Dockerfile uses `${PORT:-5000}`
2. **Database not found**: Check SQLALCHEMY_DATABASE_URI path
3. **Permission errors**: Verify directory permissions in Dockerfile
4. **Environment variables**: Check Render dashboard configuration

### Debug Steps:
1. Check Render service logs
2. Verify environment variables in Render dashboard
3. Test database connectivity
4. Confirm port configuration
