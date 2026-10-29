# ============================================================
# data_updater.py — النسخة المتزامنة (تضمن إضافة المواضيع فوراً)
# ============================================================
import os
import json
import urllib.request
import ssl

# ⚠️ الرابط الأساسي للمستودع الخاص بك
REPO_RAW = "https://raw.githubusercontent.com/almnsob001-gif/junior_doctor_updater/main"
VERSION_URL = f"{REPO_RAW}/updates/version.json"
DATA_URL_TEMPLATE = f"{REPO_RAW}/updates/data_{{version}}.json"

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

def _fetch(url, timeout=3):
    """جلب البيانات مع مهلة قصيرة (3 ثواني) لتجنب تعليق التطبيق"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    req = urllib.request.Request(url, headers={"User-Agent": "JuniorDoctor/1.0"})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        return resp.read().decode("utf-8")

def check_for_updates(user_data_dir, current_version=1.0):
    """
    هذه الدالة الآن متزامنة (تنتظر التحميل لتنتهي قبل أن يكمل التطبيق).
    هذا يضمن أن المواضيع الجديدة ستظهر فوراً عند فتح التطبيق.
    """
    err_path = _safe_path(user_data_dir, _ERROR_FILE)
    try:
        # 1. جلب رقم آخر إصدار من GitHub
        raw = _fetch(VERSION_URL)
        version_info = json.loads(raw)
        latest = float(version_info.get("version", current_version))

        # 2. إذا كان الإصدار الحالي هو الأحدث، لا تفعل شيئاً
        if latest <= float(current_version):
            return

        # 3. تحميل بيانات الإصدار الجديد
        data_url = DATA_URL_TEMPLATE.format(version=str(latest))
        raw = _fetch(data_url)
        new_data = json.loads(raw)

        # 4. حفظ البيانات الجديدة
        data_path = _safe_path(user_data_dir, _DATA_FILE)
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)

        # 5. حفظ رقم الإصدار
        ver_path = _safe_path(user_data_dir, _LAST_VERSION_FILE)
        with open(ver_path, "w", encoding="utf-8") as f:
            f.write(str(latest))

        # 6. مسح أي خطأ سابق
        if os.path.exists(err_path):
            os.remove(err_path)

        print(f"[updater] Updated to version {latest} successfully.")

    except Exception as e:
        # في حال حدوث خطأ (مثل انقطاع الإنترنت)، نحفظه بصمت ولا نغلق التطبيق
        try:
            with open(err_path, "w", encoding="utf-8") as f:
                f.write(str(e))
        except Exception:
            pass

def get_error_message(user_data_dir):
    """تقرأ ملف الأخطاء إن وجد."""
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
