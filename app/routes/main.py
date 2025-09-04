from flask import Blueprint, jsonify

main_bp = Blueprint("main", __name__)

@main_bp.route("/", methods=["GET"])
def index():
    return jsonify({
        "message": "Flask Railway App is Running!",
        "status": "success",
        "endpoints": {
            "health": "/api/health",
        }
    }), 200