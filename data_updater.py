# ============================================================
# data_updater.py — النسخة الذكية (تفتح فوراً بدون نت، وتنتظر التحميل مع النت)
# ============================================================
import os
import json
import urllib.request
import ssl
import socket

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

def is_online():
    """
    فحص سريع جداً للإنترنت (يأخذ أقل من ثانية).
    يتصل بخادم جوجل (8.8.8.8) لمعرفة ما إذا كان هناك اتصال فعلي.
    """
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=1.0)
        return True
    except OSError:
        return False

def _fetch(url, timeout=15):
    """جلب البيانات مع مهلة انتظار (15 ثانية للتحميل، كافية للشبكات الضعيفة)"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    req = urllib.request.Request(url, headers={"User-Agent": "JuniorDoctor/1.0"})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        return resp.read().decode("utf-8")

def check_for_updates(user_data_dir, current_version=1.0):
    """
    إذا لم يكن هناك إنترنت: يفتح التطبيق فوراً.
    إذا كان هناك إنترنت: ينتظر حتى يتم تحميل البيانات الجديدة بالكامل.
    """
    # 1. الفحص السريع: هل هناك إنترنت؟
    if not is_online():
        print("[updater] No internet. Opening app immediately.")
        return

    # 2. يوجد إنترنت -> انتظر وقم بتحميل التحديثات
    err_path = _safe_path(user_data_dir, _ERROR_FILE)
    try:
        # جلب رقم آخر إصدار
        raw = _fetch(VERSION_URL)
        version_info = json.loads(raw)
        latest = float(version_info.get("version", current_version))

        # إذا كان الإصدار الحالي هو الأحدث
        if latest <= float(current_version):
            print("[updater] App is up to date.")
            return

        # تحميل بيانات الإصدار الجديد
        print(f"[updater] Downloading version {latest}...")
        data_url = DATA_URL_TEMPLATE.format(version=str(latest))
        raw = _fetch(data_url)
        new_data = json.loads(raw)

        # حفظ البيانات الجديدة بأمان
        data_path = _safe_path(user_data_dir, _DATA_FILE)
        temp_path = data_path + ".tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
        os.replace(temp_path, data_path)

        # حفظ رقم الإصدار
        ver_path = _safe_path(user_data_dir, _LAST_VERSION_FILE)
        with open(ver_path, "w", encoding="utf-8") as f:
            f.write(str(latest))

        # مسح أي خطأ سابق
        if os.path.exists(err_path):
            os.remove(err_path)

        print(f"[updater] Successfully updated to version {latest}.")

    except Exception as e:
        # حفظ الخطأ بصمت حتى لا يتعطل التطبيق
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
