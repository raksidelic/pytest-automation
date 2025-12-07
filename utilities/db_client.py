from arango import ArangoClient
from config import Config
import logging

class DBClient:
    def __init__(self):
        # Başlangıçta bağlanma! Sadece değişkenleri hazırla.
        self.client = None
        self.db = None
        self.logger = logging.getLogger("DBClient")

    def _connect(self):
        """Gerçek bağlantıyı ihtiyaç anında kurar (Lazy Loading)"""
        if self.db is not None:
            return # Zaten bağlıysa tekrar uğraşma

        try:
            self.logger.info(f"DB Bağlantısı kuruluyor: {Config.ARANGO_URL} -> {Config.ARANGO_DB}")
            self.client = ArangoClient(hosts=Config.ARANGO_URL)
            
            # Bağlantıyı oluştur
            self.db = self.client.db(
                Config.ARANGO_DB, 
                username=Config.ARANGO_USER, 
                password=Config.ARANGO_PASS
            )
            
            # Bağlantıyı test et (Hata varsa burada patlasın ve yakalayalım)
            self.db.properties()
            self.logger.info("DB Bağlantısı Başarılı.")
            
        except Exception as e:
            self.logger.error(f"DB Bağlantı Hatası: {e}")
            # Burada raise etmiyoruz, testin devam etmesine izin verip
            # veriyi çekemezse default değer dönmesini sağlayacağız (Robustness)
            self.db = None 

    def get_error_message(self, error_code, lang="message_en"):
        # Önce bağlanmayı dene
        self._connect()
        
        # Eğer bağlantı başarısız olduysa kod patlamasın, güvenli çıkış yap
        if self.db is None:
            self.logger.warning(f"DB bağlı değil, '{error_code}' için varsayılan mesaj dönülüyor.")
            return "DB Error: Connection Failed"

        aql = f"FOR doc IN error_codes FILTER doc.code == @code RETURN doc.{lang}"
        bind_vars = {'code': error_code}
        
        try:
            cursor = self.db.aql.execute(aql, bind_vars=bind_vars)
            result = [doc for doc in cursor]
            
            if result:
                return result[0]
            else:
                self.logger.warning(f"Uyarı: {error_code} kodlu mesaj DB'de bulunamadı.")
                return "Unknown Error Code"
                
        except Exception as e:
            self.logger.error(f"AQL Sorgu Hatası: {e}")
            return "DB Query Error"

    def close(self):
        if self.client:
            self.client.close()