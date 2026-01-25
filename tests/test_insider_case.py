import allure
from pages.insider_home_page import InsiderHomePage
from pages.insider_careers_page import InsiderCareersPage

@allure.feature("Insider Case Study")
@allure.story("QA Job Search & Verification")
@allure.severity(allure.severity_level.CRITICAL)
class TestInsiderCase:

    def test_insider_qa_jobs_workflow(self, driver):
        """
        Insider QA Assessment Scenario:
        1. Home Page Check
        2. Careers Page -> Filter (Istanbul, Turkiye & Quality Assurance)
        3. Verify Job Details
        4. Verify Redirect
        """
        home_page = InsiderHomePage(driver)
        careers_page = InsiderCareersPage(driver)

        # STEP 1: Visit Home Page
        with allure.step("1. Visit https://insiderone.com/"):
            home_page.load()
            home_page.verify_page_loaded()

        # STEP 2: Visit Careers & Filter
        with allure.step("2. Go to Careers QA & Filter"):
            careers_page.load_qa_page()
            careers_page.click_see_all_jobs()
            careers_page.apply_filters(
                location="Istanbul, Turkiye", 
                department="Quality Assurance"
            )

        # STEP 3: Verify Job Lists
        with allure.step("3. Verify Job Details (Position, Dept, Location)"):
            careers_page.verify_jobs_content(
                expected_position="Quality Assurance",
                expected_dept="Quality Assurance",
                expected_location="Istanbul, Turkiye"
            )

        # STEP 4: Check Redirect
        with allure.step("4. Click 'View Role' & Check Redirect"):
            careers_page.verify_view_role_redirect()