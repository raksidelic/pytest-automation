from arango import ArangoClient
from config import Config
import logging

class DBClient:
    def __init__(self):
        self.client = None
        self.db = None
        self.logger = logging.getLogger("DBClient")
        
        # --- DEBUG LOGLARI ---
        print(f"\n[DEBUG] DBClient Başlatılıyor... Hedef: {Config.ARANGO_URL}")

    def _connect(self):
        """
        AKILLI BAĞLANTI YÖNETİCİSİ (State-Based Logic):
        1. Mevcut bağlantı var mı? Varsa 'Ping' at (Zombie Check).
        2. Ping başarısızsa veya hiç bağlantı yoksa, sıfırdan 'Fresh Connection' kur.
        """
        # --- ADIM 1: ZOMBIE CHECK (Mevcut bağlantıyı kontrol et) ---
        if self.db is not None:
            try:
                self.db.properties() # Ping
                return # Bağlantı sağlıklı, çık.
            except Exception:
                print("[DEBUG] ⚠️ Mevcut bağlantı ölü (Zombie), yenileniyor...")
                self.db = None
                self.client = None # Reset

        # --- ADIM 2: FRESH CONNECT (Sıfırdan bağlan) ---
        try:
            self.logger.info(f"DB Bağlantısı deneniyor: {Config.ARANGO_URL}")
            # Client nesnesini sıfırdan yarat
            self.client = ArangoClient(hosts=Config.ARANGO_URL)
            
            temp_db = self.client.db(
                Config.ARANGO_DB, 
                username=Config.ARANGO_USER, 
                password=Config.ARANGO_PASS
            )
            
            # HANDSHAKE (Canlılık ve Yetki Kontrolü)
            temp_db.properties()
            
            self.db = temp_db
            print("[DEBUG] BAĞLANTI BAŞARILI (Fresh Connect)! 🎉")
            self.logger.info("DB Bağlantısı Başarılı.")
            
        except Exception as e:
            print(f"[DEBUG] ❌ Bağlantı Başarısız: {e}")
            self.logger.error(f"DB Bağlantı Hatası: {e}")
            self.db = None
            self.client = None

    def is_connected(self):
        """
        Fixture için kontrol metodu.
        """
        self._connect()
        return self.db is not None

    def get_error_message(self, error_code, lang="message_en"):
        # Bağlantı garantisi (Zombie ise yeniler)
        self._connect()

        if self.db is None:
            return "DB Error: Connection Failed"

        aql = f"FOR doc IN error_codes FILTER doc.code == @code RETURN doc.{lang}"
        bind_vars = {'code': error_code}
        
        try:
            cursor = self.db.aql.execute(aql, bind_vars=bind_vars)
            result = [doc for doc in cursor]
            return result[0] if result else "Unknown Error Code"
        except Exception as e:
            self.logger.error(f"AQL Sorgu Hatası: {e}")
            # Hata aldıysak bağlantıyı sonraki sefer için resetleyelim
            self.db = None 
            return "DB Query Error"

    def close(self):
        if self.client:
            self.client.close()