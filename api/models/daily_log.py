from api.utils.database import execute_query, DatabaseError
from api.utils.helpers import generate_uuid

class DailyLog:
    def __init__(self, log_id=None, user_id=None, cycle_id=None, 
                 log_date=None, selections=None):
        self.log_id = log_id
        self.user_id = user_id
        self.cycle_id = cycle_id
        self.log_date = log_date
        self.selections = selections or {}

    @classmethod
    def create(cls, user_id, cycle_id, log_date, selections=None):
        """Create new daily log"""
        log_data = {
            'log_id': generate_uuid(),
            'user_id': user_id,
            'cycle_id': cycle_id,
            'log_date': log_date,
            'selections': selections or {}
        }
        
        try:
            result = execute_query('daily_logs', 'insert', json=log_data)
            if result:
                return cls(**result)
            return None
        except DatabaseError as e:
            raise e

    @classmethod
    def get_user_logs(cls, user_id, start_date=None, end_date=None):
        """Get daily logs for user within date range"""
        try:
            query_params = {
                'columns': '*',
                'eq': ('user_id', user_id),
                'order': ('log_date', {'ascending': False})
            }
            
            if start_date and end_date:
                query_params['gte'] = ('log_date', start_date)
                query_params['lte'] = ('log_date', end_date)
            elif start_date:
                query_params['gte'] = ('log_date', start_date)
            elif end_date:
                query_params['lte'] = ('log_date', end_date)
                
            result = execute_query('daily_logs', 'select', **query_params)
            return [cls(**log) for log in result] if result else []
        except DatabaseError as e:
            raise e

    @classmethod
    def get_cycle_logs(cls, cycle_id, user_id):
        """Get all logs for a specific cycle"""
        try:
            result = execute_query('daily_logs', 'select', columns='*',
                                 eq=('cycle_id', cycle_id))
            # Filter by user_id for security
            user_logs = [log for log in result if log['user_id'] == user_id]
            return [cls(**log) for log in user_logs]
        except DatabaseError as e:
            raise e

    def update(self, **kwargs):
        """Update daily log"""
        try:
            result = execute_query('daily_logs', 'update',
                                 json=kwargs, eq=('log_id', self.log_id))
            return result
        except DatabaseError as e:
            raise e

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'log_id': self.log_id,
            'user_id': self.user_id,
            'cycle_id': self.cycle_id,
            'log_date': str(self.log_date) if self.log_date else None,
            'selections': self.selections
        }
