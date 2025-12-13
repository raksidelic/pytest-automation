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

    # 2. Mimari Kontrolü (Explicit Check)
    # ---------------------------------------------------------
    
    # A. ARM MIMARISI (Apple Silicon, Raspberry Pi, AWS Graviton)
    if any(x in arch for x in ["arm", "aarch64"]):
        architecture_type = "ARM"
        browsers_json = "browsers_arm.json"
        
        print("✅ Tespit: ARM Mimarisi (Apple Silicon / RPi)")
        print("📦 ARM uyumlu imajlar (seleniarm) hazırlanıyor...")
        
        # Pull işlemlerini sessizce yap, hata varsa göster
        subprocess.run(["docker", "pull", "seleniarm/standalone-chromium:latest"], check=False)
        subprocess.run(["docker", "pull", "seleniarm/standalone-firefox:latest"], check=False)

    # B. INTEL/AMD MIMARISI (Standart PC, Laptop, Sunucular, CI Runnerlar)
    elif any(x in arch for x in ["x86_64", "amd64", "i386", "i686"]):
        architecture_type = "INTEL"
        browsers_json = "browsers_intel.json"
        
        print("✅ Tespit: Intel/AMD Mimarisi")
        print("📦 Intel uyumlu imajlar (selenoid standard) hazırlanıyor...")
        
        subprocess.run(["docker", "pull", "selenoid/vnc:chrome_120.0"], check=False)
        subprocess.run(["docker", "pull", "selenoid/vnc:firefox_120.0"], check=False)

    # C. TANIMLANAMAYAN MIMARI (Hata Ver ve Dur)
    else:
        print(f"❌ HATA: İşlemci mimarisi tanınamadı: '{arch}'")
        print("   Bu script sadece ARM64 ve x86_64 mimarilerini destekler.")
        print("   Lütfen 'browsers.json' seçimini manuel yapınız.")
        sys.exit(1)

    # 3. Docker Compose'u Başlat
    # ---------------------------------------------------------
    if browsers_json:
        print(f"\n🚀 Test Ortamı Başlatılıyor... (Konfigürasyon: {browsers_json})")
        
        # Mevcut ortam değişkenlerini kopyala ve yenisini ekle
        env = os.environ.copy()
        env["BROWSERS_JSON"] = browsers_json
        
        try:
            # Temizlik
            print("🧹 Eski containerlar temizleniyor...")
            subprocess.run(["docker-compose", "down", "--remove-orphans"], env=env, stderr=subprocess.DEVNULL)
            
            # Başlat ve Exit Code'u Yakala (CI/CD İçin Kritik Kısım)
            print("🚀 Testler Başlatılıyor...")
            
            # --exit-code-from parametresi ile test sonucunu yakalıyoruz.
            # Eğer pytest başarısız olursa, bu komut 0 olmayan bir kod döner.
            result = subprocess.run(
                ["docker-compose", "up", "--build", "--exit-code-from", "pytest-tests"], 
                env=env
            )
            
            # Test sonucunu (0: Başarılı, 1: Hata) işletim sistemine (veya CI'a) bildir.
            # Bu sayede CI pipeline'ı testi failed olarak işaretleyebilir.
            sys.exit(result.returncode)

        except KeyboardInterrupt:
            print("\n🛑 İşlem kullanıcı tarafından iptal edildi.")
            # Kullanıcı durdurduysa temiz çıkış yap, hata kodu döndürme
            sys.exit(0)
            
        except Exception as e:
            print(f"\n❌ Beklenmeyen bir hata oluştu: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()