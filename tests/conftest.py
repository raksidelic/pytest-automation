# tests/conftest.py

import pytest
import allure
import logging
import os
import json
import docker
import fcntl
import glob
from config import Config
from utilities.db_client import DBClient
from utilities.driver_factory import DriverFactory

# --- LOGGING ---
logger = logging.getLogger("Conftest")
logging.getLogger("selenium").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# Manifest Dosyası ve Sonuç Klasörü
ALLURE_RESULTS_DIR = "/app/allure-results"
CLEANUP_MANIFEST = os.path.join(ALLURE_RESULTS_DIR, "cleanup_manifest.jsonl")

@pytest.fixture(scope="session")
def db_client():
    client = DBClient()
    yield client
    client.close()

def _log_video_decision(node_id, test_name, session_id, video_name, action):
    """
    Kritik verileri manifestoya kaydeder.
    EKLENEN: 'node_id' (Eşsiz Test Kimliği) ve 'session_id' (Docker Konteyner Kimliği)
    """
    entry = {
        "node_id": node_id,       # tests/test_login.py::test_func[user1] (Eşsiz)
        "test_name": test_name,   # test_func[user1]
        "session_id": session_id, # Docker konteynerini bulmak için
        "video": video_name, 
        "action": action
    }
    try:
        with open(CLEANUP_MANIFEST, "a") as f:
            fcntl.flock(f, fcntl.LOCK_EX) # 🔒 Güvenli Yazma
            f.write(json.dumps(entry) + "\n")
            fcntl.flock(f, fcntl.LOCK_UN)
    except Exception as e:
        logger.error(f"Manifest dosyasına yazılamadı: {e}")

def _match_json_to_test(json_data, target_node_id):
    """
    Allure JSON'ı ile Pytest Node ID'sini akıllı eşleştirme.
    """
    # 1. FullName Kontrolü (Genellikle: tests.test_login#test_func)
    full_name = json_data.get("fullName", "")
    
    # Node ID'yi paket yapısına çevir (tests/test_x.py -> tests.test_x)
    # Basit bir "içeriyor mu" kontrolü çoğu zaman yeterlidir ama parametreleri ayıklamak lazım.
    
    # JSON'daki isim bizim node_id'nin son parçasıyla uyuşuyor mu?
    # Örn: node_id="...::test_login[user1]" vs JSON Name="test_login" + params
    
    # En güvenli yol: History ID veya Label kontrolü ama basitçe:
    # Allure 'fullName' genellikle dosya yolu ve fonksiyon adını içerir.
    # Bizim target_node_id de bunları içerir.
    
    # Basitleştirilmiş Eşleşme:
    # node_id içindeki dosya yolunu (tests/test_login.py) paket formatına (tests.test_login) çevirip ara.
    normalized_node = target_node_id.replace("/", ".").replace(".py", "").replace("::", ".")
    
    if full_name and full_name in normalized_node:
        return True
        
    # Parametreli testler için 'name' kontrolü (Riskli ama yedek plan)
    # Eğer parametre varsa node_id içinde '[' karakteri olur.
    json_name = json_data.get("name", "")
    if json_name in target_node_id:
        # Eğer node_id parametre içeriyorsa ve json_name ana isimi karşılıyorsa...
        # Daha derin kontrol gerekebilir ama şimdilik bu, sadece 'name' == 'name' den çok daha iyidir.
        return True
        
    return False

def _inject_video_to_teardown(node_id, video_filename):
    """
    Doğru JSON dosyasını bulup videoyu enjekte eder.
    """
    json_files = glob.glob(os.path.join(ALLURE_RESULTS_DIR, "*-result.json"))
    
    for json_file in json_files:
        try:
            with open(json_file, "r+") as f:
                data = json.load(f)
                
                # GELİŞMİŞ EŞLEŞTİRME (Fix for Risk 1)
                if _match_json_to_test(data, node_id):
                    
                    video_attachment = {
                        "name": "Test Videosu",
                        "source": video_filename, 
                        "type": "video/mp4"
                    }

                    # Teardown (Afters) Hedefleme
                    target_step = None
                    if "afters" in data:
                        for step in data["afters"]:
                            if "driver" in step.get("name", ""):
                                target_step = step
                                break
                        if not target_step and data["afters"]:
                            target_step = data["afters"][-1]

                    if target_step:
                        if "attachments" not in target_step: target_step["attachments"] = []
                        if not any(a['source'] == video_filename for a in target_step['attachments']):
                            target_step["attachments"].append(video_attachment)
                    else:
                        if "attachments" not in data: data["attachments"] = []
                        data["attachments"].append(video_attachment)

                    # Dosyayı güncelle
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
                    return # Eşleşme bulundu ve işlendi, çık.
        except: continue

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

