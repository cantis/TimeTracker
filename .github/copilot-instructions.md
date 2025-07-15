# TimeTracker AI Coding Instructions

## Project Overview
Flask-based time tracking application with Bootstrap frontend, SQLite database, and Docker containerization.
Uses Blueprint architecture with three main modules: `home` (entry management), `reports` (analytics), and `admin` (settings).

## Architecture Patterns
- **Flask application factory** in `app/app.py` with Blueprint registration
- **Time storage format**: Mixed handling of both integer minutes-past-midnight and "HH:MM" strings (see `parse_time_to_minutes()` in reports.py)
- **Database models**: SQLAlchemy with explicit `__init__` methods for type hinting (see `app/models.py`)
- **Template structure**: Base template with Bootstrap 5, header/footer includes, flash message handling

## Development Workflow
- **Package management**: `uv` for dependencies, PowerShell for commands
- **Testing**: pytest with arrange/act/assert pattern, `$env:PYTHONPATH='S:\TimeTracker'; pytest` to run
- **Database**: SQLite with Docker volume mounting to `/app/data`
- **CSS/JS**: Inline in templates, sortable tables with time format conversion

## Time Handling Specifics
```python
# Always use parse_time_to_minutes() for mixed format support
def parse_time_to_minutes(value):
    # Handles both 480 (int) and "8:00" (str) formats
```

## Testing Conventions
- Use `with app.app_context():` for database operations in tests
- Import models locally in test functions to avoid circular imports
- Direct route paths (`"/reports/weekly"`) instead of `url_for()` to avoid Flask context issues

## Code Style
- PEP 8 naming, type annotations for functions/variables
- Sorted imports per ruff style
- Minimal docstrings for files, functions, classes
- No logging unless specifically requested
- `|` syntax for optional model fields