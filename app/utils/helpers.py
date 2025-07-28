# app/utils/helpers.py
# Utility functions for the Fleet Management application.

from flask import session, current_app

def log_event(cursor, asset_type, asset_id, event_type, details):
    """Helper function for logging events"""
    cursor.execute(
        "INSERT INTO asset_history_log (asset_type, asset_id, event_type, user_id, details) VALUES (%s, %s, %s, %s, %s)",
        (asset_type, asset_id, event_type, session.get('user_id'), details)
    )

def get_db():
    """Get database connection from current app context"""
    return current_app.get_db()
