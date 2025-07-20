"""
Authentication and authorization routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from ..utils.database import get_db
from ..utils.auth import authenticate_user, update_last_login, login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = authenticate_user(username, password)
        
        if user:
            # Set session variables
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['email'] = user['email']
            session['role'] = user['role']
            
            # Update last login
            update_last_login(user['id'])
            
            # Redirect based on role
            if user['role'] == 'Administrator':
                return redirect(url_for('admin.dashboard'))
            elif user['role'] == 'Manager':
                return redirect(url_for('manager.dashboard'))
            elif user['role'] == 'Support':
                return redirect(url_for('support.dashboard'))
            elif user['role'] == 'Integration Manager':
                return redirect(url_for('integration.dashboard'))
            else:
                return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Handle user logout"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('profile.html')

@auth_bp.route('/api/profile/change_password', methods=['POST'])
@login_required
def change_password():
    """API endpoint to change user password"""
    data = request.get_json()
    
    if not all(key in data for key in ['current_password', 'new_password', 'confirm_password']):
        return jsonify({"error": "All password fields are required."}), 400
    
    if data['new_password'] != data['confirm_password']:
        return jsonify({"error": "New passwords do not match."}), 400
    
    if len(data['new_password']) < 8:
        return jsonify({"error": "New password must be at least 8 characters long."}), 400
    
    user_id = session['user_id']
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Verify current password
        cursor.execute("SELECT password_hash FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user or not check_password_hash(user['password_hash'], data['current_password']):
            return jsonify({"error": "Current password is incorrect."}), 400
        
        # Update password
        new_password_hash = generate_password_hash(data['new_password'])
        cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", 
                      (new_password_hash, user_id))
        db.commit()
        
        return jsonify({"message": "Password changed successfully."}), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({"error": "An error occurred while changing password."}), 500
    finally:
        cursor.close()
