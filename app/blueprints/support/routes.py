# app/blueprints/support/routes.py
# Support routes for support functionality.

from flask import render_template
from . import support_bp
from app.utils.decorators import login_required, role_required

@support_bp.route('/dashboard')
@login_required
@role_required('Support')
def dashboard():
    """Serves the main helpdesk dashboard for Support staff."""
    return render_template('support/dashboard.html')

# Integration Manager routes (temporary location until separate blueprint)
@support_bp.route('/integration/dashboard')
@login_required
@role_required('Integration Manager')
def integration_dashboard():
    """Serves the dashboard for Integration Managers to see their requests."""
    return render_template('integration/dashboard.html')

@support_bp.route('/integration/new_request')
@login_required
@role_required('Integration Manager')
def integration_new_request():
    """Serves the form for an Integration Manager to request a new phone."""
    return render_template('integration/new_request.html')
