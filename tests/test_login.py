import pytest
import allure
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from utilities.test_data import TestData
from utilities.db_client import DBClient  # Client'ı burada import ediyoruz

@allure.epic("Login Testleri")
class TestLogin:

    @allure.story("Başarılı Giriş Testleri")
    @pytest.mark.parametrize("username, password", TestData.VALID_USERS)
    def test_valid_login_scenarios(self, driver, username, password):
        login_page = LoginPage(driver)
        login_page.load()
        login_page.login(username, password)
    
        dashboard = DashboardPage(driver)
    
        # Assertion öncesi son durum kanıtı
        allure.attach(driver.get_screenshot_as_png(), name="Dashboard Kontrolü", attachment_type=allure.attachment_type.PNG)
    
        assert "inventory" in dashboard.get_url(), f"{username} ile giriş yapılamadı!"

    @allure.story("Başarısız Giriş Denemeleri")
    # 'expected_error' yerine 'error_key' (LOCKED, INVALID vb.) alıyoruz
    @pytest.mark.parametrize("username, password, error_key", TestData.INVALID_LOGIN_DATA)
    def test_invalid_login_scenarios(self, driver, username, password, error_key):
        
        # --- KRİTİK DEĞİŞİKLİK: RUNTIME DB FETCH ---
        # Test şu an çalışıyor, demek ki sistem ayakta.
        # Şimdi veritabanına bağlanıp o anahtarın gerçek mesajını çekiyoruz.
        db = DBClient()
        expected_error_message = db.get_error_message(error_key)
        db.close()
        
        # Loglama (Hata olursa CI loglarında ne çektiğimizi görelim)
        print(f"[{username}] İçin Beklenen Mesaj DB'den Çekildi: '{expected_error_message}'")
        # -------------------------------------------

        login_page = LoginPage(driver)
        login_page.load()
        login_page.login(username, password)
    
        # Assertion öncesi son durum kanıtı
        allure.attach(driver.get_screenshot_as_png(), name="Hata Mesajı Kontrolü", attachment_type=allure.attachment_type.PNG)
    
        actual_error = login_page.get_error_message()
        
        # Artık elimizde "DB Error..." değil, veritabanından gelen gerçek mesaj var.
        assert expected_error_message in actual_error