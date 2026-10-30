# ============================================================
# data_updater.py — النسخة النهائية (مع سجل التحديثات)
# ============================================================
import os
import json
import urllib.request
import ssl
import threading
import concurrent.futures

REPO_RAW = "https://raw.githubusercontent.com/almnsob001-gif/junior_doctor_updater/main"
VERSION_URL = f"{REPO_RAW}/updates/version.json"

_ERROR_FILE = "update_error.txt"
_DATA_FILE = "downloaded_data.json"
_LAST_VERSION_FILE = "last_version.txt"
_UPDATES_LOG_FILE = "latest_updates.json" # ملف لحفظ التحديثات

def _safe_path(user_data_dir, name):
    try:
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir, exist_ok=True)
        return os.path.join(user_data_dir, name)
    except Exception:
        return os.path.join(os.path.expanduser("~"), name)

def _fetch(url, timeout=15):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={"User-Agent": "JuniorDoctor/1.0"})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        return resp.read().decode("utf-8")

def _download_single_file(url):
    try:
        raw_data = _fetch(url, timeout=15)
        return json.loads(raw_data)
    except Exception as e:
        print(f"[updater] Failed to parse {url}: {e}")
        return None

def _background_update_worker(user_data_dir, current_version):
    err_path = _safe_path(user_data_dir, _ERROR_FILE)
    last_ver_path = _safe_path(user_data_dir, _LAST_VERSION_FILE)
    data_path = _safe_path(user_data_dir, _DATA_FILE)
    updates_log_path = _safe_path(user_data_dir, _UPDATES_LOG_FILE)
    
    try:
        # 1. قراءة الإصدار المحفوظ في الهاتف
        local_version = 0.0
        if os.path.exists(last_ver_path):
            try:
                with open(last_ver_path, "r", encoding="utf-8") as f:
                    local_version = float(f.read().strip())
            except:
                pass

        # 2. جلب ملف الإصدارات
        raw_version = _fetch(VERSION_URL, timeout=10)
        version_info = json.loads(raw_version)
        
        latest_version = float(version_info.get("latest_version", 1.0))
        urls_list = version_info.get("medical_data_urls", [])

        if latest_version <= local_version or not urls_list:
            print("[updater] App is up to date.")
            return

        print(f"[updater] Downloading version {latest_version}...")
        
        # 3. تحميل الملفات في الخلفية
        new_downloaded_data = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {executor.submit(_download_single_file, url): url for url in urls_list}
            for future in concurrent.futures.as_completed(future_to_url):
                part_data = future.result()
                if part_data:
                    for spec, subs in part_data.items():
                        if spec not in new_downloaded_data:
                            new_downloaded_data[spec] = {}
                        for sub, topics in subs.items():
                            if sub not in new_downloaded_data[spec]:
                                new_downloaded_data[spec][sub] = {}
                            for topic, content in topics.items():
                                new_downloaded_data[spec][sub][topic] = content

        if new_downloaded_data:
            # 4. قراءة البيانات القديمة للمقارنة
            existing_data = {}
            if os.path.exists(data_path):
                try:
                    with open(data_path, "r", encoding="utf-8") as f:
                        existing_data = json.load(f) or {}
                except Exception:
                    pass
            
            # 5. مقارنة البيانات لمعرفة "ما الجديد"
            updated_log = []
            for spec, subs in new_downloaded_data.items():
                for sub, topics in subs.items():
                    for topic, content in topics.items():
                        old_content = existing_data.get(spec, {}).get(sub, {}).get(topic)
                        if old_content is None:
                            updated_log.append(f"✨ NEW: {topic}")
                        elif old_content != content:
                            updated_log.append(f"🔄 UPDATED: {topic}")

            # 6. دمج البيانات الجديدة مع القديمة
            for spec, subs in new_downloaded_data.items():
                if spec not in existing_data:
                    existing_data[spec] = {}
                for sub, topics in subs.items():
                    if sub not in existing_data[spec]:
                        existing_data[spec][sub] = {}
                    for topic, content in topics.items():
                        existing_data[spec][sub][topic] = content
                        
            # 7. حفظ البيانات المدمجة
            temp_path = data_path + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
            os.replace(temp_path, data_path)

            # 8. حفظ سجل التحديثات
            if updated_log:
                with open(updates_log_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "version": latest_version,
                        "topics": updated_log
                    }, f, ensure_ascii=False, indent=2)

            # 9. حفظ رقم الإصدار الجديد
            with open(last_ver_path, "w", encoding="utf-8") as f:
                f.write(str(latest_version))

            if os.path.exists(err_path):
                os.remove(err_path)

            print(f"[updater] Successfully updated to {latest_version}.")

    except Exception as e:
        print(f"[updater] Update failed: {e}")
        try:
            with open(err_path, "w", encoding="utf-8") as f:
                f.write(f"Error: {str(e)}")
        except Exception:
            pass

def check_for_updates(user_data_dir, current_version=1.0):
    thread = threading.Thread(target=_background_update_worker, args=(user_data_dir, current_version))
    thread.daemon = True
    thread.start()

def get_error_message(user_data_dir):
    path = _safe_path(user_data_dir, _ERROR_FILE)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            return content if content else None
        except Exception:
            return None
    return None

def load_downloaded_data(user_data_dir):
    path = _safe_path(user_data_dir, _DATA_FILE)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except Exception:
        return {}

def get_latest_updates(user_data_dir):
    path = _safe_path(user_data_dir, _UPDATES_LOG_FILE)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None
