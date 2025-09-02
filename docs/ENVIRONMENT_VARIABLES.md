# Environment Variables Documentation

This document describes the environment variables used by the TimeTracker application.

## Database Configuration

### `DATABASE_URL` (Recommended)
- **Description**: Primary database connection string (Render.com standard)
- **Format**: `protocol://username:password@host:port/database`
- **Examples**:
  - PostgreSQL: `DATABASE_URL=postgresql://user:pass@localhost:5432/timetracker_db`
  - SQLite: `DATABASE_URL=sqlite:///instance/timetrack.db`

### `SQLALCHEMY_DATABASE_URI` (Legacy)
- **Description**: Alternative database connection string for backward compatibility
- **Note**: `DATABASE_URL` takes precedence if both are set
- **Example**: `SQLALCHEMY_DATABASE_URI=sqlite:///instance/timetrack.db`

## Default Admin User Settings

When the application starts and no users exist in the database, it will automatically create a default admin user. The credentials for this user can be configured using the following environment variables:

### `DEFAULT_ADMIN_USERNAME`
- **Description**: Username for the default admin user
- **Example**: `DEFAULT_ADMIN_USERNAME=myadmin`

### `DEFAULT_ADMIN_EMAIL`
- **Description**: Email address for the default admin user
- **Example**: `DEFAULT_ADMIN_EMAIL=admin@mycompany.com`

### `DEFAULT_ADMIN_PASSWORD`
- **Description**: Password for the default admin user
- **Example**: `DEFAULT_ADMIN_PASSWORD=mySecurePassword123!`

## Application Settings

### `SECRET_KEY`
- **Description**: Flask secret key for session management and security
- **Example**: `SECRET_KEY=your-secret-key-here`
- **Note**: Use a strong, random value in production

### `DAY_START_TIME`
- **Description**: Default start time for work day (24-hour format)
- **Example**: `DAY_START_TIME=08:30`

### `DAY_END_TIME`
- **Description**: Default end time for work day (24-hour format)
- **Example**: `DAY_END_TIME=17:00`

## Security Considerations

- **Change default credentials**: Always change the default admin credentials in production environments
- **Use strong passwords**: Ensure the default admin password meets your security requirements
- **Environment protection**: Keep your `.env` file secure and never commit it to version control
- **Database security**: Use strong database passwords and restrict access

## Example .env Configuration

### For Local Development (SQLite)
```env
# Database
DATABASE_URL=sqlite:///instance/timetrack.db

# Security
SECRET_KEY=dev-key-only-for-development

# Application Settings
DAY_START_TIME=08:30
DAY_END_TIME=17:00

# Default Admin User
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_EMAIL=admin@timetracker.local
DEFAULT_ADMIN_PASSWORD=admin123
```

### For Production (PostgreSQL)
```env
# Database
DATABASE_URL=postgresql://username:password@host:port/database

# Security
SECRET_KEY=<generate-strong-random-key>

# Application Settings
DAY_START_TIME=08:30
DAY_END_TIME=17:00

# Default Admin User
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_EMAIL=admin@yourcompany.com
DEFAULT_ADMIN_PASSWORD=<generate-secure-password>
```

## Usage

These environment variables are used when:
1. The application starts
2. Database connection is established
3. No users exist in the database (for admin user creation)
4. The `SKIP_DEFAULT_ADMIN` environment variable is not set to `True`

Once a user is created, the admin user variables have no effect unless the database is reset.
