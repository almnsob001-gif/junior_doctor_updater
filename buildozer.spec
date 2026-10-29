[app]
title = Junior Doctor
package.name = juniordoctor_v85
package.domain = org.juniordoctor
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,json,txt
icon.filename = %(source.dir)s/icon.png
version = 8.5

requirements = python3==3.10.12,hostpython3==3.10.12,kivy==2.3.0,cython==0.29.34

android.permissions = INTERNET,WAKE_LOCK
android.accept_sdk_license = True
android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.orientation = portrait

[buildozer]
warn_on_root = 0
