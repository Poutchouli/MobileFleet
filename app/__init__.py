# app/__init__.py
# Main application factory for the Fleet Management application.

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name=None):
    """Application factory pattern"""
    # Configure Flask to find templates and static files in the root directory
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Configure the app
    configure_app(app)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Configure logging
    configure_logging(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Add security headers
    add_security_headers(app)
    
    # Database connection management
    setup_database_handlers(app)
    
    return app

def configure_app(app):
    """Configure Flask app settings"""
    # Session Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Session settings
    session_timeout_hours = int(os.environ.get('SESSION_TIMEOUT_HOURS', 8))
    app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 60 * session_timeout_hours
    app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Remember me configuration
    app.config['REMEMBER_ME_DAYS'] = int(os.environ.get('REMEMBER_ME_DAYS', 30))
    
    # Database Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        os.environ.get('SQLALCHEMY_DATABASE_URI') or 
        os.environ.get('DATABASE_URL')
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def configure_logging(app):
    """Configure structured logging for production use."""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler = RotatingFileHandler(
        'logs/fleet_management.log',
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        logging.Formatter(
            '%(asctime)s %(levelname)s [%(name)s] %(message)s - %(pathname)s:%(lineno)d'
        )
    )
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.DEBUG)
    app.logger.info("Fleet Management application started")

def register_blueprints(app):
    """Register all application blueprints"""
    from app.blueprints.auth import auth_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.manager import manager_bp
    from app.blueprints.support import support_bp
    from app.blueprints.api import api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(manager_bp, url_prefix='/manager')
    app.register_blueprint(support_bp, url_prefix='/support')
    app.register_blueprint(api_bp, url_prefix='/api')

def register_error_handlers(app):
    """Register application error handlers"""
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error('Server Error: %s', error, exc_info=True)
        return {'error': 'Internal server error'}, 500

def add_security_headers(app):
    """Add security headers to all responses"""
    @app.after_request
    def security_headers(response):
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = (
            'browsing-topics=(), interest-cohort=(), geolocation=(), '
            'camera=(), microphone=(), payment=(), usb=(), '
            'magnetometer=(), gyroscope=(), accelerometer=()'
        )
        
        if not app.config.get('DEBUG'):
            response.headers['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdn.jsdelivr.net; "
                "img-src 'self' data:; "
                "font-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com"
            )
        
        return response

def setup_database_handlers(app):
    """Setup database connection handlers"""
    def get_db():
        if 'db' not in g:
            try:
                g.db = psycopg2.connect(
                    os.environ.get('DATABASE_URL'), 
                    cursor_factory=RealDictCursor
                )
                app.logger.debug("Database connection established")
            except psycopg2.OperationalError as e:
                app.logger.error("Database connection failed: %s", e, exc_info=True)
                raise ConnectionError(f"Could not connect to the database: {e}")
            except Exception as e:
                app.logger.error("Unexpected error connecting to database: %s", e, exc_info=True)
                raise
        return g.db

    @app.teardown_appcontext
    def close_db(e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()
            app.logger.debug("Database connection closed")
    
    # Make get_db available globally
    app.get_db = get_db
