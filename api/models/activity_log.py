from api.utils.database import execute_query, DatabaseError
from api.utils.helpers import generate_uuid

class ActivityLog:
    def __init__(self, activity_log_id=None, user_id=None, activity_type=None,
                 duration_min=None, exercise_rpe=None, performed_at=None, notes=None):
        self.activity_log_id = activity_log_id
        self.user_id = user_id
        self.activity_type = activity_type
        self.duration_min = duration_min
        self.exercise_rpe = exercise_rpe
        self.performed_at = performed_at
        self.notes = notes

    @classmethod
    def create(cls, user_id, activity_type=None, duration_min=None, 
               exercise_rpe=None, notes=None):
        """Create new activity log"""
        activity_data = {
            'activity_log_id': generate_uuid(),
            'user_id': user_id,
            'activity_type': activity_type,
            'duration_min': duration_min,
            'exercise_rpe': exercise_rpe,
            'notes': notes
        }
        
        try:
            result = execute_query('activity_logs', 'insert', json=activity_data)
            if result:
                return cls(**result)
            return None
        except DatabaseError as e:
            raise e

    @classmethod
    def get_user_activities(cls, user_id, page=1, limit=20, activity_type=None):
        """Get user activities with pagination"""
        try:
            offset = (page - 1) * limit
            query_params = {
                'columns': '*',
                'eq': ('user_id', user_id),
                'order': ('performed_at', {'ascending': False}),
                'limit': limit,
                'offset': offset
            }
            
            if activity_type:
                query_params['eq'] = [('user_id', user_id), ('activity_type', activity_type)]
            
            result = execute_query('activity_logs', 'select', **query_params)
            return [cls(**activity) for activity in result] if result else []
        except DatabaseError as e:
            raise e

    @classmethod
    def get_by_id(cls, activity_id, user_id):
        """Get specific activity by ID and user"""
        try:
            result = execute_query('activity_logs', 'select', columns='*',
                                 eq=('activity_log_id', activity_id))
            if result and result['user_id'] == user_id:
                return cls(**result)
            return None
        except DatabaseError as e:
            raise e

    def update(self, **kwargs):
        """Update activity data"""
        try:
            result = execute_query('activity_logs', 'update',
                                 json=kwargs, eq=('activity_log_id', self.activity_log_id))
            return result
        except DatabaseError as e:
            raise e

    def delete(self):
        """Delete activity"""
        try:
            result = execute_query('activity_logs', 'delete',
                                 eq=('activity_log_id', self.activity_log_id))
            return result
        except DatabaseError as e:
            raise e

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'activity_log_id': self.activity_log_id,
            'user_id': self.user_id,
            'activity_type': self.activity_type,
            'duration_min': self.duration_min,
            'exercise_rpe': self.exercise_rpe,
            'performed_at': str(self.performed_at) if self.performed_at else None,
            'notes': self.notes
        }
