# ============================================================
# data_updater.py — النسخة الخلفية (تفتح التطبيق فوراً)
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

def _safe_path(user_data_dir, name):
    try:
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir, exist_ok=True)
        return os.path.join(user_data_dir, name)
    except Exception:
        return os.path.join(os.path.expanduser("~"), name)

def _fetch(url, timeout=10):
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
    except Exception:
        return None

# هذه هي الدالة التي تعمل في الخلفية
def _background_update_worker(user_data_dir, current_version):
    err_path = _safe_path(user_data_dir, _ERROR_FILE)
    last_ver_path = _safe_path(user_data_dir, _LAST_VERSION_FILE)
    
    try:
        # 1. قراءة الإصدار المحفوظ في الهاتف
        local_version = 0.0
        if os.path.exists(last_ver_path):
            try:
                with open(last_ver_path, "r", encoding="utf-8") as f:
                    local_version = float(f.read().strip())
            except:
                pass

        # 2. جلب ملف الإصدارات من GitHub (في الخلفية)
        raw_version = _fetch(VERSION_URL, timeout=5)
        version_info = json.loads(raw_version)
        
        latest_version = float(version_info.get("latest_version", 1.0))
        urls_list = version_info.get("medical_data_urls", [])

        if not urls_list and version_info.get("medical_data_url"):
            urls_list = [version_info.get("medical_data_url")]

        # 3. المقارنة: إذا كان إصدار الهاتف هو الأحدث، اخرج بصمت
        if latest_version <= local_version:
            return

        if not urls_list:
            return

        # 4. تحميل الملفات (في الخلفية)
        merged_data = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {executor.submit(_download_single_file, url): url for url in urls_list}
            for future in concurrent.futures.as_completed(future_to_url):
                part_data = future.result()
                if part_data:
                    for spec, subs in part_data.items():
                        if spec not in merged_data:
                            merged_data[spec] = {}
                        for sub, topics in subs.items():
                            if sub not in merged_data[spec]:
                                merged_data[spec][sub] = {}
                            for topic, content in topics.items():
                                merged_data[spec][sub][topic] = content

        # 5. حفظ البيانات الجديدة بصمت
        if merged_data:
            data_path = _safe_path(user_data_dir, _DATA_FILE)
            temp_path = data_path + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(merged_data, f, ensure_ascii=False, indent=2)
            os.replace(temp_path, data_path)

            with open(last_ver_path, "w", encoding="utf-8") as f:
                f.write(str(latest_version))

            if os.path.exists(err_path):
                os.remove(err_path)

    except Exception as e:
        try:
            with open(err_path, "w", encoding="utf-8") as f:
                f.write(f"Error: {str(e)}")
        except Exception:
            pass

# هذه الدالة التي يستدعيها main.py
def check_for_updates(user_data_dir, current_version=1.0):
    """
    تقوم بتشغيل التحديث في الخلفية وتعود فوراً (لا تعطل فتح التطبيق)
    """
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
