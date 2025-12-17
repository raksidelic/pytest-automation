import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # --- ORTAM AYARLARI ---
    ENV = os.getenv("ENV", "STAGE").upper()
    BASE_URL = os.getenv("BASE_URL", "https://www.saucedemo.com")
    TIMEOUT = int(os.getenv("TIMEOUT", 10))
    
    # --- TEST KOŞUM AYARLARI ---
    BROWSER = os.getenv("BROWSER", "chrome").lower()
    HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
    RECORD_VIDEO = os.getenv("RECORD_VIDEO", "on_failure").lower()

    # --- SELENOID / GRID AYARLARI ---
    SELENIUM_REMOTE_URL = os.getenv("SELENIUM_REMOTE_URL")
    
    # --- DATABASE: NOSQL (ARANGO) ---
    ARANGO_URL = os.getenv("ARANGO_URL", "http://localhost:8529")
    ARANGO_DB = os.getenv("ARANGO_DB_NAME", "_system")
    ARANGO_USER = os.getenv("ARANGO_USER", "root")
    ARANGO_PASS = os.getenv("ARANGO_PASSWORD", "")
    
    # --- DATABASE: SQL (POSTGRESQL - Zero Trust) ---
    # Eski ve mükerrer kodlar temizlendi.
    # Varsayılan değer YOK. .env'den gelmek zorunda.
    _PG_HOST = os.getenv("POSTGRESQL_HOST")
    _PG_PORT = os.getenv("POSTGRESQL_PORT")
    _PG_DB = os.getenv("POSTGRESQL_DB")
    _PG_USER = os.getenv("POSTGRESQL_USER")
    _PG_PASS = os.getenv("POSTGRESQL_PASSWORD")

    @property
    def POSTGRES_DSN(self):
        """
        Bağlantı cümlesini oluşturur. Bilgiler eksikse None döner.
        Format: postgresql://user:pass@host:port/dbname
        """
        if not all([self._PG_HOST, self._PG_USER, self._PG_PASS, self._PG_DB]):
            return None
        
        return f"postgresql://{self._PG_USER}:{self._PG_PASS}@{self._PG_HOST}:{self._PG_PORT}/{self._PG_DB}"

    @staticmethod
    def is_remote():
        """Testlerin Selenoid üzerinde mi yoksa lokalde mi koştuğunu belirler."""
        return Config.SELENIUM_REMOTE_URL is not None