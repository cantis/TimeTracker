from flask import Blueprint, render_template

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/settings')
def settings():
    """Render the settings page."""
    return render_template('settings.html')
