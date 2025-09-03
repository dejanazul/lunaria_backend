import uuid
from datetime import datetime, date
from flask import jsonify
import bcrypt

def generate_uuid():
    """Generate UUID string"""
    return str(uuid.uuid4())

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def format_response(data=None, message="Success", status=200):
    """Standard API response format"""
    return jsonify({
        'status': 'success' if status < 400 else 'error',
        'message': message,
        'data': data
    }), status

def format_error(message="Error occurred", status=400, errors=None):
    """Standard API error response format"""
    response = {
        'status': 'error',
        'message': message
    }
    if errors:
        response['errors'] = errors
    return jsonify(response), status

def serialize_datetime(obj):
    """Serialize datetime objects to ISO format"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return obj

def calculate_cycle_length(start_date, end_date):
    """Calculate cycle length in days"""
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    return (end_date - start_date).days
