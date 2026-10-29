# ============================================================
# data_updater.py — النسخة الاحترافية (تمنع تعليق التطبيق نهائياً)
# ============================================================
import os
import json
import threading
import urllib.request
import ssl
import traceback

# ⚠️ الرابط الأساسي للمستودع الخاص بك
REPO_RAW = "https://raw.githubusercontent.com/almnsob001-gif/junior_doctor_updater/main"
VERSION_URL = f"{REPO_RAW}/updates/version.json"
DATA_URL_TEMPLATE = f"{REPO_RAW}/updates/data_{{version}}.json"

_ERROR_FILE = "update_error.txt"
_DATA_FILE = "downloaded_data.json"
_LAST_VERSION_FILE = "last_version.txt"

# قفل (Lock) لمنع تداخل عمليات القراءة والكتابة على الملفات
_file_lock = threading.Lock()

def _safe_path(user_data_dir, name):
    try:
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir, exist_ok=True)
        return os.path.join(user_data_dir, name)
    except Exception:
        return os.path.join(os.path.expanduser("~"), name)

def _fetch(url, timeout=8):
    """دالة جلب البيانات مع تخطي التحقق من شهادة SSL (لتجنب مشاكل أندرويد)"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    req = urllib.request.Request(url, headers={"User-Agent": "JuniorDoctor/1.0"})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        return resp.read().decode("utf-8")

def _check_worker(user_data_dir, current_version):
    """هذه الدالة تعمل في الخلفية ولا توقف واجهة التطبيق"""
    err_path = _safe_path(user_data_dir, _ERROR_FILE)
    try:
        # 1. محاولة جلب ملف الإصدار
        try:
            raw = _fetch(VERSION_URL)
            version_info = json.loads(raw)
            latest = float(version_info.get("version", current_version))
        except Exception as e:
            # لا نكتب خطأ إذا كان مجرد انقطاع إنترنت، نتجاهله بصمت
            print(f"[updater] version check skipped: {e}")
            return

        # 2. إذا كان الإصدار الحالي هو الأحدث
        if latest <= float(current_version):
            print("[updater] no update needed")
            return

        # 3. تحميل بيانات الإصدار الجديد
        data_url = DATA_URL_TEMPLATE.format(version=str(latest))
        raw = _fetch(data_url)
        new_data = json.loads(raw)

        # 4. الحفظ بأمان (نكتب في ملف مؤقت ثم نستبدل الأصلي لتجنب تلف البيانات)
        data_path = _safe_path(user_data_dir, _DATA_FILE)
        temp_path = data_path + ".tmp"
        
        with _file_lock:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(new_data, f, ensure_ascii=False, indent=2)
            os.replace(temp_path, data_path) # استبدال آمن

            # 5. حفظ رقم الإصدار
            ver_path = _safe_path(user_data_dir, _LAST_VERSION_FILE)
            with open(ver_path, "w", encoding="utf-8") as f:
                f.write(str(latest))

            # 6. مسح أي خطأ سابق
            if os.path.exists(err_path):
                os.remove(err_path)

        print(f"[updater] updated to version {latest}")

    except Exception:
        # حفظ تفاصيل الخطأ في ملف لكي يقرأه التطبيق
        with _file_lock:
            try:
                with open(err_path, "w", encoding="utf-8") as f:
                    f.write(traceback.format_exc())
            except Exception:
                pass

def check_for_updates(user_data_dir, current_version=1.0):
    """
    هذه الدالة هي التي يستدعيها التطبيق.
    تقوم بتشغيل عملية التحديث في (Thread) منفصل وتعود فوراً.
    """
    t = threading.Thread(
        target=_check_worker,
        args=(user_data_dir, current_version),
        daemon=True
    )
    t.start()

def get_error_message(user_data_dir):
    """تقرأ ملف الأخطاء إن وجد، وتعود فوراً بـ None إذا لم يوجد."""
    path = _safe_path(user_data_dir, _ERROR_FILE)
    if os.path.exists(path):
        try:
            with _file_lock:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
            return content if content else None
        except Exception:
            return None
    return None

def load_downloaded_data(user_data_dir):
    """تقرأ البيانات المحملة سابقاً (تحدث بسرعة ولا تعلق التطبيق)."""
    path = _safe_path(user_data_dir, _DATA_FILE)
    if not os.path.exists(path):
        return {}
    try:
        with _file_lock:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f) or {}
    except Exception:
        return {}
