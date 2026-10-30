# ============================================================
# data_updater.py — النسخة النهائية الجاهزة للنشر
# ------------------------------------------------------------
# الإصلاحات المطبَّقة:
#   1. تفعيل التحقق من شهادة SSL (حذف CERT_NONE)
#   2. الاستبدال الكامل بدل الدمج (الحذف من GitHub ينتقل للهاتف)
#   3. إلغاء fallback expanduser("~") الذي يفشل على أندرويد
#   4. تسجيل الحذف في سجل التحديثات (🗑️ REMOVED)
#   5. رفض التحديث كلياً إذا فشل أي ملف (حماية من بيانات جزئية)
# ============================================================
import os
import json
import ssl
import urllib.request
import threading
import concurrent.futures

REPO_RAW = "https://raw.githubusercontent.com/almnsob001-gif/junior_doctor_updater/main"
VERSION_URL = f"{REPO_RAW}/updates/version.json"

_ERROR_FILE       = "update_error.txt"
_DATA_FILE        = "downloaded_data.json"
_LAST_VERSION_FILE = "last_version.txt"
_UPDATES_LOG_FILE = "latest_updates.json"


# ------------------------------------------------------------
# مساعدات الملفات
# ------------------------------------------------------------
def _safe_path(user_data_dir, name):
    if not user_data_dir:
        raise ValueError(
            "user_data_dir must be provided. "
            "Use App.get_running_app().user_data_dir in main.py"
        )
    os.makedirs(user_data_dir, exist_ok=True)
    return os.path.join(user_data_dir, name)


# ------------------------------------------------------------
# الشبكة — SSL سليم
# ------------------------------------------------------------
def _fetch(url, timeout=15):
    """HTTPS مع التحقق الكامل من الشهادة (بدون CERT_NONE)."""
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "JuniorDoctor/1.0"})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        return resp.read().decode("utf-8")


def _download_single_file(url):
    try:
        return json.loads(_fetch(url, timeout=20))
    except Exception as e:
        print(f"[updater] Download failed {url}: {e}")
        return None


# ------------------------------------------------------------
# العامل الرئيسي
# ------------------------------------------------------------
def _background_update_worker(user_data_dir, current_version):
    try:
        err_path        = _safe_path(user_data_dir, _ERROR_FILE)
        last_ver_path   = _safe_path(user_data_dir, _LAST_VERSION_FILE)
        data_path       = _safe_path(user_data_dir, _DATA_FILE)
        updates_log_path = _safe_path(user_data_dir, _UPDATES_LOG_FILE)

        # 1) الإصدار المحلي المحفوظ
        local_version = 0.0
        if os.path.exists(last_ver_path):
            try:
                with open(last_ver_path, "r", encoding="utf-8") as f:
                    local_version = float(f.read().strip())
            except Exception:
                pass

        # 2) جلب version.json
        version_info = json.loads(_fetch(VERSION_URL, timeout=10))
        latest_version = float(version_info.get("latest_version", 1.0))
        urls_list = version_info.get("medical_data_urls", [])

        if latest_version <= local_version or not urls_list:
            print("[updater] Already up to date.")
            return

        print(f"[updater] Downloading version {latest_version}...")

        # 3) تحميل كل الملفات بالتوازي
        new_data = {}
        failures = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(_download_single_file, u): u for u in urls_list}
            for fut in concurrent.futures.as_completed(futures):
                url = futures[fut]
                part = fut.result()
                if part is None:
                    failures.append(url)
                    continue
                for spec, subs in part.items():
                    if not isinstance(subs, dict):
                        continue
                    new_data.setdefault(spec, {})
                    for sub, topics in subs.items():
                        if not isinstance(topics, dict):
                            continue
                        new_data[spec].setdefault(sub, {})
                        for topic, content in topics.items():
                            new_data[spec][sub][topic] = content

        # حماية: إذا فشل ملف واحد، ألغِ التحديث كلياً
        if failures:
            raise RuntimeError(f"Failed to download {len(failures)} file(s): {failures}")

        if not new_data:
            print("[updater] No data — aborting.")
            return

        # 4) قراءة البيانات القديمة (للمقارنة فقط)
        old_data = {}
        if os.path.exists(data_path):
            try:
                with open(data_path, "r", encoding="utf-8") as f:
                    old_data = json.load(f) or {}
            except Exception:
                old_data = {}

        # 5) بناء سجل التحديثات (قبل الاستبدال)
        updated_log = []
        for spec, subs in new_data.items():
            for sub, topics in subs.items():
                for topic, content in topics.items():
                    old_content = old_data.get(spec, {}).get(sub, {}).get(topic)
                    if old_content is None:
                        updated_log.append(f"✨ NEW: {topic}")
                    elif old_content != content:
                        updated_log.append(f"🔄 UPDATED: {topic}")
        # المحذوفات (موجودة في القديم وغير موجودة في الجديد)
        for spec, subs in old_data.items():
            for sub, topics in subs.items():
                for topic in topics:
                    if topic not in new_data.get(spec, {}).get(sub, {}):
                        updated_log.append(f"🗑️ REMOVED: {topic}")

        # 6) ★ الاستبدال الكامل — الإصلاح الجوهري ★
        tmp = data_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, data_path)

        # 7) حفظ سجل التحديثات
        if updated_log:
            with open(updates_log_path, "w", encoding="utf-8") as f:
                json.dump({"version": latest_version, "topics": updated_log},
                          f, ensure_ascii=False, indent=2)
        elif os.path.exists(updates_log_path):
            try:
                os.remove(updates_log_path)
            except Exception:
                pass

        # 8) حفظ رقم الإصدار
        with open(last_ver_path, "w", encoding="utf-8") as f:
            f.write(str(latest_version))

        # 9) تنظيف ملف الأخطاء
        if os.path.exists(err_path):
            try:
                os.remove(err_path)
            except Exception:
                pass

        print(f"[updater] Updated to {latest_version} ✔")

    except Exception as e:
        print(f"[updater] Update failed: {e}")
        try:
            p = _safe_path(user_data_dir, _ERROR_FILE)
            with open(p, "w", encoding="utf-8") as f:
                f.write(f"Error: {e}")
        except Exception:
            pass


# ------------------------------------------------------------
# الواجهة العامة
# ------------------------------------------------------------
def check_for_updates(user_data_dir, current_version=1.0):
    t = threading.Thread(target=_background_update_worker,
                         args=(user_data_dir, current_version))
    t.daemon = True
    t.start()


def get_error_message(user_data_dir):
    path = _safe_path(user_data_dir, _ERROR_FILE)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                c = f.read().strip()
            return c or None
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
