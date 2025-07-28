# app/blueprints/api/auth_routes.py
# Authentication API routes.

from flask import request, jsonify, current_app, session
from werkzeug.security import check_password_hash, generate_password_hash
from . import api_bp
from app.utils.decorators import login_required
from app.utils.helpers import get_db

@api_bp.route('/profile/change_password', methods=['POST'])
@login_required
def change_password():
    """
    Allows users to change their own password.
    Requires current password validation for security.
    """
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
    
    db = get_db()
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

@api_bp.route('/profile/update', methods=['PUT'])
@login_required
def update_profile():
    """
    Allows users to update their own name and email.
    """
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
    
    db = get_db()
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

@api_bp.route('/profile/info', methods=['GET'])
@login_required
def get_profile_info():
    """
    Get current user's profile information.
    """
    user_id = session.get('user_id')
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute(
            "SELECT username, full_name, email FROM users WHERE id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
        cursor.close()
        
        if user:
            return jsonify(user), 200
        else:
            return jsonify({"error": "User not found"}), 404
            
    except Exception as e:
        cursor.close()
        current_app.logger.error("Error getting profile info for user %s: %s", user_id, e, exc_info=True)
        return jsonify({"error": "An unexpected error occurred", "message": str(e)}), 500
