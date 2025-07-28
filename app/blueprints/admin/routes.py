# app/blueprints/admin/routes.py
# Admin routes for administrative functionality.

from flask import render_template, current_app, send_from_directory
from . import admin_bp
from app.utils.decorators import login_required, role_required

@admin_bp.route('/dashboard')
@login_required
@role_required('Administrator')
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/overview')
@login_required
@role_required('Administrator')
def overview():
    """Serves the overview page with all workers status for administrators."""
    return render_template('admin/overview.html')

@admin_bp.route('/phones')
@login_required
@role_required('Administrator')
def phones():
    return render_template('admin/phones.html')

@admin_bp.route('/sims')
@login_required
@role_required('Administrator')
def sims():
    return render_template('admin/sims.html')

@admin_bp.route('/phone-numbers')
@login_required
@role_required('Administrator')
def phone_numbers():
    """Serves the page for managing phone numbers."""
    return render_template('admin/phone_numbers.html')

@admin_bp.route('/workers')
@login_required
@role_required('Administrator')
def workers():
    """Serves the page for managing workers."""
    return render_template('admin/workers.html')

@admin_bp.route('/users')
@login_required
@role_required('Administrator')
def users():
    """Serves the page for managing users."""
    return render_template('admin/users.html')

@admin_bp.route('/roles')
@login_required
@role_required('Administrator')
def roles():
    """Serves the page for managing roles."""
    return render_template('admin/roles.html')

@admin_bp.route('/provision')
@login_required
@role_required('Administrator')
def provision_wizard():
    """Serves the multi-step phone provisioning wizard page."""
    return render_template('admin/provision.html')

@admin_bp.route('/import')
@login_required
@role_required('Administrator')
def import_csv():
    """Serves the CSV data import page."""
    return render_template('admin/import.html')

@admin_bp.route('/requests')
@login_required
@role_required('Administrator')
def phone_requests():
    """Serves the page for admins to manage phone requests."""
    return render_template('admin/requests.html')

# Test pages
@admin_bp.route('/test-api')
@login_required
@role_required('Administrator')
def test_api():
    """Serves a test page for API debugging."""
    return send_from_directory('.', 'test_api.html')

@admin_bp.route('/csv-import-test')
@login_required
@role_required('Administrator')
def csv_import_test():
    """Serves a simplified CSV import test page."""
    return send_from_directory('.', 'csv_import_test.html')
