from flask import Blueprint, request, g
from app.models.activity_log import ActivityLog
from app.services.cookie_service import CookieService
from app.utils.helpers import format_response, format_error
from app.utils.decorators import auth_required, validate_json
from app.utils.validators import ActivityLogSchema

activities_bp = Blueprint('activities', __name__)

@activities_bp.route('/', methods=['GET'])
@auth_required
def get_activities():
    """Get all activities for current user"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        activity_type = request.args.get('type')
        
        activities = ActivityLog.get_user_activities(
            g.current_user_id, 
            page=page, 
            limit=limit,
            activity_type=activity_type
        )
        
        return format_response(
            [activity.to_dict() for activity in activities],
            "Activities retrieved successfully"
        )
    
    except Exception as e:
        return format_error("Failed to retrieve activities", 500)

@activities_bp.route('/', methods=['POST'])
@auth_required
@validate_json(ActivityLogSchema)
def create_activity():
    """Log new activity"""
    try:
        data = g.validated_data
        activity = ActivityLog.create(
            user_id=g.current_user_id,
            activity_type=data.get('activity_type'),
            duration_min=data.get('duration_min'),
            exercise_rpe=data.get('exercise_rpe'),
            notes=data.get('notes')
        )
        
        # Award cookies for activity completion
        cookie_reward = CookieService.calculate_activity_reward(
            activity_type=data.get('activity_type'),
            duration_min=data.get('duration_min'),
            exercise_rpe=data.get('exercise_rpe')
        )
        
        if cookie_reward > 0:
            CookieService.add_transaction(
                user_id=g.current_user_id,
                amount=cookie_reward,
                transaction_type='activity_completion',
                description=f'Activity: {data.get("activity_type")}'
            )
        
        response_data = activity.to_dict()
        response_data['cookie_reward'] = cookie_reward
        
        return format_response(
            response_data,
            "Activity logged successfully",
            201
        )
    
    except Exception as e:
        return format_error("Failed to log activity", 500)

@activities_bp.route('/<activity_id>', methods=['PUT'])
@auth_required
@validate_json(ActivityLogSchema)
def update_activity(activity_id):
    """Update existing activity"""
    try:
        activity = ActivityLog.get_by_id(activity_id, g.current_user_id)
        if not activity:
            return format_error("Activity not found", 404)
        
        data = g.validated_data
        activity.update(**data)
        
        return format_response(
            activity.to_dict(),
            "Activity updated successfully"
        )
    
    except Exception as e:
        return format_error("Failed to update activity", 500)

@activities_bp.route('/<activity_id>', methods=['DELETE'])
@auth_required
def delete_activity(activity_id):
    """Delete activity"""
    try:
        activity = ActivityLog.get_by_id(activity_id, g.current_user_id)
        if not activity:
            return format_error("Activity not found", 404)
        
        activity.delete()
        
        return format_response(None, "Activity deleted successfully")
    
    except Exception as e:
        return format_error("Failed to delete activity", 500)

@activities_bp.route('/stats', methods=['GET'])
@auth_required
def get_activity_stats():
    """Get activity statistics for current user"""
    try:
        from app.services.activity_service import ActivityService
        stats = ActivityService.get_user_statistics(g.current_user_id)
        
        return format_response(stats, "Statistics retrieved successfully")
    
    except Exception as e:
        return format_error("Failed to retrieve statistics", 500)
