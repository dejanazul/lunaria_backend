from flask_jwt_extended import create_access_token, create_refresh_token
from app.models.user import User
from app.utils.helpers import format_error

class AuthService:
    @staticmethod
    def register_user(username, email, password, name=None, birth_date=None):
        """Register new user"""
        # Check if user already exists
        existing_user = User.get_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Create new user
        user = User.create(
            username=username,
            email=email,
            password=password,
            name=name,
            birth_date=birth_date
        )
        
        if user:
            # Generate tokens
            access_token = create_access_token(identity=user.user_id)
            refresh_token = create_refresh_token(identity=user.user_id)
            
            return {
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        
        raise Exception("Failed to create user")

    @staticmethod
    def login_user(email, password):
        """Authenticate user login"""
        user = User.get_by_email(email)
        if not user:
            raise ValueError("Invalid email or password")
        
        if not user.verify_password(password):
            raise ValueError("Invalid email or password")
        
        # Generate tokens
        access_token = create_access_token(identity=user.user_id)
        refresh_token = create_refresh_token(identity=user.user_id)
        
        return {
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }

    @staticmethod
    def refresh_token(user_id):
        """Generate new access token"""
        user = User.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        access_token = create_access_token(identity=user_id)
        return {'access_token': access_token}

def get_user_by_id(user_id):
    """Get user by ID"""
    return User.get_by_id(user_id)
