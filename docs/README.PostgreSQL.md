# Local PostgreSQL Setup

## Prerequisites
- PostgreSQL installed locally
- Python environment with psycopg2-binary

## Setup Steps

### 1. Install PostgreSQL
Download and install PostgreSQL from https://www.postgresql.org/download/

### 2. Create Database
```powershell
# Connect to PostgreSQL as superuser
psql -U postgres

# Create database and user
CREATE DATABASE timetracker_db;
CREATE USER timetracker WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE timetracker_db TO timetracker;

# Exit psql
\q
```

### 3. Update Environment Variables
Update your `.env` file:
```env
DATABASE_URL=postgresql://timetracker:your_password@localhost:5432/timetracker_db
```

### 4. Run Application
```powershell
# Install dependencies
uv sync

# Run the application
uv run python run.py
```

## Testing Database Connection

```python
# Test script to verify PostgreSQL connection
import os
from sqlalchemy import create_engine, text

database_url = os.getenv('DATABASE_URL')
if database_url:
    engine = create_engine(database_url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        print("PostgreSQL version:", result.fetchone()[0])
        print("✅ Database connection successful!")
else:
    print("❌ DATABASE_URL not found in environment variables")
```

## Common Issues

### Connection Refused
- Ensure PostgreSQL service is running
- Check host and port in DATABASE_URL
- Verify firewall settings

### Authentication Failed
- Check username and password in DATABASE_URL
- Verify user permissions in PostgreSQL

### Database Not Found
- Ensure database exists: `CREATE DATABASE timetracker_db;`
- Check database name in DATABASE_URL

## Docker Development

For Docker-based local development with PostgreSQL:

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: timetracker_db
      POSTGRES_USER: timetracker
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      DATABASE_URL: postgresql://timetracker:password@db:5432/timetracker_db
    depends_on:
      - db

volumes:
  postgres_data:
```

Run with: `docker-compose -f docker-compose.dev.yml up`
