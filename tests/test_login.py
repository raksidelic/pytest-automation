import pytest
import allure
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from utilities.test_data import TestData

@allure.feature("Login Scenarios")
class TestLogin:

    @allure.story("Successful Login Tests")
    @pytest.mark.parametrize("username, password", TestData.VALID_USERS)
    def test_valid_login_scenarios(self, driver, username, password):
        login_page = LoginPage(driver)
        login_page.load()
        login_page.login(username, password)
        
        dashboard = DashboardPage(driver)
        
        allure.attach(driver.get_screenshot_as_png(), name="Dashboard", attachment_type=allure.attachment_type.PNG)
        assert "inventory" in dashboard.get_url(), f"Login failed with {username}!"

    @allure.story("Failed Login Attempts")
    @pytest.mark.parametrize("username, password, error_key", TestData.INVALID_LOGIN_DATA)
    def test_invalid_login_scenarios(self, driver, db_client, username, password, error_key):
        """
        db_client: Fixture coming from conftest.py.
        error_key: 'LOCKED' or 'INVALID' string coming from TestData.
        """
        # 1. Dynamically fetch expected error from database (Lazy Fetch)
        with allure.step(f"Fetching '{error_key}' message from DB"):
            expected_error_msg = db_client.get_error_message(error_key)
            print(f"[{error_key}] Expected Message: {expected_error_msg}")

        # 2. UI Operations
        login_page = LoginPage(driver)
        login_page.load()
        login_page.login(username, password)
        
        allure.attach(driver.get_screenshot_as_png(), name="Error Screen", attachment_type=allure.attachment_type.PNG)
        
        # 3. Verification
        actual_error = login_page.get_error_message()
        assert expected_error_msg in actual_error