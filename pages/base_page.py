import allure
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from allure_commons.types import AttachmentType
from config import Config

class BasePage:
    def __init__(self, driver):
        self.driver = driver

    def find(self, locator):
        return WebDriverWait(self.driver, Config.TIMEOUT).until(
            EC.visibility_of_element_located(locator)
        )

    @allure.step("Tıklanıyor: {locator}")
    def click(self, locator):
        self.find(locator).click()
        self.take_screenshot(f"Tıklandı: {locator}")

    @allure.step("Metin yazılıyor: {text}")
    def send_text(self, locator, text):
        element = self.find(locator)
        element.clear()
        element.send_keys(text)
        self.take_screenshot(f"Yazıldı: {text}")

    def get_url(self):
        return self.driver.current_url

    # --- YARDIMCI METOD ---
    def take_screenshot(self, name):
        """Rapora ekran görüntüsü ekleyen merkezi fonksiyon"""
        allure.attach(
            self.driver.get_screenshot_as_png(),
            name=name,
            attachment_type=AttachmentType.PNG
        )