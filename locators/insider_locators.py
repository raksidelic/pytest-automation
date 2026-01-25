from selenium.webdriver.common.by import By

class InsiderLocators:
    # Home Page
    HOME_LOGO = (By.XPATH, "//div[@class='header-logo']")
    MAIN_BLOCKS = (By.TAG_NAME, "section")

    # Cookie Consent
    COOKIE_ACCEPT_BTN = (By.ID, "wt-cli-accept-all-btn")

    # QA Careers Page
    SEE_ALL_JOBS_BTN = (By.XPATH, "//a[contains(text(), 'See all QA jobs')]")

    # Filtering Section
    LOCATION_FILTER_DROPDOWN = (By.ID, "filter-by-location")
    DEPARTMENT_FILTER_DROPDOWN = (By.ID, "filter-by-department")
    
    # Job List
    JOB_LIST_CONTAINER = (By.ID, "jobs-list")
    JOB_ITEM = (By.XPATH, "//*[@id='jobs-list']//div[contains(@class, 'position-list-item')]")
    
    JOB_POSITION_TITLE = (By.XPATH, ".//*[contains(@class, 'position-title')]")
    JOB_DEPARTMENT = (By.XPATH, ".//*[contains(@class, 'position-department')]")
    JOB_LOCATION = (By.XPATH, ".//*[contains(@class, 'position-location')]")
    VIEW_ROLE_BTN = (By.XPATH, ".//a[contains(text(), 'View Role')]")