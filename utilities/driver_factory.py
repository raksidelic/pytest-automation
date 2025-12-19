import logging
from typing import Any
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

# --- YENİ EKLENEN: APPIUM KÜTÜPHANELERİ ---
# Eğer 'ModuleNotFoundError' alırsan: pip install Appium-Python-Client
from appium import webdriver as appium_driver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions

# Logger Tanımlaması
logger = logging.getLogger("DriverFactory")

class DriverFactory:
    @staticmethod
    def get_driver(config: Any, execution_id: str) -> WebDriver:
        """
        Verilen konfigürasyona göre (Local, Remote veya Mobile) WebDriver örneği oluşturur.
        execution_id: Her test koşumu için üretilen benzersiz UUID.
        """
        # Config'den platformu al. Eğer yoksa varsayılan 'web' kabul et.
        platform = getattr(config, "PLATFORM_NAME", "web").lower()
        
        logger.info(f"Driver Factory Tetiklendi: {platform.upper()} | ExecID: {execution_id}")

        if platform == "web":
            return DriverFactory._create_web_driver(config, execution_id)
        elif platform == "android":
            return DriverFactory._create_android_driver(config, execution_id)
        elif platform == "ios":
            raise NotImplementedError("❌ iOS desteği henüz eklenmedi.")
        else:
            raise ValueError(f"❌ Bilinmeyen platform: {platform}")

    # =========================================================================
    # BÖLÜM 1: WEB DRIVER (Eski kodlarınız buraya taşındı, mantık aynı)
    # =========================================================================
    @staticmethod
    def _create_web_driver(config: Any, execution_id: str) -> WebDriver:
        browser = config.BROWSER.lower()
        remote_url = config.SELENIUM_REMOTE_URL
        
        logger.info(f"Web Driver Başlatılıyor: {browser.upper()} | Headless: {config.HEADLESS}")

        # 1. Tarayıcı Opsiyonlarını Hazırla
        options = DriverFactory._get_browser_options(browser, config)

        # 2. Remote (Selenoid) veya Local Driver Başlat
        if remote_url:
            return DriverFactory._create_remote_web_driver(remote_url, options, execution_id, config)
        else:
            return DriverFactory._create_local_driver(browser, options)

    @staticmethod
    def _get_browser_options(browser: str, config: Any):
        """Tarayıcıya özel standart opsiyonları ayarlar."""
        options = None
        
        if browser == "chrome":
            options = ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-popup-blocking")
            
        elif browser == "firefox":
            options = FirefoxOptions()
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
        
        else:
            raise ValueError(f"❌ Desteklenmeyen tarayıcı türü: {browser}")

        if config.HEADLESS:
            options.add_argument("--headless")

        return options

    @staticmethod
    def _create_remote_web_driver(remote_url: str, options: Any, execution_id: str, config: Any) -> WebDriver:
        """Remote Web WebDriver (Selenoid/Grid) bağlantısını kurar."""
        
        mode = getattr(config, "RECORD_VIDEO", "on_failure").lower()
        should_record = mode in ["true", "always", "on_failure", "on_success"]

        selenoid_options = {
            "enableVNC": True,
            "enableVideo": should_record,
            "videoScreenSize": "1920x1080",
            "name": execution_id,
            "labels": {
                "env": "test", 
                "team": "qa",
                "execution_id": execution_id
            }
        }
        
        options.set_capability("selenoid:options", selenoid_options)
        
        try:
            logger.info(f"Remote Web bağlantı kuruluyor... (Label: {execution_id})")
            driver = webdriver.Remote(command_executor=remote_url, options=options)
            
            if should_record:
                driver.video_name = f"{driver.session_id}.mp4"
            else:
                driver.video_name = None

            logger.info(f"✅ Web Driver başlatıldı. Video: {driver.video_name}")
            return driver
        
        except Exception as e:
            logger.error(f"❌ Remote Web Driver başlatılamadı! Hata: {e}")
            raise e

    @staticmethod
    def _create_local_driver(browser: str, options: Any) -> WebDriver:
        """Local Web WebDriver başlatır."""
        try:
            if browser == "chrome":
                driver = webdriver.Chrome(options=options)
            elif browser == "firefox":
                driver = webdriver.Firefox(options=options)
            else:
                 raise ValueError(f"Local driver için desteklenmeyen tarayıcı: {browser}")
            
            logger.info("✅ Local Web Driver başarıyla başlatıldı.")
            driver.maximize_window()
            return driver
        except Exception as e:
            logger.error(f"❌ Local Web Driver başlatılamadı! Hata: {e}")
            raise e

    # =========================================================================
    # BÖLÜM 2: MOBILE DRIVER (YENİ EKLENEN KISIM)
    # =========================================================================
    @staticmethod
    def _create_android_driver(config: Any, execution_id: str) -> WebDriver:
        """
        Appium 2.0 Standartlarına uygun Android Sürücüsü.
        """
        options = UiAutomator2Options()
        
        # 1. Temel Yetenekler (Capabilities)
        options.platform_name = "Android"
        options.automation_name = "UiAutomator2"
        options.device_name = getattr(config, "MOBILE_DEVICE_NAME", "Android Emulator")
        
        # 2. Uygulama Kaynağı (URL veya Path)
        app_path = getattr(config, "MOBILE_APP_PATH", None)
        if app_path:
            logger.info(f"📲 Native App Testi Başlatılıyor: {app_path}")
            options.app = app_path
        else:
            # App yoksa Mobile Web (Chrome) Testi demektir
            logger.info("🌐 Mobile Web Testi Başlatılıyor (Chrome)")
            options.set_capability("browserName", "Chrome")
            # Chrome açıldığında 'chromedriver' otomatik devreye girer.

        # 3. Video ve Loglama için Selenoid Etiketleri
        mode = getattr(config, "RECORD_VIDEO", "on_failure").lower()
        should_record = mode in ["true", "always", "on_failure", "on_success"]
        
        selenoid_options = {
            "enableVNC": True,
            "enableVideo": should_record,
            "name": f"Mobile_{execution_id}",
            "labels": {
                "env": "mobile", 
                "team": "qa",
                "execution_id": execution_id
            }
        }
        options.set_capability("selenoid:options", selenoid_options)

        # 4. Bağlantı URL'i (Config'den Mobile URL, yoksa Genel Remote URL)
        remote_url = getattr(config, "MOBILE_REMOTE_URL", None) or config.SELENIUM_REMOTE_URL
        
        if not remote_url:
            raise ValueError("❌ Mobil test için bir Remote URL (Appium/Selenoid) bulunamadı.")

        try:
            logger.info(f"📱 Android Driver başlatılıyor... URL: {remote_url}")
            driver = appium_driver.Remote(command_executor=remote_url, options=options)
            
            if should_record:
                driver.video_name = f"{driver.session_id}.mp4"
            else:
                driver.video_name = None
                
            logger.info(f"✅ Android Driver Hazır. Session: {driver.session_id}")
            return driver
            
        except Exception as e:
            logger.error(f"❌ Android Driver Başlatılamadı: {e}")
            raise e