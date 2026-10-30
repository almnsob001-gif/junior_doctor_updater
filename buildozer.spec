[app]
title = JuniorMed Hub
package.name = juniormedhub
package.domain = com.almnsob
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,json,txt
icon.filename = %(source.dir)s/icon.png
version = 8.5

requirements = python3==3.10.12,hostpython3==3.10.12,kivy==2.3.0,cython==0.29.34,arabic-reshaper,python-bidi

android.permissions = INTERNET
android.accept_sdk_license = True

android.api = 34
android.minapi = 24
android.ndk_api = 24
android.ndk = 25b
android.archs = arm64-v8a
android.orientation = portrait

# ---- إعدادات النشر على Google Play ----
android.release_artifact = aab
android.private_storage = True
android.allow_backup = False

[buildozer]
warn_on_root = 0
log_level = 2
