# start_tests.py:

import platform
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# --- DEPENDENCY CHECK ---
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  WARNING: 'python-dotenv' library not installed. .env file might not be read.")
    print("👉 To install: pip install python-dotenv")

try:
    import docker
except ImportError:
    print("❌ CRITICAL ERROR: 'docker' library is missing.")
    print("👉 To install: pip install docker")
    sys.exit(1)
# -------------------------------------

# --- DOCKERFILE TEMPLATE ---
DOCKERFILE_TEMPLATE = """
FROM alpine:latest
RUN apk add --no-cache ffmpeg bash xset pulseaudio-utils
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
"""

def is_docker_running():
    """Checks if Docker Daemon is running."""
    try:
        client = docker.from_env()
        client.ping()
        return True
    except Exception:
        return False

def check_image_exists(image_name):
    """Checks if the specified image exists locally using Docker SDK."""
    try:
        client = docker.from_env()
        client.images.get(image_name)
        return True
    except docker.errors.ImageNotFound:
        return False
    except Exception:
        return False

def cleanup_stuck_workers():
    """
    [GLOBAL STANDARD CLEANUP]
    Replaces unsafe 'subprocess.run(..., shell=True)' usage.
    Uses Docker SDK to inspect and remove containers safely.
    
    Logic:
    - Target: Images containing 'selenoid' or 'seleniarm'.
    - Exclude: Images containing 'aerokube' (to keep Hub/UI alive).
    """
    try:
        client = docker.from_env()
        containers = client.containers.list(all=True)
        
        for container in containers:
            try:
                # Image tags usually look like: ['selenoid/vnc:chrome_120.0']
                tags = container.image.tags
                if not tags: 
                    continue
                
                image_name = tags[0]
                
                # Filter Logic
                is_worker = "selenoid" in image_name or "seleniarm" in image_name
                is_infrastructure = "aerokube" in image_name
                
                if is_worker and not is_infrastructure:
                    container.remove(force=True)
            except Exception:
                continue
                
    except Exception as e:
        print(f"⚠️ Worker cleanup failed: {e}")

def build_arm_native_recorder(target_image_name):
    original_image = "selenoid/video-recorder:latest-release"
    
    print(f"   🛠️  ATTENTION: '{target_image_name}' not found. Automatic build process starting...")
    
    # 1. Original Image Check
    if check_image_exists(original_image):
        print(f"   ✅ Original source image ({original_image}) found locally.")
    else:
        print(f"   📥 Pulling original image: {original_image}")
        try:
            client = docker.from_env()
            client.images.pull(original_image)
        except Exception:
            print(f"   ❌ ERROR: Could not pull '{original_image}'. Check internet.")
            sys.exit(1)
    
    # Temporary directory operation
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        script_path = temp_path / "entrypoint.sh"
        dockerfile_path = temp_path / "Dockerfile"
        
        # 2. Extract entrypoint.sh
        print("   📄 Copying entrypoint.sh from original image...")
        try:
            client = docker.from_env()
            # Equivalent to 'docker run --rm --entrypoint cat ...'
            # We use a container to read the file content
            container = client.containers.run(
                original_image, 
                entrypoint="cat /entrypoint.sh",
                remove=True,
                detach=False,
                stdout=True
            )
            with open(script_path, "wb") as f:
                f.write(container)
                
        except Exception as e:
             print(f"   ❌ ERROR: Could not extract entrypoint.sh: {e}")
             sys.exit(1)
        
        if script_path.stat().st_size == 0:
            print("   ❌ ERROR: Extracted entrypoint.sh is empty!")
            sys.exit(1)
            
        # 3. Create Dockerfile
        print("   📝 Creating Dockerfile...")
        with open(dockerfile_path, "w") as f:
            f.write(DOCKERFILE_TEMPLATE.strip())
            
        # 4. Build New Image
        print(f"   🔨 Building Native ARM image: {target_image_name}")
        try:
            client.images.build(path=temp_dir, tag=target_image_name, rm=True)
            print("   ✅ Image successfully built!")
        except Exception as e:
            print(f"   ❌ ERROR: Build failed: {e}")
            sys.exit(1)
            
    print("   🧹 Temporary files cleaned.")

