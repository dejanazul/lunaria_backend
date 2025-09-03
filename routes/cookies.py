from flask import Blueprint, request, g
from services.cookie_service import CookieService
from utils.helpers import format_response, format_error
from utils.decorators import auth_required

cookies_bp = Blueprint('cookies', __name__)

@cookies_bp.route('/balance', methods=['GET'])
@auth_required
def get_balance():
    """Get current cookie balance"""
    try:
        balance = CookieService.get_balance(g.current_user_id)
        return format_response(
            {'balance': balance},
            "Balance retrieved successfully"
        )
    
    except Exception as e:
        return format_error("Failed to get balance", 500)

@cookies_bp.route('/transactions', methods=['GET'])
@auth_required
def get_transactions():
    """Get cookie transaction history"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        transaction_type = request.args.get('type')
        
        transactions = CookieService.get_transactions(
            g.current_user_id, page, limit, transaction_type
        )
        
        return format_response(
            [tx.to_dict() for tx in transactions],
            "Transactions retrieved successfully"
        )
    
    except Exception as e:
        return format_error("Failed to get transactions", 500)

@cookies_bp.route('/daily-login', methods=['POST'])
@auth_required
def daily_login():
    """Award daily login cookies"""
    try:
        result = CookieService.process_daily_login(g.current_user_id)
        
        if result['awarded']:
            return format_response(
                result,
                f"Daily login reward: {result['amount']} cookies!"
            )
        else:
            return format_response(
                result,
                "Daily login already claimed today"
            )
    
    except Exception as e:
        return format_error("Failed to process daily login", 500)

@cookies_bp.route('/spend', methods=['POST'])
@auth_required
def spend_cookies():
    """Spend cookies on items/features"""
    try:
        data = request.get_json()
        item_type = data.get('item_type')
        amount = data.get('amount')
        description = data.get('description', '')
        
        if not item_type or not amount:
            return format_error("item_type and amount are required", 400)
        
        if amount <= 0:
            return format_error("Amount must be positive", 400)
        
        # Check balance
        balance = CookieService.get_balance(g.current_user_id)
        if balance < amount:
            return format_error("Insufficient cookie balance", 400)
        
        # Valid spending categories
        valid_types = ['store_purchase', 'pet_feed', 'unlock_content']
        if item_type not in valid_types:
            return format_error(f"Invalid item_type. Use: {valid_types}", 400)
        
        # Process spending
        transaction = CookieService.add_transaction(
            user_id=g.current_user_id,
            amount=-amount,  # Negative for spending
            transaction_type=item_type,
            description=description
        )
        
        new_balance = CookieService.get_balance(g.current_user_id)
        
        return format_response(
            {
                'transaction': transaction.to_dict(),
                'new_balance': new_balance
            },
            "Cookies spent successfully"
        )
    
    except Exception as e:
        return format_error("Failed to spend cookies", 500)

@cookies_bp.route('/leaderboard', methods=['GET'])
@auth_required
def get_leaderboard():
    """Get cookie leaderboard"""
    try:
        limit = request.args.get('limit', 10, type=int)
        leaderboard = CookieService.get_leaderboard(limit)
        
        return format_response(
            leaderboard,
            "Leaderboard retrieved successfully"
        )
    
    except Exception as e:
        return format_error("Failed to get leaderboard", 500)
