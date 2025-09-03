from flask import jsonify
from werkzeug.exceptions import HTTPException
from marshmallow import ValidationError
from api.utils.database import DatabaseError

def register_error_handlers(app):
    """Register global error handlers"""
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return jsonify({
            'status': 'error',
            'message': 'Validation failed',
            'errors': e.messages
        }), 400
    
    @app.errorhandler(DatabaseError)
    def handle_database_error(e):
        return jsonify({
            'status': 'error',
            'message': 'Database operation failed',
            'error': str(e)
        }), 500
    
    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({
            'status': 'error',
            'message': 'Resource not found'
        }), 404
    
    @app.errorhandler(500)
    def handle_internal_error(e):
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return jsonify({
            'status': 'error',
            'message': e.description,
            'code': e.code
        }), e.code
