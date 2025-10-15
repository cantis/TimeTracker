# Render.com Deployment Guide (PostgreSQL)

## Prerequisites
- Render.com account
- GitHub repository with your TimeTracker code

## Deployment Options

### Option 1: Using render.yaml (Recommended)

The `render.yaml` file is pre-configured to create both a web service and PostgreSQL database.

1. **Push your code** to GitHub including the `render.yaml` file
2. **Connect to Render**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically:
     - Create a PostgreSQL database (`timetracker-db`)
     - Create a web service (`timetracker`)
     - Link them with the `DATABASE_URL` environment variable

### Option 2: Manual Configuration

#### Step 1: Create PostgreSQL Database
1. **Create Database**:
   - Go to Render Dashboard
   - Click "New" → "PostgreSQL"
   - **Name**: `timetracker-db`
   - **Database**: `timetracker`
   - **User**: `timetracker`
   - **Plan**: `Starter` (free tier)

#### Step 2: Create Web Service
1. **Create Web Service**:
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
   DATABASE_URL=<connection-string-from-postgres-service>
   DAY_START_TIME=08:30
   DAY_END_TIME=17:00
   DEFAULT_ADMIN_USERNAME=admin
   DEFAULT_ADMIN_EMAIL=admin@yourdomain.com
   DEFAULT_ADMIN_PASSWORD=<secure-password>
   ```

## Database Configuration

### Local Development
Update your `.env` file for local PostgreSQL:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/timetracker_db
```

Or use SQLite for local development:
```env
DATABASE_URL=sqlite:///instance/timetrack.db
```

### Environment Variables Priority
The application checks for database configuration in this order:
1. `DATABASE_URL` (Render.com standard, recommended)
2. `SQLALCHEMY_DATABASE_URI` (legacy support)
3. SQLite fallback (development only)

## Important Notes

### Database Persistence
✅ **PostgreSQL**: Persistent storage across deployments
- Data is preserved during app restarts and deployments
- Automatic backups available on paid plans
- Better performance for production workloads

### Environment Variables
- `SECRET_KEY`: Use Render's "Generate Value" feature for security
- `DATABASE_URL`: Automatically provided when linking PostgreSQL service
- `DEFAULT_ADMIN_PASSWORD`: Use Render's "Generate Value" or set a strong password

### First Run
- Database tables are created automatically on first run
- Default admin user is created based on environment variables
- Check logs to confirm successful initialization

### Health Checks
The app responds to health checks at the root path `/`

### Logs
View application logs in the Render dashboard under your service's "Logs" tab

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
