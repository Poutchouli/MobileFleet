# app/blueprints/manager/routes.py
# Manager routes for manager functionality.

from flask import render_template
from . import manager_bp
from app.utils.decorators import login_required, role_required

@manager_bp.route('/dashboard')
@login_required
@role_required('Manager')
def dashboard():
    """Serves the main dashboard for Managers."""
    return render_template('manager/dashboard.html')

@manager_bp.route('/tickets')
@login_required
@role_required('Manager')
def tickets():
    """Serves the page for a manager to view their submitted tickets."""
    return render_template('manager/tickets.html')

@manager_bp.route('/ticket/<int:ticket_id>')
@login_required
@role_required('Manager')
def ticket_detail(ticket_id):
    """Serves the detailed ticket view page for a manager."""
    return render_template('manager/ticket_detail.html', ticket_id=ticket_id)

@manager_bp.route('/create_ticket')
@login_required
@role_required('Manager')
def create_ticket():
    """Serves the create ticket page for a manager."""
    return render_template('manager/create_ticket.html')
