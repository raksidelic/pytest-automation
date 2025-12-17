import psycopg2
from config import Config

def seed_postgres():
    print("🌱 PostgreSQL Tohumlanıyor...")
    
    # 1. Config'den DSN al (Zero Trust yapısını kullanıyoruz)
    dsn = Config().POSTGRES_DSN
    
    if not dsn:
        print("❌ HATA: Bağlantı bilgileri (.env) eksik!")
        return

    try:
        # Localhost'tan bağlanıyorsak host'u 'localhost' yapmamız gerekebilir
        # Ama eğer bu scripti Docker içinden değil de terminalden (local python) çalıştırıyorsan:
        # .env dosyasındaki POSTGRESQL_HOST=postgres_container yerine localhost yazmalısın.
        # Veya docker exec ile çalıştıracağız. Şimdilik kodun sağlamlığına güvenelim.
        
        conn = psycopg2.connect(dsn.replace("postgres_container", "localhost")) 
        cursor = conn.cursor()

        # 2. Temizlik ve Tablo Oluşturma
        cursor.execute("DROP TABLE IF EXISTS users;")
        cursor.execute("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                role VARCHAR(20) NOT NULL
            );
        """)

        # 3. Veri Ekleme
        cursor.execute("INSERT INTO users (username, role) VALUES (%s, %s)", ("onur_admin", "admin"))
        cursor.execute("INSERT INTO users (username, role) VALUES (%s, %s)", ("test_user", "guest"))
        
        conn.commit()
        print("✅ Başarılı: 'users' tablosu oluşturuldu ve 2 kullanıcı eklendi.")
        
        conn.close()

    except Exception as e:
        print(f"❌ Tohumlama Hatası: {e}")
        print("İpucu: Eğer localden çalıştırıyorsan .env dosyasındaki HOST'u geçici olarak 'localhost' yapman gerekebilir.")

if __name__ == "__main__":
    seed_postgres()