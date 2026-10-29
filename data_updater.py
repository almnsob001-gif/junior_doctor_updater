# ============================================================
# data_updater.py — النسخة المطابقة تماماً لملفاتك على GitHub
# ============================================================
import os
import json
import urllib.request
import ssl

# رابط المستودع الخاص بك
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
    """جلب البيانات مع تخطي حماية SSL"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    req = urllib.request.Request(url, headers={"User-Agent": "JuniorDoctor/1.0"})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        return resp.read().decode("utf-8")

def check_for_updates(user_data_dir, current_version=1.0):
    """يقرأ ملف version.json ويحمل الرابط الموجود بداخله"""
    err_path = _safe_path(user_data_dir, _ERROR_FILE)
    try:
        # 1. جلب ملف الإصدارات (مهلة 3 ثوانٍ فقط لكي لا يعلق التطبيق بدون نت)
        raw_version = _fetch(VERSION_URL, timeout=3)
        version_info = json.loads(raw_version)
        
        # قراءة الأسماء بالضبط كما كتبتها في GitHub (latest_version و medical_data_url)
        latest_version = float(version_info.get("latest_version", current_version))
        medical_data_url = version_info.get("medical_data_url")

        # 2. إذا كان الإصدار الحالي هو الأحدث، أو لم يوجد رابط، لا تفعل شيئاً
        if latest_version <= float(current_version) or not medical_data_url:
            print("[updater] App is up to date or no data URL provided.")
            return

        # 3. يوجد تحديث -> قم بتحميل البيانات من الرابط المباشر
        print(f"[updater] New version {latest_version} found. Downloading from {medical_data_url}...")
        raw_data = _fetch(medical_data_url, timeout=15)
        new_data = json.loads(raw_data)

        # 4. حفظ البيانات الجديدة بأمان
        data_path = _safe_path(user_data_dir, _DATA_FILE)
        temp_path = data_path + ".tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
        os.replace(temp_path, data_path)

        # 5. مسح أي خطأ سابق
        if os.path.exists(err_path):
            os.remove(err_path)

        print(f"[updater] Successfully updated to version {latest_version}.")

    except Exception as e:
        # حفظ الخطأ لعرضه في الصفحة الرئيسية إذا حدث خطأ
        print(f"[updater] Update skipped/failed: {e}")
        try:
            with open(err_path, "w", encoding="utf-8") as f:
                f.write(f"Error: {str(e)}")
        except Exception:
            pass

def get_error_message(user_data_dir):
    """تقرأ ملف الأخطاء إن وجد (لعرضه في الصفحة الرئيسية)."""
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
    """تقرأ البيانات المحملة بعد أن ينتهي التحميل."""
    path = _safe_path(user_data_dir, _DATA_FILE)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except Exception:
        return {}
