[app]
title = Junior Doctor
package.name = juniordoc
package.domain = com.almnsob.juniormedhub
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,json,txt
icon.filename = %(source.dir)s/icon.png
version = 8.6

requirements = python3==3.10.12,hostpython3==3.10.12,kivy==2.3.0,cython==0.29.34,arabic-reshaper,python-bidi,certifi

android.permissions = INTERNET,WAKE_LOCK
android.accept_sdk_license = True

android.api = 34
android.minapi = 24
android.ndk = 25b

android.archs = arm64-v8a
android.orientation = portrait

android.private_storage = True
android.allow_backup = False

# ==========================================
# إعدادات التوقيع للنشر (Google Play AAB)
# ==========================================
android.release_artifact = aab
android.keystore_path = release.keystore
android.keystore_alias = %(keystore_alias)s
android.keystore_passwd = %(keystore_password)s
android.keystore_alias_passwd = %(keystore_password)s

[buildozer]
warn_on_root = 0
log_level = 2
