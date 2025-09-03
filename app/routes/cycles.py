from flask import Blueprint, request, g
from app.services.cycle_service import CycleService
from app.utils.helpers import format_response, format_error
from app.utils.decorators import auth_required, validate_json
from app.utils.validators import MenstrualCycleSchema, DailyLogSchema

cycles_bp = Blueprint('cycles', __name__)

@cycles_bp.route('/', methods=['GET'])
@auth_required
def get_cycles():
    """Get all cycles for current user"""
    try:
        limit = request.args.get('limit', type=int)
        cycles = CycleService.get_user_cycles(g.current_user_id, limit)
        
        return format_response(
            [cycle.to_dict() for cycle in cycles],
            "Cycles retrieved successfully"
        )
    
    except Exception as e:
        return format_error("Failed to retrieve cycles", 500)

@cycles_bp.route('/', methods=['POST'])
@auth_required
@validate_json(MenstrualCycleSchema)
def create_cycle():
    """Create new menstrual cycle"""
    try:
        data = g.validated_data
        cycle = CycleService.create_cycle(
            user_id=g.current_user_id,
            start_date=data['start_date'],
            end_date=data.get('end_date'),
            period_length=data.get('period_length')
        )
        
        return format_response(
            cycle.to_dict(),
            "Cycle created successfully",
            201
        )
    
    except Exception as e:
        return format_error("Failed to create cycle", 500)

@cycles_bp.route('/<cycle_id>', methods=['GET'])
@auth_required
def get_cycle(cycle_id):
    """Get specific cycle with logs"""
    try:
        result = CycleService.get_cycle_with_logs(g.current_user_id, cycle_id)
        
        if not result:
            return format_error("Cycle not found", 404)
        
        return format_response(result, "Cycle retrieved successfully")
    
    except Exception as e:
        return format_error("Failed to retrieve cycle", 500)

@cycles_bp.route('/statistics', methods=['GET'])
@auth_required
def get_statistics():
    """Get cycle statistics for current user"""
    try:
        stats = CycleService.calculate_cycle_statistics(g.current_user_id)
        return format_response(stats, "Statistics retrieved successfully")
    
    except Exception as e:
        return format_error("Failed to retrieve statistics", 500)

@cycles_bp.route('/predictions', methods=['GET'])
@auth_required
def get_predictions():
    """Get cycle predictions for current user"""
    try:
        prediction = CycleService.predict_next_cycle(g.current_user_id)
        
        if not prediction:
            return format_response(
                None,
                "Insufficient data for predictions",
                200
            )
        
        return format_response(prediction, "Prediction generated successfully")
    
    except Exception as e:
        return format_error("Failed to generate predictions", 500)

@cycles_bp.route('/<cycle_id>/logs', methods=['POST'])
@auth_required
@validate_json(DailyLogSchema)
def add_daily_log(cycle_id):
    """Add daily log to cycle"""
    try:
        from app.models.daily_log import DailyLog
        from app.models.menstrual_cycle import MenstrualCycle
        
        # Verify cycle belongs to user
        cycle = MenstrualCycle.get_by_id(cycle_id, g.current_user_id)
        if not cycle:
            return format_error("Cycle not found", 404)
        
        data = g.validated_data
        log = DailyLog.create(
            user_id=g.current_user_id,
            cycle_id=cycle_id,
            log_date=data['log_date'],
            selections=data.get('selections', {})
        )
        
        return format_response(
            log.to_dict(),
            "Daily log added successfully",
            201
        )
    
    except Exception as e:
        return format_error("Failed to add daily log", 500)
