# Rate Limiter Utility for Flask Application
import time
from functools import wraps
from flask import request, jsonify, session
from collections import defaultdict, deque

class RateLimiter:
    def __init__(self):
        # Store request timestamps by user_id and endpoint
        self.requests = defaultdict(lambda: defaultdict(deque))
        # Request limits per endpoint (requests per time window)
        self.limits = {
            'default': (30, 60),  # 30 requests per 60 seconds
            'ticket_details': (10, 30),  # 10 requests per 30 seconds
            'ticket_updates': (5, 30),   # 5 updates per 30 seconds
            'worker_history': (5, 30),   # 5 history requests per 30 seconds
        }
    
    def is_allowed(self, user_id, endpoint_key='default'):
        """Check if request is allowed based on rate limits"""
        now = time.time()
        max_requests, window = self.limits.get(endpoint_key, self.limits['default'])
        
        # Get user's request history for this endpoint
        user_requests = self.requests[user_id][endpoint_key]
        
        # Remove old requests outside the time window
        while user_requests and user_requests[0] < now - window:
            user_requests.popleft()
        
        # Check if under the limit
        if len(user_requests) >= max_requests:
            return False
        
        # Add current request
        user_requests.append(now)
        return True
    
    def get_reset_time(self, user_id, endpoint_key='default'):
        """Get time until rate limit resets"""
        now = time.time()
        _, window = self.limits.get(endpoint_key, self.limits['default'])
        user_requests = self.requests[user_id][endpoint_key]
        
        if not user_requests:
            return 0
        
        oldest_request = user_requests[0]
        reset_time = oldest_request + window - now
        return max(0, reset_time)

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(endpoint_key='default', error_message=None):
    """Decorator to apply rate limiting to Flask routes"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get user ID from session
            user_id = session.get('user_id')
            if not user_id:
                # If no user in session, use IP as fallback
                user_id = request.remote_addr
            
            # Check rate limit
            if not rate_limiter.is_allowed(user_id, endpoint_key):
                reset_time = rate_limiter.get_reset_time(user_id, endpoint_key)
                
                # Custom error message or default
                message = error_message or f"Too many requests. Please wait {int(reset_time)} seconds before trying again."
                
                return jsonify({
                    'error': message,
                    'retry_after': int(reset_time)
                }), 429  # HTTP 429 Too Many Requests
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def debounce_requests(cooldown_seconds=1):
    """Decorator to prevent rapid successive identical requests"""
    last_requests = {}
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id', request.remote_addr)
            endpoint = f"{request.endpoint}:{user_id}"
            now = time.time()
            
            # Check if this is a duplicate request too soon
            if endpoint in last_requests:
                time_since_last = now - last_requests[endpoint]
                if time_since_last < cooldown_seconds:
                    return jsonify({
                        'error': f'Please wait {cooldown_seconds} second(s) between requests',
                        'retry_after': cooldown_seconds - time_since_last
                    }), 429
            
            last_requests[endpoint] = now
            return f(*args, **kwargs)
        return decorated_function
    return decorator
