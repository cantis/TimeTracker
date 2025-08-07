# Environment Variables Documentation

This document describes the environment variables used by the TimeTracker application.

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

## Security Considerations

- **Change default credentials**: Always change the default admin credentials in production environments
- **Use strong passwords**: Ensure the default admin password meets your security requirements
- **Environment protection**: Keep your `.env` file secure and never commit it to version control

## Example .env Configuration

```env
# Default Admin User Settings
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_EMAIL=admin@timetracker.local
DEFAULT_ADMIN_PASSWORD=admin123
```

## Usage

These environment variables are only used when:
1. The application starts
2. No users exist in the database
3. The `SKIP_DEFAULT_ADMIN` environment variable is not set to `True`

Once a user is created, these variables have no effect unless the database is reset.
