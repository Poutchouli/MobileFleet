# app/blueprints/api/__init__.py
# API blueprint for all API endpoints.

from flask import Blueprint

api_bp = Blueprint('api', __name__)

from . import auth_routes
from . import admin_routes  
from . import manager_routes
from . import general_routes
