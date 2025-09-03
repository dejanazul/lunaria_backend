from datetime import datetime, timedelta
from models.menstrual_cycle import MenstrualCycle
from models.daily_log import DailyLog
from utils.helpers import calculate_cycle_length

class CycleService:
    @staticmethod
    def create_cycle(user_id, start_date, end_date=None, period_length=None):
        """Create new menstrual cycle"""
        cycle = MenstrualCycle.create(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            period_length=period_length
        )
        return cycle

    @staticmethod
    def get_user_cycles(user_id, limit=None):
        """Get all cycles for user"""
        return MenstrualCycle.get_user_cycles(user_id, limit)

    @staticmethod
    def get_cycle_with_logs(user_id, cycle_id):
        """Get cycle with daily logs"""
        cycle = MenstrualCycle.get_by_id(cycle_id, user_id)
        if not cycle:
            return None
        
        logs = DailyLog.get_cycle_logs(cycle_id, user_id)
        
        return {
            'cycle': cycle.to_dict(),
            'logs': [log.to_dict() for log in logs]
        }

    @staticmethod
    def calculate_cycle_statistics(user_id):
        """Calculate cycle statistics for user"""
        cycles = MenstrualCycle.get_user_cycles(user_id)
        
        if len(cycles) < 2:
            return {
                'avg_cycle_length': None,
                'avg_period_length': None,
                'total_cycles': len(cycles)
            }
        
        completed_cycles = [c for c in cycles if c.end_date]
        
        if not completed_cycles:
            return {
                'avg_cycle_length': None,
                'avg_period_length': None,
                'total_cycles': len(cycles)
            }
        
        # Calculate average cycle length
        cycle_lengths = []
        for i in range(len(completed_cycles) - 1):
            current = completed_cycles[i]
            next_cycle = completed_cycles[i + 1]
            length = calculate_cycle_length(next_cycle.start_date, current.start_date)
            cycle_lengths.append(length)
        
        avg_cycle_length = sum(cycle_lengths) / len(cycle_lengths) if cycle_lengths else None
        
        # Calculate average period length
        period_lengths = [c.period_length for c in completed_cycles if c.period_length]
        avg_period_length = sum(period_lengths) / len(period_lengths) if period_lengths else None
        
        return {
            'avg_cycle_length': round(avg_cycle_length, 1) if avg_cycle_length else None,
            'avg_period_length': round(avg_period_length, 1) if avg_period_length else None,
            'total_cycles': len(cycles)
        }

    @staticmethod
    def predict_next_cycle(user_id):
        """Predict next cycle start date"""
        cycles = MenstrualCycle.get_user_cycles(user_id, limit=3)
        
        if len(cycles) < 2:
            return None
        
        stats = CycleService.calculate_cycle_statistics(user_id)
        if not stats['avg_cycle_length']:
            return None
        
        last_cycle = cycles
        if not last_cycle.start_date:
            return None
        
        # Predict next cycle
        next_start = last_cycle.start_date + timedelta(days=int(stats['avg_cycle_length']))
        
        return {
            'predicted_start_date': next_start.isoformat(),
            'confidence': 'high' if len(cycles) >= 3 else 'medium',
            'based_on_cycles': len(cycles)
        }
