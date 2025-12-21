# pages/login_page.py:

import allure
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from config import Config

class LoginPage(BasePage):
    # Locators
    USERNAME_INPUT = (By.CSS_SELECTOR, "#user-name")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "#password")
    LOGIN_BTN = (By.CSS_SELECTOR, "#login-button")
    ERROR_MSG = (By.CSS_SELECTOR, "[data-test='error']")

    # Actions
    def load(self):
        with allure.step(f"Navigating to {Config.BASE_URL}"):
            self.logger.info(f"PAGE LOADING: {Config.BASE_URL}")
            self.driver.get(Config.BASE_URL)
            self.take_screenshot("Page Loaded")

    @allure.step("Performing login operation")
    def login(self, username, password):
        # Since send_text and click methods trigger the logger inside BasePage,
        # there is no need to write extra logs here.
        self.send_text(self.USERNAME_INPUT, username)
        self.send_text(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BTN)

    def get_error_message(self):
        text = self.find(self.ERROR_MSG).text
        self.take_screenshot(f"Error Message Seen: {text}")
        self.logger.info(f"ERROR MESSAGE READ: {text}")
        return text