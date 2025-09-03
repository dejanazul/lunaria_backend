from datetime import datetime, timedelta
from api.models.activity_log import ActivityLog

class ActivityService:
    @staticmethod
    def get_user_statistics(user_id):
        """Get activity statistics for user"""
        try:
            from api.utils.database import get_supabase
            supabase = get_supabase()
            
            # Get activities from last 30 days
            thirty_days_ago = (datetime.now() - timedelta(days=30)).date()
            
            activities = ActivityLog.get_user_activities(user_id, page=1, limit=1000)
            recent_activities = [
                a for a in activities 
                if a.performed_at and a.performed_at.date() >= thirty_days_ago
            ]
            
            if not recent_activities:
                return {
                    'total_activities': 0,
                    'total_duration': 0,
                    'avg_duration': 0,
                    'avg_rpe': 0,
                    'most_common_activity': None,
                    'activities_this_month': 0
                }
            
            # Calculate statistics
            total_duration = sum(a.duration_min or 0 for a in recent_activities)
            durations = [a.duration_min for a in recent_activities if a.duration_min]
            rpes = [a.exercise_rpe for a in recent_activities if a.exercise_rpe]
            
            # Activity type frequency
            activity_types = [a.activity_type for a in recent_activities if a.activity_type]
            most_common = max(set(activity_types), key=activity_types.count) if activity_types else None
            
            return {
                'total_activities': len(activities),
                'activities_this_month': len(recent_activities),
                'total_duration': total_duration,
                'avg_duration': round(sum(durations) / len(durations), 1) if durations else 0,
                'avg_rpe': round(sum(rpes) / len(rpes), 1) if rpes else 0,
                'most_common_activity': most_common
            }
            
        except Exception as e:
            raise e