from datetime import datetime, date
from api.models.cookie_transaction import CookieTransaction
from api.models.user import User

class CookieService:
    # Cookie reward rates
    REWARDS = {
        'daily_login': 10,
        'task_completion': 20,
        'activity_base': 5,
        'community_post': 2,
        'cycle_completion': 50
    }

    @staticmethod
    def get_balance(user_id):
        """Get user's current cookie balance"""
        return CookieTransaction.get_user_balance(user_id)

    @staticmethod
    def get_transactions(user_id, page=1, limit=20, transaction_type=None):
        """Get user's transaction history"""
        return CookieTransaction.get_user_transactions(
            user_id, page, limit, transaction_type
        )

    @staticmethod
    def add_transaction(user_id, amount, transaction_type, description=None):
        """Add new transaction and update user balance"""
        # Create transaction record
        transaction = CookieTransaction.create(
            user_id=user_id,
            amount=amount,
            transaction_type=transaction_type,
            description=description
        )
        
        # Update user's cookie balance
        user = User.get_by_id(user_id)
        if user:
            user.update_cookie_balance(amount)
        
        return transaction

    @staticmethod
    def process_daily_login(user_id):
        """Process daily login reward"""
        today = date.today()
        
        # Check if already claimed today
        transactions = CookieService.get_transactions(user_id, limit=10)
        daily_login_today = any(
            tx.transaction_type == 'daily_login' and 
            tx.created_at and 
            tx.created_at.date() == today
            for tx in transactions
        )
        
        if daily_login_today:
            return {
                'awarded': False,
                'amount': 0,
                'message': 'Daily login already claimed today'
            }
        
        # Award daily login cookies
        amount = CookieService.REWARDS['daily_login']
        transaction = CookieService.add_transaction(
            user_id=user_id,
            amount=amount,
            transaction_type='daily_login',
            description='Daily login bonus'
        )
        
        return {
            'awarded': True,
            'amount': amount,
            'transaction_id': transaction.transaction_id,
            'message': 'Daily login reward claimed!'
        }

    @staticmethod
    def calculate_activity_reward(activity_type, duration_min, exercise_rpe):
        """Calculate cookie reward for activity"""
        if not duration_min:
            return 0
        
        base_reward = CookieService.REWARDS['activity_base']
        
        # Bonus for duration (1 cookie per 10 minutes)
        duration_bonus = max(0, (duration_min // 10))
        
        # Bonus for high intensity (RPE 7-10)
        intensity_bonus = 0
        if exercise_rpe and exercise_rpe >= 7:
            intensity_bonus = exercise_rpe - 6
        
        total_reward = base_reward + duration_bonus + intensity_bonus
        return min(total_reward, 50)  # Cap at 50 cookies per activity

    @staticmethod
    def get_leaderboard(limit=10):
        """Get top cookie earners"""
        try:
            from api.utils.database import get_supabase
            supabase = get_supabase()
            
            # Use RPC function or custom query
            result = supabase.rpc('get_cookie_leaderboard', {'limit_count': limit}).execute()
            
            if result.data:
                return result.data
            
            # Fallback: get from users table
            result = supabase.table('users').select(
                'username, cookie_balance'
            ).order('cookie_balance', desc=True).limit(limit).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            return []

    @staticmethod
    def award_task_completion(user_id, task_description, cookie_reward):
        """Award cookies for task completion"""
        return CookieService.add_transaction(
            user_id=user_id,
            amount=cookie_reward,
            transaction_type='task_completion',
            description=f'Task completed: {task_description}'
        )