import os
import time
from datetime import datetime

from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_simple():
    return (
        jsonify(
            {
                "status": "ok",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "message": "Service is running",
            }
        ),
        200,
    )
