# app/utils/decorators.py
# Authentication and authorization decorators for the Fleet Management application.

import time
from datetime import datetime, timedelta
from functools import wraps
from collections import defaultdict, deque
from flask import session, request, jsonify, redirect, url_for, current_app

# Rate Limiter Implementation
class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(lambda: defaultdict(deque))
        self.limits = {
            'default': (30, 60),
            'ticket_details': (10, 30),
            'ticket_updates': (5, 30),
            'worker_history': (5, 30),
        }
    
    def is_allowed(self, user_id, endpoint_key='default'):
        now = time.time()
        max_requests, window = self.limits.get(endpoint_key, self.limits['default'])
        user_requests = self.requests[user_id][endpoint_key]
        
        while user_requests and user_requests[0] < now - window:
            user_requests.popleft()
        
        if len(user_requests) >= max_requests:
            return False
        
        user_requests.append(now)
        return True

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(endpoint_key='default', error_message=None):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id', request.remote_addr)
            
            if not rate_limiter.is_allowed(user_id, endpoint_key):
                message = error_message or "Too many requests. Please wait before trying again."
                return jsonify({'error': message}), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def debounce_requests(cooldown_seconds=1):
    """Debounce requests decorator"""
    last_requests = {}
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id', request.remote_addr)
            endpoint = f"{request.endpoint}:{user_id}"
            now = time.time()
            
            if endpoint in last_requests:
                time_since_last = now - last_requests[endpoint]
                if time_since_last < cooldown_seconds:
                    return jsonify({'error': f'Please wait {cooldown_seconds} second(s) between requests'}), 429
            
            last_requests[endpoint] = now
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def login_required(f):
    """Authentication required decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Debug logging for session state
        current_app.logger.debug("login_required check for %s - user_id in session: %s, path: %s", 
                        request.endpoint, 'user_id' in session, request.path)
        
        if 'user_id' not in session:
            current_app.logger.warning("Authentication required - no user_id in session for %s", request.path)
            # Return JSON error for API endpoints
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('auth.login', next=request.url))
        
        # Check if session has expired
        if 'last_activity' in session:
            try:
                last_activity = datetime.fromisoformat(session['last_activity'])
                session_timeout = current_app.config['PERMANENT_SESSION_LIFETIME']
                
                # Check if remember_me extends the session
                if session.get('remember_me'):
                    remember_me_days = current_app.config.get('REMEMBER_ME_DAYS', 30)
                    session_timeout = 60 * 60 * 24 * remember_me_days
                
                if datetime.now() - last_activity > timedelta(seconds=session_timeout):
                    current_app.logger.info("Session expired for user %s (last activity: %s)", 
                                   session.get('username', 'Unknown'), session['last_activity'])
                    session.clear()
                    if request.path.startswith('/api/'):
                        return jsonify({'error': 'Session expired'}), 401
                    return redirect(url_for('auth.login', next=request.url))
            except (ValueError, TypeError) as e:
                current_app.logger.debug("Invalid last_activity timestamp for user %s: %s", 
                               session.get('username', 'Unknown'), e)
                session['last_activity'] = datetime.now().isoformat()
        else:
            session['last_activity'] = datetime.now().isoformat()
        
        # Update last activity timestamp for session renewal
        session['last_activity'] = datetime.now().isoformat()
        session.permanent = True
        
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_role):
    """Role-based authorization decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] != required_role:
                return jsonify({"error": "Forbidden"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
