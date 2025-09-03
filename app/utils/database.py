from supabase.client import create_client, Client
from flask import g, current_app
import psycopg2
from psycopg2.extras import RealDictCursor
import os

def init_supabase(app):
    """Initialize Supabase client with Flask app"""
    # Validate configuration first
    from config import validate_config
    try:
        validate_config()
    except ValueError as e:
        app.logger.error(f"Configuration validation failed: {e}")
        raise e
    
    # Initialize Supabase client
    app.supabase_client = create_client(
        app.config['SUPABASE_URL'],
        app.config['SUPABASE_KEY']
    )
    
    # Initialize admin client with service role key (for admin operations)
    if app.config.get('SUPABASE_SERVICE_ROLE_KEY'):
        app.supabase_admin_client = create_client(
            app.config['SUPABASE_URL'],
            app.config['SUPABASE_SERVICE_ROLE_KEY']
        )
    
    app.logger.info("Supabase clients initialized successfully")

def get_supabase() -> Client:
    """Get Supabase client from Flask application context"""
    if 'supabase' not in g:
        g.supabase = current_app.supabase_client
    return g.supabase

def get_supabase_admin() -> Client:
    """Get Supabase admin client (service role) from Flask application context"""
    if 'supabase_admin' not in g:
        if hasattr(current_app, 'supabase_admin_client'):
            g.supabase_admin = current_app.supabase_admin_client
        else:
            # Fallback to regular client
            g.supabase_admin = current_app.supabase_client
    return g.supabase_admin

def get_db_connection():
    """Get direct PostgreSQL connection for complex queries"""
    if 'db_connection' not in g:
        try:
            # Use the appropriate database URL based on environment
            db_url = current_app.config.get('DATABASE_URL') or current_app.config.get('SUPABASE_DB_URL')
            
            g.db_connection = psycopg2.connect(
                db_url,
                cursor_factory=RealDictCursor
            )
            g.db_connection.autocommit = True
        except Exception as e:
            current_app.logger.error(f"Database connection failed: {e}")
            raise DatabaseError(f"Failed to connect to database: {str(e)}")
    
    return g.db_connection

def close_db_connection():
    """Close database connection"""
    db = g.pop('db_connection', None)
    if db is not None:
        db.close()

class DatabaseError(Exception):
    """Custom database exception"""
    pass

def execute_query(table_name, query_method, **kwargs):
    """Execute Supabase query with error handling"""
    try:
        supabase = get_supabase()
        table = supabase.table(table_name)
        result = getattr(table, query_method)(**kwargs).execute()
        
        if hasattr(result, 'error') and result.error:
            raise DatabaseError(f"Database error: {result.error}")
            
        return result.data
    except Exception as e:
        current_app.logger.error(f"Database query failed: {str(e)}")
        raise DatabaseError(f"Database operation failed: {str(e)}")

def execute_raw_sql(query, params=None):
    """Execute raw SQL query using direct PostgreSQL connection"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            
            # Return results for SELECT queries
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            else:
                return cursor.rowcount
                
    except Exception as e:
        current_app.logger.error(f"Raw SQL query failed: {str(e)}")
        raise DatabaseError(f"SQL execution failed: {str(e)}")

# Connection health check
def check_database_health():
    health_status = {
        'supabase': False,
        'postgres': False
    }
    
    try:
        supabase = get_supabase()
        # Simple query to test connection
        result = supabase.table('users').select('user_id').limit(1).execute()
        health_status['supabase'] = True
    except Exception as e:
        current_app.logger.warning(f"Supabase health check failed: {e}")
    
    # Test direct PostgreSQL connection
    try:
        execute_raw_sql("SELECT 1")
        health_status['postgres'] = True
    except Exception as e:
        current_app.logger.warning(f"PostgreSQL health check failed: {e}")
    
    return health_status
