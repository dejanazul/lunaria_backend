from flask import Blueprint, request, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.auth_service import AuthService
from utils.helpers import format_response, format_error
from utils.decorators import validate_json
from utils.validators import UserRegistrationSchema, UserLoginSchema

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@validate_json(UserRegistrationSchema)
def register():
    """User registration endpoint"""
    try:
        data = g.validated_data
        result = AuthService.register_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            name=data.get('name'),
            birth_date=data.get('birth_date')
        )
        
        return format_response(result, "User registered successfully", 201)
    
    except ValueError as e:
        return format_error(str(e), 400)
    except Exception as e:
        return format_error("Registration failed", 500)

@auth_bp.route('/login', methods=['POST'])
@validate_json(UserLoginSchema)
def login():
    """User login endpoint"""
    try:
        data = g.validated_data
        result = AuthService.login_user(
            email=data['email'],
            password=data['password']
        )
        
        return format_response(result, "Login successful")
    
    except ValueError as e:
        return format_error(str(e), 401)
    except Exception as e:
        return format_error("Login failed", 500)

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        user_id = get_jwt_identity()
        result = AuthService.refresh_token(user_id)
        
        return format_response(result, "Token refreshed successfully")
    
    except Exception as e:
        return format_error("Token refresh failed", 500)

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout endpoint"""
    # In a production app, you would add the token to a blacklist
    return format_response(None, "Logged out successfully")

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        user_id = get_jwt_identity()
        from services.auth_service import get_user_by_id
        user = get_user_by_id(user_id)
        
        if not user:
            return format_error("User not found", 404)
        
        return format_response(user.to_dict(), "Profile retrieved successfully")
    
    except Exception as e:
        return format_error("Failed to get profile", 500)
