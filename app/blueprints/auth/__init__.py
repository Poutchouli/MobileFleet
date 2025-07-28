# app/blueprints/auth/__init__.py
# Authentication blueprint for login, logout, and profile management.

from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

from . import routes
