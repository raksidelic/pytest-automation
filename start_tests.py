import platform
import os
import subprocess
import sys

def main():
    # 1. İşlemci Mimarisini Algıla
    arch = platform.machine().lower()
    system = platform.system()
    
    print(f"🖥️  Sistem Taranıyor... İşletim Sistemi: {system} | İşlemci: {arch}")

    browsers_json = None
    architecture_type = None

    # 2. Mimari Kontrolü
    # ---------------------------------------------------------
    if any(x in arch for x in ["arm", "aarch64"]):
        architecture_type = "ARM"
        browsers_json = "browsers_arm.json"
        print("✅ Tespit: ARM Mimarisi (Apple Silicon / RPi)")
        print("📦 ARM uyumlu imajlar (seleniarm) hazırlanıyor...")
        subprocess.run(["docker", "pull", "seleniarm/standalone-chromium:latest"], check=False)
        subprocess.run(["docker", "pull", "seleniarm/standalone-firefox:latest"], check=False)

    elif any(x in arch for x in ["x86_64", "amd64", "i386", "i686"]):
        architecture_type = "INTEL"
        browsers_json = "browsers_intel.json"
        print("✅ Tespit: Intel/AMD Mimarisi")
        print("📦 Intel uyumlu imajlar (selenoid standard) hazırlanıyor...")
        subprocess.run(["docker", "pull", "selenoid/vnc:chrome_120.0"], check=False)
        subprocess.run(["docker", "pull", "selenoid/vnc:firefox_120.0"], check=False)

    else:
        print(f"❌ HATA: İşlemci mimarisi tanınamadı: '{arch}'")
        sys.exit(1)

    # 3. Docker Compose'u Başlat
    # ---------------------------------------------------------
    if browsers_json:
        print(f"\n🚀 Test Ortamı Başlatılıyor... (Konfigürasyon: {browsers_json})")
        
        env = os.environ.copy()
        env["BROWSERS_JSON"] = browsers_json
        
        try:
            print("🧹 Temizlik Başlıyor...")
            
            # A. Standart Compose Temizliği
            subprocess.run(["docker-compose", "down", "--remove-orphans"], env=env, stderr=subprocess.DEVNULL)
            
            # B. ZORUNLU TEMİZLİK (Conflict Hatası Çözümü)
            # docker-compose bazen proje ismi eşleşmezse eski container'ı silemez.
            # Biz burada isimden yakalayıp zorla siliyoruz (Eski .gitlab-ci.yml mantığı)
            containers_to_kill = ["selenoid", "selenoid-ui", "pytest-test-runner"]
            print(f"🔨 Kalan containerlar zorla siliniyor: {', '.join(containers_to_kill)}")
            
            for container in containers_to_kill:
                # 'docker rm -f' varsa siler, yoksa hata vermez (stderr susturuldu)
                subprocess.run(["docker", "rm", "-f", container], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Başlat ve Exit Code'u Yakala
            print("🚀 Testler Başlatılıyor...")
            result = subprocess.run(
                ["docker-compose", "up", "--build", "--exit-code-from", "pytest-tests"], 
                env=env
            )
            
            sys.exit(result.returncode)

        except KeyboardInterrupt:
            print("\n🛑 İşlem kullanıcı tarafından iptal edildi.")
            sys.exit(0)
            
        except Exception as e:
            print(f"\n❌ Beklenmeyen bir hata oluştu: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()