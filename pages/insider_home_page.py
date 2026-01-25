import allure
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from locators.insider_locators import InsiderLocators

class InsiderHomePage(BasePage):
    
    @allure.step("Load Insider Home Page")
    def load(self):
        self.driver.get("https://insiderone.com/")
        self.take_screenshot("Home Page Loaded")
        self.handle_cookies()
        self.take_screenshot("Cookie Handled")

    @allure.step("Handle Cookies")
    def handle_cookies(self):
        try:
            wait = WebDriverWait(self.driver, 10)
            cookie_btn = wait.until(EC.element_to_be_clickable(InsiderLocators.COOKIE_ACCEPT_BTN))
            
            cookie_btn.click()
            self.logger.info("Cookie banner accepted.")
            
        except Exception:
            self.logger.info("Cookie banner did not appear or was not clickable.")
            self.take_screenshot("No Cookie Banner")
    
    @allure.step("Verify Home Page Content")
    def verify_page_loaded(self):
        assert "Insider" in self.driver.title, "Page title does not contain 'Insider'"
        
        logo = self.find(InsiderLocators.HOME_LOGO)
        assert logo.is_displayed(), "Insider Logo is not visible!"
        
        blocks = self.driver.find_elements(*InsiderLocators.MAIN_BLOCKS)
        assert len(blocks) > 0, "Main page blocks are not loaded!"
        
        self.logger.info("Home page and main blocks verified.")