@pytest.fixture(scope="function")
def driver(request):
    test_name = request.node.name
    node_id = request.node.nodeid # Eşsiz ID (Fix for Risk 1)
    driver_instance = None
    
    # 1. SETUP
    try:
        driver_instance = DriverFactory.get_driver(Config, test_name)
        driver_instance.implicitly_wait(Config.TIMEOUT)
        yield driver_instance
    except Exception as e:
        logger.error(f"[SETUP HATA] Driver başlatılamadı: {e}")
        yield None

    # 2. TEARDOWN
    if driver_instance:
        # Hata kontrolü
        is_failed = False
        node = request.node
        if getattr(node, 'rep_call', None) and node.rep_call.failed:
            is_failed = True
            try:
                allure.attach(
                    driver_instance.get_screenshot_as_png(), 
                    name="Hata_Goruntusu", 
                    attachment_type=allure.attachment_type.PNG
                )
            except: pass

        # Gerekli verileri topla
        video_name = getattr(driver_instance, 'video_name', None)
        
        # Session ID'yi al (Fix for Risk 3)
        # Driver kapanmadan önce session_id'yi almalıyız!
        session_id = None
        try:
            session_id = driver_instance.session_id
        except: pass

        # Driver'ı kapat
        driver_instance.quit()

        # 3. KARAR VE MANİFESTO
        if video_name:
            mode = Config.RECORD_VIDEO.lower()
            should_keep = False
            
            if mode == "true": should_keep = True
            elif mode == "on_failure" and is_failed: should_keep = True
            elif mode == "on_success" and not is_failed: should_keep = True
            
            action = "keep" if should_keep else "delete"
            
            # Güncellenmiş Karar Kaydı (NodeID ve SessionID ile)
            _log_video_decision(node_id, test_name, session_id, video_name, action)

def pytest_sessionfinish(session, exitstatus):
    """
    POST-PROCESS: SENKRONİZASYON VE İŞLEME
    """
    if hasattr(session.config, 'workerinput'):
        return

    if not os.path.exists(CLEANUP_MANIFEST):
        return

    logger.info("🧹 [POST-PROCESS] Docker Senkronizasyonu ve Raporlama...")
    
    try:
        docker_client = docker.from_env()
    except:
        docker_client = None
    
    manifest_entries = []
    try:
        with open(CLEANUP_MANIFEST, "r") as f:
            for line in f:
                try: manifest_entries.append(json.loads(line.strip()))
                except: pass
    except: pass

    processed_count = 0
    deleted_count = 0

    for entry in manifest_entries:
        video_file = entry.get("video")
        action = entry.get("action")
        node_id = entry.get("node_id") # Test ismi yerine Node ID kullanıyoruz
        session_id = entry.get("session_id") # Konteyner ID
        
        file_path = os.path.join(ALLURE_RESULTS_DIR, video_file)

        # --- A. GÜÇLENDİRİLMİŞ SENKRONİZASYON (Fix for Risk 3) ---
        # Dosya ismi yerine Session ID ile konteyner arıyoruz.
        if docker_client and session_id:
            try:
                # Selenoid, konteynerleri genellikle session_id ile etiketler veya adlandırır.
                # Ya da video kaydediciyi session_id ile ilişkilendirir.
                # En geniş kapsamlı arama: Tüm konteynerleri tara.
                for container in docker_client.containers.list(ignore_removed=True):
                    # Container ID veya Name session_id içeriyor mu? (Selenoid Standardı)
                    c_id = container.id
                    c_name = container.name
                    
                    # Ayrıca video dosyası adı container env/cmd içinde var mı? (Yedek kontrol)
                    # Hem Session ID hem de Dosya Adı kontrolü yapıyoruz.
                    is_related = (session_id in c_id) or \
                                 (session_id in c_name) or \
                                 (video_file in str(container.attrs))
                    
                    if is_related:
                        container.wait() # Bekle
                        break
            except: pass
        
        # --- B. AKSİYON ---
        if action == "keep":
            if os.path.exists(file_path):
                # Yeni inject fonksiyonu node_id kullanıyor
                _inject_video_to_teardown(node_id, video_file)
                processed_count += 1
                
        elif action == "delete":
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except: pass

    if os.path.exists(CLEANUP_MANIFEST):
        os.remove(CLEANUP_MANIFEST)
        
    logger.info(f"✅ Tamamlandı. Eklenen: {processed_count} | Silinen: {deleted_count}")