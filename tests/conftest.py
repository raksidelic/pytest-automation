import pytest
import allure
import logging
from config import Config
from utilities.db_client import DBClient
from utilities.driver_factory import DriverFactory # <-- Artık bunu kullanacağız

# --- GÜRÜLTÜ ENGELLEME ---
logging.getLogger("selenium").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

@pytest.fixture(scope="session")
def db_client():
    client = DBClient()
    yield client
    client.close()

@pytest.fixture(scope="function")
def driver(request):
    """
    Driver Factory kullanarak tarayıcıyı ayağa kaldırır.
    Tüm ayarlar (Remote, Local, Options) DriverFactory içindedir.
    """
    test_name = request.node.name
    
    # --- DRIVER BAŞLATMA (FACTORY KULLANIMI) ---
    driver_instance = None
    try:
        # Kod buraya gelince utilities/driver_factory.py dosyasına gider
        driver_instance = DriverFactory.get_driver(Config, test_name)
        driver_instance.implicitly_wait(Config.TIMEOUT)
        yield driver_instance
    
    except Exception as e:
        print(f"\n[HATA] Driver başlatılamadı: {e}")
        yield None

    # --- TEARDOWN (TEST BİTİŞİ) ---
    # Setup aşamasında hata yoksa ve test koşarken hata aldıysa screenshot al
    if getattr(request.node, 'rep_call', None) and request.node.rep_call.failed:
        if driver_instance:
            try:
                allure.attach(
                    driver_instance.get_screenshot_as_png(), 
                    name="Hata_Goruntusu", 
                    attachment_type=allure.attachment_type.PNG
                )
            except:
                pass
            
    if driver_instance:
        driver_instance.quit()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)