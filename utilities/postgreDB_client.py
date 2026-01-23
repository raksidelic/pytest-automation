# utilities/sql_client.py:

import psycopg2
import logging
from config import Config

class SQLClient:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.logger = logging.getLogger("SQLClient")
        self.config = Config()

    def connect(self):
        """Lazy Connection: Connect when needed."""
        if self.connection:
            return

        dsn = self.config.POSTGRES_DSN
        if not dsn:
            # Falls here if .env is empty
            self.logger.warning("⚠️ PostgreSQL settings missing. Continuing without Test DB connection.")
            return

        try:
            # Security: Do not log the password
            self.logger.info(f"Attempting SQL Connection: {self.config._PG_HOST}:{self.config._PG_PORT}")
            
            self.connection = psycopg2.connect(dsn)
            self.cursor = self.connection.cursor()
            self.logger.info("✅ PostgreSQL Connection Successful.")
        except Exception as e:
            self.logger.error(f"❌ SQL Connection Error: {e}")
            self.connection = None

    def is_connected(self):
        """
        Checks if the database connection is alive.
        """
        self.connect() # Try connecting
        
        if self.connection is None:
            return False

        try:
            # Test connection with the simplest query (Ping)
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except Exception:
            return False

    def execute_query(self, query, params=None):
        self.connect()
        if not self.connection:
            return None

        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            
            if query.strip().upper().startswith("SELECT"):
                return self.cursor.fetchall()
            else:
                return self.cursor.rowcount
        except Exception as e:
            self.logger.error(f"Query Error: {e}")
            self.connection.rollback()
            return None

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            self.logger.info("SQL connection closed.")