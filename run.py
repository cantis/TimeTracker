from flask import render_template

from app.app import create_app

app = create_app()


@app.errorhandler(Exception)
def handle_exception(error: Exception) -> str:
    """Handle exceptions globally."""
    return render_template('error.html', error=error)


if __name__ == '__main__':
    app.run(debug=True)
