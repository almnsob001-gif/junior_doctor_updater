import os
import json
import urllib.request
import ssl

def check_for_updates(data_dir, current_version=1.0):
    version_url = "https://raw.githubusercontent.com/almnsob001-gif/junior_doctor_updater/main/updates/version.json"
    save_path = os.path.join(data_dir, "downloaded_medical.json")
    error_path = os.path.join(data_dir, "update_error.txt")
    
    # تجاوز مشاكل شهادات الأمان
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        req = urllib.request.Request(version_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
            version_data = json.loads(response.read().decode())
        
        latest_version = version_data.get("latest_version", 1.0)
        medical_url = version_data.get("medical_data_url")
        
        if latest_version > current_version:
            req_data = urllib.request.Request(medical_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_data, timeout=15, context=ctx) as response:
                new_data = json.loads(response.read().decode())
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, ensure_ascii=False, indent=2)
            
            if os.path.exists(error_path): os.remove(error_path)
            
    except Exception as e:
        with open(error_path, 'w', encoding='utf-8') as f:
            f.write(f"ERROR: {str(e)}")

def load_downloaded_data(data_dir):
    save_path = os.path.join(data_dir, "downloaded_medical.json")
    if os.path.exists(save_path):
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def get_error_message(data_dir):
    error_path = os.path.join(data_dir, "update_error.txt")
    if os.path.exists(error_path):
        with open(error_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""
