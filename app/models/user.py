from app.utils.database import execute_query, DatabaseError
from app.utils.helpers import hash_password, verify_password, generate_uuid

class User:
    def __init__(self, user_id=None, username=None, email=None, 
                 password_hash=None, name=None, birth_date=None, 
                 cookie_balance=0, created_at=None):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.name = name
        self.birth_date = birth_date
        self.cookie_balance = cookie_balance
        self.created_at = created_at

    @classmethod
    def create(cls, username, email, password, name=None, birth_date=None):
        """Create new user"""
        user_data = {
            'user_id': generate_uuid(),
            'username': username,
            'email': email,
            'password_hash': hash_password(password),
            'name': name,
            'birth_date': birth_date,
            'cookie_balance': 0
        }
        
        try:
            result = execute_query('users', 'insert', json=user_data)
            if result:
                return cls(**result)
            return None
        except DatabaseError as e:
            raise e

    @classmethod
    def get_by_email(cls, email):
        """Get user by email"""
        try:
            result = execute_query('users', 'select', columns='*', 
                                 eq=('email', email))
            if result:
                return cls(**result)
            return None
        except DatabaseError as e:
            raise e

    @classmethod
    def get_by_id(cls, user_id):
        """Get user by ID"""
        try:
            result = execute_query('users', 'select', columns='*', 
                                 eq=('user_id', user_id))
            if result:
                return cls(**result)
            return None
        except DatabaseError as e:
            raise e

    def verify_password(self, password):
        """Verify password"""
        return verify_password(password, self.password_hash)

    def update(self, **kwargs):
        """Update user data"""
        try:
            result = execute_query('users', 'update', 
                                 json=kwargs, eq=('user_id', self.user_id))
            return result
        except DatabaseError as e:
            raise e

    def update_cookie_balance(self, amount):
        """Update cookie balance"""
        new_balance = self.cookie_balance + amount
        self.update(cookie_balance=new_balance)
        self.cookie_balance = new_balance
        return new_balance

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'birth_date': str(self.birth_date) if self.birth_date else None,
            'cookie_balance': self.cookie_balance,
            'created_at': str(self.created_at) if self.created_at else None
        }
