from functools import wraps
from flask import request, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.helpers import format_error
from services.auth_service import get_user_by_id

def auth_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        try:
            user_id = get_jwt_identity()
            g.current_user_id = user_id
            return f(*args, **kwargs)
        except Exception as e:
            return format_error("Authentication required", 401)
    return decorated_function

def load_user(f):
    """Decorator to load current user data"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if hasattr(g, 'current_user_id'):
            user = get_user_by_id(g.current_user_id)
            g.current_user = user
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    @auth_required
    @load_user
    def decorated_function(*args, **kwargs):
        if not getattr(g.current_user, 'is_admin', False):
            return format_error("Admin privileges required", 403)
        return f(*args, **kwargs)
    return decorated_function

def validate_json(schema_class):
    """Decorator to validate JSON request data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                from utils.validators import validate_json_data
                data = validate_json_data(schema_class, request.get_json())
                g.validated_data = data
                return f(*args, **kwargs)
            except Exception as e:
                return format_error(f"Validation error: {str(e)}", 400)
        return decorated_function
    return decorator
