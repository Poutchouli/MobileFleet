# app/blueprints/manager/__init__.py
# Manager blueprint for manager functionality.

from flask import Blueprint

manager_bp = Blueprint('manager', __name__, template_folder='templates')

from . import routes
