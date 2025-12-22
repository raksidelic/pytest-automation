import pytest
import allure
from pages.finom_landing_page import FinomLandingPage

# Test Data: (Country Name, Language Code)
# Language is set to 'None' for Ireland because it redirects directly to the homepage.
LOCALIZATION_DATA = [
    ("Germany", "EN"),
    ("Germany", "DE"),
    ("France", "FR"),
    ("Italy", "EN"),
    ("The Netherlands", "NL"),
    ("Belgium", "FR"),
    ("Spain", "ES"),
    ("Poland", "PL"),
    ("Portugal", "PT"),
    ("Austria", "DE"),
    ("Ireland", None),
    ("Other", "EN"),
    ("Other", "DE"),
    ("Other", "FR"),
    ("Other", "ES"),
    ("Other", "IT"),
    ("Other", "NL")
]

@allure.feature("International Access (Localization)")
@allure.story("Country and Language Selection Automation")
@allure.severity(allure.severity_level.CRITICAL)
class TestFinomLocalization:

    @pytest.mark.parametrize("country, language", LOCALIZATION_DATA)
    def test_country_language_selection(self, driver, country, language):
        """
        Verifies country and language selection on Finom.co entry.
        Language selection is skipped for countries like Ireland.
        """
        page = FinomLandingPage(driver)
        
        # 1. Navigate to Site
        page.load()
        
        # 2. Handle Cookies if present
        page.handle_cookies()
        
        # 3. Select Country
        page.select_country(country)
        
        # 4. Select Language (If necessary)
        if language:
            page.select_language(language)
            
        # 5. Homepage Verification (Sign In)
        page.sign_in()