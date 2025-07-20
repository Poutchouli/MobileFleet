"""
Authentication and authorization utilities
"""
from functools import wraps
from flask import session, redirect, url_for, current_app, jsonify, request
from werkzeug.security import check_password_hash
from .database import get_db

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({"error": "Authentication required"}), 401
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_role):
    """Decorator to require specific role for routes"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if session.get('role') != required_role:
                if request.is_json:
                    return jsonify({"error": "Insufficient permissions"}), 403
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def authenticate_user(username, password):
    """Authenticate user credentials"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT u.id, u.username, u.password_hash, u.full_name, u.email, 
               r.role_name, u.last_login 
        FROM users u 
        JOIN roles r ON u.role_id = r.id 
        WHERE u.username = %s
    """, (username,))
    
    user = cursor.fetchone()
    cursor.close()
    
    if user and check_password_hash(user['password_hash'], password):
        return {
            'id': user['id'],
            'username': user['username'],
            'full_name': user['full_name'],
            'email': user['email'],
            'role': user['role_name'],
            'last_login': user['last_login']
        }
    return None

def update_last_login(user_id):
    """Update user's last login timestamp"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE users SET last_login = NOW() WHERE id = %s", (user_id,))
    db.commit()
    cursor.close()
