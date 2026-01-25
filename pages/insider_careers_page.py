import time
import allure
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select 
from pages.base_page import BasePage
from locators.insider_locators import InsiderLocators

class InsiderCareersPage(BasePage):
    
    @allure.step("Navigate to QA Careers Page")
    def load_qa_page(self):
        self.driver.get("https://insiderone.com/careers/quality-assurance/")
        self.take_screenshot("QA Careers Page Loaded")

    @allure.step("Click 'See all QA jobs'")
    def click_see_all_jobs(self):
        self.click(InsiderLocators.SEE_ALL_JOBS_BTN)
        time.sleep(2)
        self.take_screenshot("Jobs List Page Opened")

    def try_select_dropdown(self, locator, visible_text, timeout=20):
        """
        Dropdown selection function with a retry mechanism to handle 
        database latency (delayed data loading).
        """
        end_time = time.time() + timeout
        last_exception = None
        
        self.logger.info(f"Waiting for dropdown option: '{visible_text}'")
        
        while time.time() < end_time:
            try:
                dropdown_element = self.find(locator)
                
                select = Select(dropdown_element)
                
                select.select_by_visible_text(visible_text)
                
                self.logger.info(f"Successfully selected: {visible_text}")
                return
                
            except Exception as e:
                last_exception = e
                time.sleep(1)
        
        self.take_screenshot(f"FAIL - Dropdown Selection {visible_text}")
        raise Exception(f"Could not select '{visible_text}' after {timeout} seconds! Last error: {last_exception}")

    @allure.step("Filter Jobs: Location={location}, Dept={department}")
    def apply_filters(self, location, department):
        dropdown_element = self.find(InsiderLocators.LOCATION_FILTER_DROPDOWN)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dropdown_element)
        
        self.try_select_dropdown(InsiderLocators.LOCATION_FILTER_DROPDOWN, location)
        self.take_screenshot(f"Location Selected: {location}")

        self.try_select_dropdown(InsiderLocators.DEPARTMENT_FILTER_DROPDOWN, department)
        self.take_screenshot(f"Department Selected: {department}")

        self.logger.warning("Waiting 5s for job list update (UI Lag Workaround)...")
        time.sleep(5)
        self.take_screenshot("Filters Applied Result")

    @allure.step("Verify Job List Content (STRICT)")
    def verify_jobs_content(self, expected_position, expected_dept, expected_location):
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located(InsiderLocators.JOB_ITEM)
        )
        
        self.logger.info(f"Checking if list matches '{expected_location}'...")
        try:
            WebDriverWait(self.driver, 10).until(
                lambda d: any(expected_location in job.text for job in d.find_elements(*InsiderLocators.JOB_ITEM))
            )
        except Exception:
            self.logger.warning("Smart Wait Timeout: List might not have updated fully yet.")

        self.take_screenshot("Job List Visible & Updated")
        
        jobs = self.driver.find_elements(*InsiderLocators.JOB_ITEM)
        
        if not jobs:
            self.take_screenshot("FAIL - No Jobs Found")
            raise Exception("No jobs found!")

        self.logger.info(f"Found {len(jobs)} jobs. STRICT validation starting...")

        for index, job in enumerate(jobs):
            self.driver.execute_script("arguments[0].scrollIntoView();", job)
            
            pos_title = job.find_element(*InsiderLocators.JOB_POSITION_TITLE).text
            dept_text = job.find_element(*InsiderLocators.JOB_DEPARTMENT).text
            loc_text = job.find_element(*InsiderLocators.JOB_LOCATION).text
            
            self.logger.info(f"Job {index+1}: {pos_title} | {dept_text} | {loc_text}")

            assert expected_position in pos_title, \
                f"STRICT FAIL: Position '{pos_title}' does not contain '{expected_position}'"

            assert expected_dept in dept_text, \
                f"STRICT FAIL: Department '{dept_text}' does not contain '{expected_dept}'"

            assert expected_location in loc_text, \
                f"STRICT FAIL: Location '{loc_text}' does not contain '{expected_location}'"

        self.take_screenshot("All Jobs Verified Successfully")

    @allure.step("Click 'View Role' and verify redirect")
    def verify_view_role_redirect(self):
        jobs = self.driver.find_elements(*InsiderLocators.JOB_ITEM)
        first_job = jobs[0]
        
        view_btn = first_job.find_element(*InsiderLocators.VIEW_ROLE_BTN)
        
        original_window = self.driver.current_window_handle
        
        self.take_screenshot("Before Clicking View Role")
        view_btn.click()
        
        WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
        
        for window_handle in self.driver.window_handles:
            if window_handle != original_window:
                self.driver.switch_to.window(window_handle)
                break
        
        time.sleep(2)
        current_url = self.driver.current_url
        self.take_screenshot("Redirected Page (Lever)")
        
        assert "lever.co" in current_url in current_url, \
            f"Redirect Check Failed! URL '{current_url}' is not a Lever form."
        
        self.driver.close()
        self.driver.switch_to.window(original_window)