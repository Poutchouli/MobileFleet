"""
Database utilities and connection management
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import current_app, g

def get_db():
    """Get database connection from Flask g object or create new one"""
    if 'db' not in g:
        try:
            g.db = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'fleet_management'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'admin'),
                cursor_factory=RealDictCursor
            )
        except psycopg2.OperationalError as e:
            current_app.logger.error(f"Database connection failed: {e}")
            raise
    return g.db

def close_db(error=None):
    """Close database connection"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    """Initialize database utilities with Flask app"""
    app.teardown_appcontext(close_db)
