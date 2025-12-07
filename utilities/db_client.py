from arango import ArangoClient
from config import Config

class DBClient:
    def __init__(self):
        # Client oluştur
        self.client = ArangoClient(hosts=Config.ARANGO_URL)
        
        # DB'ye bağlan
        self.db = self.client.db(
            Config.ARANGO_DB, 
            username=Config.ARANGO_USER, 
            password=Config.ARANGO_PASS
        )

    def get_error_message(self, error_code, lang="message_en"):
        """
        AQL (ArangoDB Query Language) ile veriyi çeker.
        Örnek Query: FOR doc IN error_codes FILTER doc.code == 'LOCKED' RETURN doc.message_en
        """
        # AQL Sorgusu
        aql = f"FOR doc IN error_codes FILTER doc.code == @code RETURN doc.{lang}"
        bind_vars = {'code': error_code}
        
        # Sorguyu çalıştır
        cursor = self.db.aql.execute(aql, bind_vars=bind_vars)
        
        # Sonucu al
        result = [doc for doc in cursor]
        
        if result:
            return result[0]
        else:
            raise ValueError(f"DB Hatası: {error_code} kodlu veri ArangoDB'de bulunamadı!")

    def close(self):
        self.client.close()