def main():
    # 0. Docker Health Check
    if not is_docker_running():
        print("❌ CRITICAL ERROR: Docker is not running! Please start Docker Desktop.")
        sys.exit(1)

    arch = platform.machine().lower()
    system = platform.system()
    
    print(f"🖥️  Scanning System... OS: {system} | Processor: {arch}")

    browsers_json = None
    video_image = None
    client = docker.from_env()

    # --- 1. ARCHITECTURE CHECK ---
    if any(x in arch for x in ["arm", "aarch64"]):
        print("✅ Detection: ARM Architecture (Apple Silicon)")
        browsers_json = "browsers_arm.json"
        video_image = "selenoid/video-recorder:arm-native"
        auto_worker_count = "3"
        
        if not check_image_exists(video_image):
            build_arm_native_recorder(video_image)
        
        print("   📦 Checking ARM Browser Images...")

        arm_images = [
            "seleniarm/standalone-chromium:latest",
            "seleniarm/standalone-firefox:latest"
        ]

        for img in arm_images:
            if check_image_exists(img):
                print(f"     ✅ Ready: {img}")
            else:
                print(f"     📥 Downloading: {img}")
                try: client.images.pull(img)
                except: pass

    elif any(x in arch for x in ["x86_64", "amd64", "i386", "i686"]):
        print("✅ Detection: Intel/AMD Architecture")
        browsers_json = "browsers_intel.json"
        video_image = "selenoid/video-recorder:latest-release"
        auto_worker_count = "2"
        
        print("   📦 Checking Intel Browser Images...")

        intel_images = [
            "selenoid/vnc:chrome_120.0",
            "selenoid/vnc:firefox_120.0",
            video_image 
        ]

        for img in intel_images:
            if check_image_exists(img):
                print(f"     ✅ Ready: {img}")
            else:
                print(f"     📥 Downloading: {img}")
                try: client.images.pull(img)
                except: pass
    else:
        print(f"❌ ERROR: Architecture not recognized ({arch}).")
        sys.exit(1)

    # --- 2. EXECUTION ---
    final_worker_count = os.getenv("WORKER_COUNT", auto_worker_count)
    
    # --- CLEANUP POLICY ---
    is_ci = os.getenv("CI", "false").lower() == "true"
    default_policy = "never" if is_ci else "on_failure"
    keep_containers_policy = os.getenv("KEEP_CONTAINERS", default_policy).lower()
    # -------------------------------------------------

    if browsers_json and video_image:
        print("\n🚀 Starting Test Environment...")
        print(f"   ⚙️ Cleanup Policy (KEEP_CONTAINERS): {keep_containers_policy}")
        print(f"   📄 Browser Config : {browsers_json}")
        print(f"   🎥 Video Image    : {video_image}")
        
        if final_worker_count != auto_worker_count:
            print(f"   ⚠️ MANUAL SETTING: Worker count set to {final_worker_count}.")
        else:
            print(f"   ⚡ Auto Worker: {final_worker_count}")
        
        env = os.environ.copy()
        env["BROWSERS_JSON"] = browsers_json
        env["VIDEO_RECORDER_IMAGE"] = video_image
        env["WORKER_COUNT"] = final_worker_count
        
        exit_code = 1 
        user_aborted = False 

        try:
            print("🧹 Cleaning up...")
            # 1. Infrastructure Cleanup (Compose)
            subprocess.run(["docker-compose", "down", "--remove-orphans"], env=env, stderr=subprocess.DEVNULL)
            
            # 2. Worker Cleanup (Secure Python Method)
            cleanup_stuck_workers()
            
            print("🎬 Starting Containers...")
            result = subprocess.run(
                ["docker-compose", "up", "--build", "--exit-code-from", "pytest-tests"], 
                env=env
            )
            exit_code = result.returncode

            if exit_code == 130:
                print("\n🛑 Stopped by user (Exit 130).")
                exit_code = 0
                user_aborted = True

        except KeyboardInterrupt:
            print("\n🛑 Stopped by user.")
            exit_code = 0
            user_aborted = True
        except Exception as e:
            print(f"❌ Error: {e}")
            exit_code = 1
        finally:
            # --- CLEANUP LOGIC ---
            should_cleanup = True 

            if keep_containers_policy in ["true", "always"]:
                should_cleanup = False
                print(f"\n🛡️  KEEP_CONTAINERS={keep_containers_policy}: System left running.")
            
            elif keep_containers_policy == "on_failure":
                if exit_code != 0 and not user_aborted: 
                    should_cleanup = False
                    print(f"\n⚠️  Test Failed (Exit: {exit_code}) and Policy=on_failure.")
                    print("🐛 System left RUNNING for debugging.")
                else:
                    print("\n✅ Tests Successful: Cleaning up system.")

            elif keep_containers_policy in ["false", "never"]:
                should_cleanup = True
                print(f"\n🧹 KEEP_CONTAINERS={keep_containers_policy}: Forced cleanup.")

            if not should_cleanup:
                print("👉 UI Address: http://localhost:8080")
                print("🧹 To clean: 'docker-compose down'")
            
            if should_cleanup:
                print("\n🧹 System cleaning (Teardown)...")
                subprocess.run(["docker-compose", "down", "--remove-orphans"], env=env, stderr=subprocess.DEVNULL)
            
            # Action 2: Worker Cleanup (ALWAYS)
            print("🚿 Cleaning workers...")
            cleanup_stuck_workers()
            print("✨ Cleanup complete.")

            sys.exit(exit_code)

if __name__ == "__main__":
    main()