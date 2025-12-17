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
        """Lazy Connection: İhtiyaç duyulduğunda bağlan."""
        if self.connection:
            return

        dsn = self.config.POSTGRES_DSN
        if not dsn:
            # .env boşsa buraya düşer
            self.logger.warning("⚠️ PostgreSQL ayarları eksik. Test DB bağlantısı olmadan devam edecek.")
            return

        try:
            # Güvenlik: Şifreyi loga basmıyoruz
            self.logger.info(f"SQL Bağlantısı deneniyor: {self.config._PG_HOST}:{self.config._PG_PORT}")
            
            self.connection = psycopg2.connect(dsn)
            self.cursor = self.connection.cursor()
            self.logger.info("✅ PostgreSQL Bağlantısı Başarılı.")
        except Exception as e:
            self.logger.error(f"❌ SQL Bağlantı Hatası: {e}")
            self.connection = None

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
            self.logger.error(f"Sorgu Hatası: {e}")
            self.connection.rollback()
            return None

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            self.logger.info("SQL bağlantısı kapatıldı.")