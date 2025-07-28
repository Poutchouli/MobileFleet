# app/blueprints/admin/__init__.py
# Admin blueprint for administrative functionality.

from flask import Blueprint

admin_bp = Blueprint('admin', __name__, template_folder='templates')

from . import routes
