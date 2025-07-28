# app/blueprints/auth/routes.py
# Authentication routes for login, logout, and profile management.

from flask import request, session, redirect, url_for, render_template, jsonify, g, current_app
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import psycopg2

from . import auth_bp
from app.utils.decorators import login_required

@auth_bp.route('/')
@login_required
def index():
    """Redirect users to their role-specific dashboard."""
    role = session.get('role')
    if role == 'Administrator':
        return redirect(url_for('admin.dashboard'))
    elif role == 'Manager':
        return redirect(url_for('manager.dashboard'))
    elif role == 'Support':
        return redirect(url_for('support.dashboard'))
    elif role == 'Integration Manager':
        return redirect(url_for('support.integration_dashboard'))
    return redirect(url_for('auth.logout'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Log login attempt
        current_app.logger.info("Login attempt for username: %s from IP: %s", username, request.remote_addr)
        
        try:
            db = current_app.get_db()
            cursor = db.cursor()
            cursor.execute("SELECT u.id, u.username, u.password_hash, r.role_name FROM users u JOIN roles r ON u.role_id = r.id WHERE u.username = %s", (username,))
            user = cursor.fetchone()
            cursor.close()
            
            if user is None or not check_password_hash(user['password_hash'], password):
                current_app.logger.warning("Failed login attempt for username: %s from IP: %s", username, request.remote_addr)
                error = 'Incorrect username or password.'
                return render_template('login.html', error=error)
                
            # Successful login
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role_name']
            
            # Session management
            session['last_activity'] = datetime.now().isoformat()
            session['login_timestamp'] = datetime.now().isoformat()
            
            # Check for remember me option
            remember_me = request.form.get('remember_me')
            if remember_me:
                session['remember_me'] = True
                session.permanent = True
            else:
                session['remember_me'] = False
                session.permanent = True
            
            current_app.logger.info("Successful login for user: %s (ID: %s) with role: %s from IP: %s (Remember Me: %s)", 
                          user['username'], user['id'], user['role_name'], request.remote_addr, bool(remember_me))
            
            # Redirect based on role
            if user['role_name'] == 'Administrator':
                return redirect(url_for('admin.dashboard'))
            elif user['role_name'] == 'Manager':
                return redirect(url_for('manager.dashboard'))
            elif user['role_name'] == 'Support':
                return redirect(url_for('support.dashboard'))
            elif user['role_name'] == 'Integration Manager':
                return redirect(url_for('integration.dashboard'))
            else:
                current_app.logger.warning("User %s has unrecognized role: %s", username, user['role_name'])
                return redirect(url_for('auth.login'))
                
        except Exception as e:
            current_app.logger.error("Error during login process for username %s: %s", username, e, exc_info=True)
            error = 'An unexpected error occurred. Please try again.'
            return render_template('login.html', error=error)
            
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    username = session.get('username', 'Unknown')
    user_id = session.get('user_id', 'Unknown')
    current_app.logger.info("User logout: %s (ID: %s) from IP: %s", username, user_id, request.remote_addr)
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    """Serves the user profile page for password management."""
    return render_template('profile.html')

# Profile Management API Routes

@auth_bp.route('/api/profile/change_password', methods=['POST'])
@login_required
def change_password():
    """Allows users to change their own password."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided."}), 400
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    
    # Validate input
    if not current_password or not new_password or not confirm_password:
        return jsonify({"error": "All fields are required."}), 400
    
    if new_password != confirm_password:
        return jsonify({"error": "New passwords do not match."}), 400
    
    if len(new_password) < 8:
        return jsonify({"error": "New password must be at least 8 characters long."}), 400
    
    db = current_app.get_db()
    cursor = db.cursor()
    
    username = session.get('username', 'Unknown')
    user_id = session.get('user_id')
    
    current_app.logger.info("Password change attempt by user %s (ID: %s)", username, user_id)
    
    try:
        # Get current user's password hash
        cursor.execute(
            "SELECT password_hash FROM users WHERE id = %s",
            (session['user_id'],)
        )
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            current_app.logger.warning("Password change failed - user %s not found in database", username)
            return jsonify({"error": "User not found."}), 404
        
        # Verify current password
        if not check_password_hash(user['password_hash'], current_password):
            cursor.close()
            current_app.logger.warning("Password change failed - incorrect current password for user %s", username)
            return jsonify({"error": "Current password is incorrect."}), 401
        
        # Generate new password hash
        new_password_hash = generate_password_hash(new_password)
        
        # Update password in database
        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE id = %s",
            (new_password_hash, session['user_id'])
        )
        
        db.commit()
        cursor.close()
        
        current_app.logger.info("Password changed successfully for user %s (ID: %s)", username, user_id)
        return jsonify({"message": "Password changed successfully."}), 200
        
    except Exception as e:
        db.rollback()
        cursor.close()
        current_app.logger.error("Unexpected error during password change for user %s: %s", username, e, exc_info=True)
        return jsonify({"error": "An unexpected error occurred", "message": str(e)}), 500

@auth_bp.route('/api/profile/update', methods=['PUT'])
@login_required
def update_profile():
    """Allows users to update their own name and email."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided."}), 400
    
    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip()
    
    # Validate input
    if not full_name and not email:
        return jsonify({"error": "At least one field (name or email) must be provided."}), 400
    
    # Basic email validation if email is provided
    if email and '@' not in email:
        return jsonify({"error": "Please provide a valid email address."}), 400
    
    db = current_app.get_db()
    cursor = db.cursor()
    
    username = session.get('username', 'Unknown')
    user_id = session.get('user_id')
    
    current_app.logger.info("Profile update attempt by user %s (ID: %s)", username, user_id)
    
    try:
        # Build update query dynamically based on provided fields
        update_fields = []
        values = []
        
        if full_name:
            update_fields.append("full_name = %s")
            values.append(full_name)
        
        if email:
            # Check if email is already taken by another user
            cursor.execute("SELECT id FROM users WHERE email = %s AND id != %s", (email, user_id))
            existing_user = cursor.fetchone()
            if existing_user:
                cursor.close()
                current_app.logger.warning("Profile update failed - email %s already exists for user %s", email, username)
                return jsonify({"error": "This email address is already in use by another user."}), 409
            
            update_fields.append("email = %s")
            values.append(email)
        
        if update_fields:
            # Add updated_at timestamp
            update_fields.append("updated_at = NOW()")
            values.append(user_id)
            
            # Execute update
            cursor.execute(
                f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s",
                values
            )
            
            db.commit()
        
        # Get updated user information
        cursor.execute(
            "SELECT full_name, email FROM users WHERE id = %s",
            (user_id,)
        )
        updated_user = cursor.fetchone()
        cursor.close()
        
        current_app.logger.info("Profile updated successfully for user %s (ID: %s)", username, user_id)
        return jsonify({
            "message": "Profile updated successfully.",
            "user": {
                "full_name": updated_user['full_name'],
                "email": updated_user['email']
            }
        }), 200
        
    except Exception as e:
        db.rollback()
        cursor.close()
        current_app.logger.error("Unexpected error during profile update for user %s: %s", username, e, exc_info=True)
        return jsonify({"error": "An unexpected error occurred", "message": str(e)}), 500

@auth_bp.route('/api/profile/info', methods=['GET'])
@login_required
def get_profile_info():
    """Get current user's profile information."""
    user_id = session.get('user_id')
    
    db = current_app.get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute(
            "SELECT username, full_name, email FROM users WHERE id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
        cursor.close()
        
        if not user:
            return jsonify({"error": "User not found."}), 404
        
        return jsonify({
            "username": user['username'],
            "full_name": user['full_name'],
            "email": user['email']
        }), 200
        
    except Exception as e:
        cursor.close()
        current_app.logger.error("Error getting profile info for user %s: %s", session.get('username'), e, exc_info=True)
        return jsonify({"error": "An unexpected error occurred", "message": str(e)}), 500
