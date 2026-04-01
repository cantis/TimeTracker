"""Admin routes for administrative functions."""

from typing import Any, Callable

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.service.user_service import (
    CreateUserError,
    DeleteUserError,
    UpdateUserError,
    create_user,
    get_all_users,
    get_user_by_id,
    update_user,
)
from app.service.user_service import (
    delete_user as delete_user_service,
)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to require admin privileges."""

    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin privileges required.', 'error')
            return redirect(url_for('home.index'))
        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function


@admin_bp.route('/settings')
@login_required
@admin_required
def settings():
    """Render the settings page."""
    return render_template('settings.html')


@admin_bp.route('/users')
@login_required
@admin_required
def user_list():
    """Display list of all users."""
    users = get_all_users()
    return render_template('admin/user_list.html', users=users)


@admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    """Add a new user."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        is_admin = request.form.get('is_admin') == 'on'
        is_active = request.form.get('is_active', 'on') == 'on'

        try:
            user = create_user(
                username=username,
                email=email,
                password=password,
                is_admin=is_admin,
                is_active=is_active,
            )
            flash(f'User "{user.username}" created successfully.', 'success')
            return redirect(url_for('admin.user_list'))
        except CreateUserError as e:
            flash(f'Error creating user: {e.message}', 'error')

    return render_template('admin/add_user.html')


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id: int):
    """Edit an existing user."""
    user = get_user_by_id(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin.user_list'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        is_admin = request.form.get('is_admin') == 'on'
        is_active = request.form.get('is_active') == 'on'

        # Don't allow users to remove their own admin status
        if user.id == current_user.id and not is_admin:
            flash('You cannot remove your own admin privileges.', 'error')
            return render_template('admin/edit_user.html', user=user)

        try:
            updated_user = update_user(
                user_id=user_id,
                username=username,
                email=email,
                password=password if password else None,
                is_admin=is_admin,
                is_active=is_active,
            )
            flash(f'User "{updated_user.username}" updated successfully.', 'success')
            return redirect(url_for('admin.user_list'))
        except UpdateUserError as e:
            flash(f'Error updating user: {e.message}', 'error')

    return render_template('admin/edit_user.html', user=user)


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id: int):
    """Delete a user."""
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'})

    # Don't allow users to delete themselves
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': 'You cannot delete your own account'})

    try:
        delete_user_service(user_id)
        return jsonify({'success': True, 'message': f'User "{user.username}" deleted successfully'})
    except DeleteUserError as e:
        return jsonify({'success': False, 'message': e.message})
