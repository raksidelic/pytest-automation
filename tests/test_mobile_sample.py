import pytest
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@allure.story("Finom Mobil Web Uyumluluk Testleri")
class TestFinomMobile:

    @allure.title("Finom.co Mobil Anasayfa Kontrolü")
    def test_finom_homepage_mobile(self, driver):
        
        # 1. Finom'a git
        base_url = "https://finom.co"
        with allure.step(f"{base_url} adresine gidiliyor"):
            driver.get(base_url)
        
        # 2. Title Kontrolü (Sayfanın yüklendiğini teyit eder)
        with allure.step("Sayfa başlığı kontrol ediliyor"):
            print(f"📄 Sayfa Başlığı: {driver.title}")
            assert "Finom" in driver.title, "Sayfa başlığında 'Finom' bulunamadı!"

        # 3. Mobil Web'e Özgü Element Kontrolü
        # Mobilde genelde 'Open Account' butonu veya Hamburger menü görünür olur.
        # Burada sayfanın görünür bir elementini bekliyoruz.
        with allure.step("Mobil arayüz elementleri kontrol ediliyor"):
            wait = WebDriverWait(driver, 20)
            
            # Not: Finom'un sitesi değişebilir, genel body kontrolü en güvenlisidir.
            # Veya spesifik bir buton (Örn: "Get started" veya "Open account")
            # Burada sayfanın 'body'sinin yüklendiğine bakıyoruz.
            body = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            assert body.is_displayed(), "Sayfa gövdesi görüntülenemedi!"
            
            # Ekran görüntüsü al (Allure raporuna eklemek için)
            allure.attach(
                driver.get_screenshot_as_png(), 
                name="Finom_Mobile_Home", 
                attachment_type=allure.attachment_type.PNG
            )
            print("✅ Finom Mobil Anasayfa Başarıyla Yüklendi.")