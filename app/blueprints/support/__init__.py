# app/blueprints/support/__init__.py
# Support blueprint for support functionality.

from flask import Blueprint

support_bp = Blueprint('support', __name__, template_folder='templates')

from . import routes
