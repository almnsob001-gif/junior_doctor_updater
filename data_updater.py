import os
import json
import urllib.request

def check_for_updates(data_dir, current_version=1.0):
    version_url = "https://raw.githubusercontent.com/almnsob001-gif/junior_doctor_updater/main/updates/version.json"
    save_path = os.path.join(data_dir, "downloaded_medical.json")
    
    try:
        # 1. جلب رقم الإصدار
        req = urllib.request.Request(version_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            version_data = json.loads(response.read().decode())
        
        latest_version = version_data.get("latest_version", 1.0)
        medical_url = version_data.get("medical_data_url")
        
        # 2. إذا كان هناك إصدار جديد، قم بتحميله
        if latest_version > current_version:
            req_data = urllib.request.Request(medical_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_data, timeout=10) as response:
                new_data = json.loads(response.read().decode())
            
            # 3. الحفظ في المسار الصحيح (data_dir)
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, ensure_ascii=False, indent=2)
            print("Update downloaded successfully.")
            
    except Exception as e:
        print(f"Update check skipped: {e}")

def load_downloaded_data(data_dir):
    save_path = os.path.join(data_dir, "downloaded_medical.json")
    if os.path.exists(save_path):
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}
