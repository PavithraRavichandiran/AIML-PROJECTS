"""
Database Connection Handler - Database-agnostic design
Supports PostgreSQL, MySQL, SQLite with centralized connection management
"""
import sqlite3
import pandas as pd
from typing import Optional, Dict, Any
from contextlib import contextmanager
import os


class DatabaseConnection:
    """Centralized database connection handler"""
    
    _instance = None
    _db_type = None
    _connection_config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def initialize(cls, db_type: str, config: Dict[str, Any]):
        """
        Initialize database connection
        
        Args:
            db_type: 'sqlite', 'postgresql', 'mysql'
            config: Connection configuration dictionary
        """
        cls._db_type = db_type.lower()
        cls._connection_config = config
    
    @classmethod
    def get_connection(cls):
        """Get database connection based on configured type"""
        if cls._db_type == 'sqlite':
            return cls._get_sqlite_connection()
        elif cls._db_type == 'postgresql':
            return cls._get_postgresql_connection()
        elif cls._db_type == 'mysql':
            return cls._get_mysql_connection()
        else:
            raise ValueError(f"Unsupported database type: {cls._db_type}")
    
    @staticmethod
    def _get_sqlite_connection():
        """SQLite connection"""
        db_path = os.getenv('SQLITE_PATH', 'db/cricbuzz.db')
        return sqlite3.connect(db_path)
    
    @staticmethod
    def _get_postgresql_connection():
        """PostgreSQL connection using psycopg2"""
        try:
            import psycopg2
        except ImportError:
            raise ImportError("psycopg2 not installed. Install with: pip install psycopg2-binary")
        
        config = DatabaseConnection._connection_config
        return psycopg2.connect(
            host=config.get('host', 'localhost'),
            port=config.get('port', 5432),
            database=config.get('database'),
            user=config.get('user'),
            password=config.get('password')
        )
    
    @staticmethod
    def _get_mysql_connection():
        """MySQL connection using mysql-connector"""
        try:
            import mysql.connector
        except ImportError:
            raise ImportError("mysql-connector-python not installed. Install with: pip install mysql-connector-python")
        
        config = DatabaseConnection._connection_config
        return mysql.connector.connect(
            host=config.get('host', 'localhost'),
            port=config.get('port', 3306),
            database=config.get('database'),
            user=config.get('user'),
            password=config.get('password')
        )
    
    @contextmanager
    def get_connection_context(self):
        """Context manager for safe connection handling"""
        conn = self.get_connection()
        try:
            yield conn
        finally:
            if conn:
                conn.close()


def run_query(sql: str, params: Optional[tuple] = None) -> pd.DataFrame:
    """
    Execute SQL query and return results as DataFrame
    Database-agnostic implementation
    
    Args:
        sql: SQL query string
        params: Optional parameters for parameterized queries
        
    Returns:
        pd.DataFrame: Query results
    """
    db = DatabaseConnection()
    
    with db.get_connection_context() as conn:
        if params:
            return pd.read_sql_query(sql, conn, params=params)
        else:
            return pd.read_sql_query(sql, conn)


def execute_query(sql: str, params: Optional[tuple] = None) -> int:
    """
    Execute INSERT/UPDATE/DELETE query
    
    Args:
        sql: SQL query string
        params: Optional parameters for parameterized queries
        
    Returns:
        int: Number of affected rows
    """
    db = DatabaseConnection()
    
    with db.get_connection_context() as conn:
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()


# Initialize default SQLite connection
DatabaseConnection.initialize('sqlite', {
    'path': os.getenv('SQLITE_PATH', 'db/cricbuzz.db')
})
