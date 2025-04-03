"""Test script to verify if database paths are writable."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_db_path() -> None:
    """Test if database paths are writable."""
    db_uri = os.environ.get('SQLALCHEMY_DATABASE_URI')
    if not db_uri:
        print("ERROR: SQLALCHEMY_DATABASE_URI environment variable is not set")
        return
    
    print(f"Testing database URI: {db_uri}")
    
    if not db_uri.startswith('sqlite:///'):
        print("This is not a SQLite database URI, skipping path check")
        return
    
    # Extract path from URI
    db_path = db_uri.replace('sqlite:///', '')
    if not db_path.startswith('/'):
        # Relative path, make it absolute from current directory
        db_path = os.path.join(os.getcwd(), db_path)
    
    db_file = Path(db_path)
    parent_dir = db_file.parent
    
    print(f"Database path: {db_file}")
    print(f"Parent directory: {parent_dir}")
    
    # Test if parent directory exists
    if not parent_dir.exists():
        print(f"Creating directory: {parent_dir}")
        try:
            parent_dir.mkdir(parents=True, exist_ok=True)
            print(f"Successfully created directory {parent_dir}")
        except Exception as e:
            print(f"ERROR: Failed to create directory {parent_dir}: {e}")
            return
    
    # Test if parent directory is writable
    if not os.access(str(parent_dir), os.W_OK):
        print(f"ERROR: Directory {parent_dir} is not writable")
        return
    
    # Test if we can create a file
    test_file = parent_dir / ".db_write_test"
    try:
        with open(test_file, 'w') as f:
            f.write("test")
        print(f"Successfully wrote to test file {test_file}")
        test_file.unlink()
        print("Test file removed")
    except Exception as e:
        print(f"ERROR: Failed to write to test file: {e}")
        return
    
    print("Database path check PASSED: The location is writable")

if __name__ == "__main__":
    test_db_path()