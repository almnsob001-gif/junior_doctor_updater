import os
import json
import urllib.request

def check_for_updates(current_version=1.0):
    """
    يتحقق من وجود تحديثات على GitHub. إذا وجد، يحملها ويحفظها في ذاكرة الهاتف.
    """
    # رابط ملف الإصدار على GitHub (تأكد من تغيير اسم المستخدم إذا لزم الأمر)
    version_url = "https://raw.githubusercontent.com/almnsob001-gif/junior_doctor_updater/main/updates/version.json"
    
    try:
        # 1. محاولة الاتصال بالإنترنت وجلب رقم الإصدار
        req = urllib.request.Request(version_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            version_data = json.loads(response.read().decode())
        
        latest_version = version_data.get("latest_version", 1.0)
        medical_url = version_data.get("medical_data_url")
        
        # إذا كان الإصدار على الإنترنت أحدث من الموجود في التطبيق
        if latest_version > current_version:
            print("New update found! Downloading...")
            
            # 2. تحميل ملف البيانات الجديد
            req_data = urllib.request.Request(medical_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_data, timeout=10) as response:
                new_data = json.loads(response.read().decode())
            
            # 3. حفظ الملف الجديد في ذاكرة الهاتف
            save_path = os.path.join(os.getcwd(), "downloaded_medical.json")
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, ensure_ascii=False, indent=2)
            
            print("Update downloaded and saved successfully.")
            return True
            
    except Exception as e:
        # إذا لم يوجد إنترنت أو حدث خطأ، نتجاهل التحديث بهدوء
        print(f"Update check skipped (offline or error): {e}")
        return False

def load_downloaded_data():
    """
    يقرأ البيانات التي تم تحميلها سابقاً من ذاكرة الهاتف.
    """
    save_path = os.path.join(os.getcwd(), "downloaded_medical.json")
    if os.path.exists(save_path):
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}
