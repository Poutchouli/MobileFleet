# app/blueprints/api/general_routes.py
# General API routes that don't fit in specific categories.

from flask import jsonify, current_app
from . import api_bp
from app.utils.decorators import login_required, role_required
from app.utils.helpers import get_db
