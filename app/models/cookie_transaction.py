from app.utils.database import execute_query, DatabaseError
from app.utils.helpers import generate_uuid

class CookieTransaction:
    def __init__(self, transaction_id=None, user_id=None, amount=None,
                 transaction_type=None, description=None, created_at=None):
        self.transaction_id = transaction_id
        self.user_id = user_id
        self.amount = amount
        self.transaction_type = transaction_type
        self.description = description
        self.created_at = created_at

    @classmethod
    def create(cls, user_id, amount, transaction_type, description=None):
        """Create new cookie transaction"""
        transaction_data = {
            'transaction_id': generate_uuid(),
            'user_id': user_id,
            'amount': amount,
            'transaction_type': transaction_type,
            'description': description
        }
        
        try:
            result = execute_query('cookie_transactions', 'insert', json=transaction_data)
            if result:
                return cls(**result)
            return None
        except DatabaseError as e:
            raise e

    @classmethod
    def get_user_transactions(cls, user_id, page=1, limit=20, transaction_type=None):
        """Get user transactions with pagination"""
        try:
            offset = (page - 1) * limit
            query_params = {
                'columns': '*',
                'eq': ('user_id', user_id),
                'order': ('created_at', {'ascending': False}),
                'limit': limit,
                'offset': offset
            }
            
            if transaction_type:
                query_params['eq'] = [('user_id', user_id), ('transaction_type', transaction_type)]
            
            result = execute_query('cookie_transactions', 'select', **query_params)
            return [cls(**tx) for tx in result] if result else []
        except DatabaseError as e:
            raise e

    @classmethod
    def get_user_balance(cls, user_id):
        """Calculate user's current cookie balance"""
        try:
            # Use RPC or custom query for SUM
            from app.utils.database import get_supabase
            supabase = get_supabase()
            
            result = supabase.rpc('get_user_cookie_balance', {'user_id': user_id}).execute()
            
            if result.data:
                return result.data['balance'] or 0
            return 0
        except Exception:
            # Fallback: calculate manually
            transactions = cls.get_all_user_transactions(user_id)
            return sum(tx.amount for tx in transactions)

    @classmethod
    def get_all_user_transactions(cls, user_id):
        """Get all transactions for balance calculation"""
        try:
            result = execute_query('cookie_transactions', 'select', 
                                 columns='amount', eq=('user_id', user_id))
            return [cls(**tx) for tx in result] if result else []
        except DatabaseError as e:
            raise e

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'transaction_id': self.transaction_id,
            'user_id': self.user_id,
            'amount': self.amount,
            'transaction_type': self.transaction_type,
            'description': self.description,
            'created_at': str(self.created_at) if self.created_at else None
        }
