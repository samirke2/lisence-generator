[app]
title = License Generator
package.name = licensegen
package.domain = org.samir

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
source.exclude_dirs = bin, .buildozer, venv, __pycache__

version = 1.0.0

requirements = python3==3.11.5,kivy==2.3.0,kivymd==1.1.1,pillow,pyjnius,android

orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/logo.png

presplash.filename = %(source.dir)s/presplash.png

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES

android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

android.archs = arm64-v8a

android.allow_backup = False
android.debug_artifact = apk

[buildozer]
log_level = 2
warn_on_root = 1