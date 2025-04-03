"""Main entry point for the TimeTracker application."""

import os
import sys
from pathlib import Path

from flask import render_template

from app.app import create_app

# Ensure critical directories exist with proper permissions
data_dir = Path('/app/data')
instance_dir = Path('/app/instance')

def ensure_directory(path: Path) -> None:
    """Ensure directory exists and is writable."""
    try:
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {path}")
        
        # Test write access
        test_file = path / '.write_test'
        with open(test_file, 'w') as f:
            f.write('test')
        test_file.unlink()
    except Exception as e:
        print(f"ERROR: Cannot write to {path}: {e}", file=sys.stderr)
        sys.exit(1)

# Ensure directories exist
if os.environ.get('SQLALCHEMY_DATABASE_URI', '').startswith('sqlite:///data/'):
    ensure_directory(data_dir)
ensure_directory(instance_dir)

app = create_app()

@app.errorhandler(Exception)
def handle_exception(error: Exception) -> str:
    """Handle exceptions globally."""
    return render_template('error.html', error=error)

if __name__ == '__main__':
    app.run(debug=True)
