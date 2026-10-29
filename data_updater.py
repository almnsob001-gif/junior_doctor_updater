# ============================================================
# data_updater.py — نسخة الملفات المنفصلة (Modular System)
# ============================================================
import os
import json
import urllib.request
import ssl

REPO_RAW = "https://raw.githubusercontent.com/almnsob001-gif/junior_doctor_updater/main"
VERSION_URL = f"{REPO_RAW}/updates/version.json"

_ERROR_FILE = "update_error.txt"
_DATA_FILE = "downloaded_data.json"

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

def check_for_updates(user_data_dir, current_version=1.0):
    err_path = _safe_path(user_data_dir, _ERROR_FILE)
    try:
        # 1. جلب ملف الإصدارات
        raw_version = _fetch(VERSION_URL, timeout=3)
        version_info = json.loads(raw_version)
        
        latest_version = float(version_info.get("latest_version", current_version))
        urls_list = version_info.get("medical_data_urls", [])

        # دعم التوافق مع النسخة القديمة إذا كان الرابط مفرداً
        if not urls_list and version_info.get("medical_data_url"):
            urls_list = [version_info.get("medical_data_url")]

        if latest_version <= float(current_version) or not urls_list:
            return

        # 2. تحميل ودمج جميع الملفات في قاموس واحد
        print(f"[updater] Downloading {len(urls_list)} files for version {latest_version}...")
        
        merged_data = {}
        for url in urls_list:
            try:
                raw_data = _fetch(url, timeout=15)
                part_data = json.loads(raw_data)
                
                # دمج ذكي للملفات
                for spec, subs in part_data.items():
                    if spec not in merged_data:
                        merged_data[spec] = {}
                    for sub, topics in subs.items():
                        if sub not in merged_data[spec]:
                            merged_data[spec][sub] = {}
                        for topic, content in topics.items():
                            merged_data[spec][sub][topic] = content
                            
                print(f"[updater] Successfully loaded: {url.split('/')[-1]}")
            except Exception as e:
                print(f"[updater] Failed to load {url}: {e}")

        # 3. حفظ البيانات المدمجة
        if merged_data:
            data_path = _safe_path(user_data_dir, _DATA_FILE)
            temp_path = data_path + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(merged_data, f, ensure_ascii=False, indent=2)
            os.replace(temp_path, data_path)

            if os.path.exists(err_path):
                os.remove(err_path)

        print(f"[updater] All done.")

    except Exception as e:
        print(f"[updater] Update skipped/failed: {e}")
        try:
            with open(err_path, "w", encoding="utf-8") as f:
                f.write(f"Error: {str(e)}")
        except Exception:
            pass

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
