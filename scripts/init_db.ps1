<#
.SYNOPSIS
    Creates the TimeTracker PostgreSQL database and user if they do not exist.

.DESCRIPTION
    Connects to PostgreSQL as the superuser 'postgres' and:
    - Creates the database if it does not exist
    - Creates the user if it does not exist
    - Grants privileges to the user on the database

.NOTES
    Run this script in PowerShell. PostgreSQL must be installed and on your PATH.
#>

# --- Configuration ---
$dbName = 'timetracker_db'
$dbUser = 'timetracker_user'
$dbPassword = 'your_password'

# --- Prompt for postgres password ---
$pgPassword = Read-Host -AsSecureString "Enter PostgreSQL password for user 'postgres'"
$plainPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($pgPassword)
)

# --- Step 1: Create the database if it doesn’t exist ---
$dbExists = & psql -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$dbName'" 2>$null
if (-not $dbExists) {
    Write-Host "Creating database '$dbName'..."
    $env:PGPASSWORD = $plainPassword
    & psql -U postgres -d postgres -c "CREATE DATABASE $dbName;"
} else {
    Write-Host "Database '$dbName' already exists."
}

# --- Step 2: Create the user if it doesn’t exist ---
$userExists = & psql -U postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$dbUser'" 2>$null
if (-not $userExists) {
    Write-Host "Creating user '$dbUser'..."
    & psql -U postgres -d postgres -c "CREATE USER $dbUser WITH ENCRYPTED PASSWORD '$dbPassword';"
} else {
    Write-Host "User '$dbUser' already exists."
}

# --- Step 3: Grant privileges ---
Write-Host "Granting privileges on $dbName to $dbUser..."
& psql -U postgres -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE $dbName TO $dbUser;"

# --- Cleanup ---
$env:PGPASSWORD = $null
Write-Host "Setup complete."
