import pytest
import allure

@allure.feature("Altyapı Kontrolleri")
class TestInfrastructure:

    @allure.story("PostgreSQL Bağlantı ve Veri Kontrolü")
    def test_postgresql_connection(self, sql_client):
        """
        Bu test:
        1. sql_client fixture'ını kullanarak DB'ye bağlanır.
        2. 'users' tablosunu sorgular.
        3. 'onur_admin' kullanıcısının varlığını doğrular.
        """
        
        with allure.step("Veritabanına SELECT sorgusu atılıyor"):
            # sql_client, conftest.py'dan gelen ve Config'i kullanan güçlü bir nesne
            rows = sql_client.execute_query("SELECT username, role FROM users WHERE username = 'onur_admin'")
        
        with allure.step("Sonuçların doğrulanması"):
            assert rows is not None, "Veritabanı bağlantısı kurulamadı veya sorgu çalışmadı!"
            assert len(rows) > 0, "Sorgu boş döndü! Seed işlemi yapıldı mı?"
            
            user_data = rows[0]
            username = user_data[0]
            role = user_data[1]
            
            print(f"\n[DB SUCCESS] Bulunan Kullanıcı: {username} | Rol: {role}")
            
            assert username == "onur_admin"
            assert role == "admin"