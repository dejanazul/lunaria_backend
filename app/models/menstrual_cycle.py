from app.utils.database import execute_query, DatabaseError
from app.utils.helpers import generate_uuid

class MenstrualCycle:
    def __init__(self, cycle_id=None, user_id=None, start_date=None, 
                 end_date=None, period_length=None):
        self.cycle_id = cycle_id
        self.user_id = user_id
        self.start_date = start_date
        self.end_date = end_date
        self.period_length = period_length

    @classmethod
    def create(cls, user_id, start_date, end_date=None, period_length=None):
        """Create new menstrual cycle"""
        cycle_data = {
            'cycle_id': generate_uuid(),
            'user_id': user_id,
            'start_date': start_date,
            'end_date': end_date,
            'period_length': period_length
        }
        
        try:
            result = execute_query('menstrual_cycles', 'insert', json=cycle_data)
            if result:
                return cls(**result)
            return None
        except DatabaseError as e:
            raise e

    @classmethod
    def get_user_cycles(cls, user_id, limit=None):
        """Get all cycles for a user"""
        try:
            query_params = {
                'columns': '*',
                'eq': ('user_id', user_id),
                'order': ('start_date', {'ascending': False})
            }
            if limit:
                query_params['limit'] = limit
                
            result = execute_query('menstrual_cycles', 'select', **query_params)
            return [cls(**cycle) for cycle in result] if result else []
        except DatabaseError as e:
            raise e

    @classmethod
    def get_by_id(cls, cycle_id, user_id):
        """Get specific cycle by ID and user"""
        try:
            result = execute_query('menstrual_cycles', 'select', columns='*',
                                 eq=('cycle_id', cycle_id))
            if result and result['user_id'] == user_id:
                return cls(**result)
            return None
        except DatabaseError as e:
            raise e

    def update(self, **kwargs):
        """Update cycle data"""
        try:
            result = execute_query('menstrual_cycles', 'update',
                                 json=kwargs, eq=('cycle_id', self.cycle_id))
            return result
        except DatabaseError as e:
            raise e

    def delete(self):
        """Delete cycle"""
        try:
            result = execute_query('menstrual_cycles', 'delete',
                                 eq=('cycle_id', self.cycle_id))
            return result
        except DatabaseError as e:
            raise e

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'cycle_id': self.cycle_id,
            'user_id': self.user_id,
            'start_date': str(self.start_date) if self.start_date else None,
            'end_date': str(self.end_date) if self.end_date else None,
            'period_length': self.period_length
        }
