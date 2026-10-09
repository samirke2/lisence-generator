[app]
title = License Generator
package.name = licensegenerator
package.domain = org.samir
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,xml
source.exclude_dirs = bin, .buildozer, venv, __pycache__, .git
source.exclude_patterns = private_key.pem, *.keystore, last_license.txt
version = 1.0.0

icon.filename = %(source.dir)s/logo.png
presplash.filename = %(source.dir)s/presplash.png
presplash.color = #020B1E

# المتطلبات (نفس النسخ المستقرة المستخدمة في Showroom Manager)
# - sqlite3 : ضروري وإلا يفشل import sqlite3 على الهاتف
# - cryptography : للتوقيع RSA (نفس الإصدار الذي عمل في التطبيق الرئيسي)
# - pyjnius : للوصول إلى Android Intent (مشاركة WhatsApp)
requirements = python3,hostpython3,kivy==2.3.0,kivymd==1.1.1,sqlite3,pillow,cryptography,pyjnius

orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 24
android.ndk = 25b
android.ndk_api = 24
android.archs = arm64-v8a
android.accept_sdk_license = True

# صلاحيات أساسية فقط (لا نحتاج تخزين في مولّد الأكواد)
android.permissions = INTERNET

android.allow_backup = False
android.logcat_filters = *:S python:D

# ⭐ هذا هو السر: نسخة p4a المستقرة (نفسها في Showroom Manager)
p4a.branch = v2024.01.21

[buildozer]
log_level = 2
warn_on_root = 1