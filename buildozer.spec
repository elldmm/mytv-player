[app]
title = MyTVPlayer
package.name = mytvplayer
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
source.exclude_exts = spec
source.exclude_dirs = tests,bin,__pycache__
version = 0.1
requirements = python3,kivy==2.2.1,pillow,pyjnius,android,urllib3,openssl
orientation = portrait
fullscreen = 0
source.include_patterns = assets/*,msyh.ttf
[buildozer]
log_level = 2
warn_on_root = 1
[android]
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.archs = arm64-v8a,armeabi-v7a
android.build_type = debug
android.enable_androidx = True
android.enable_multidex = True
android.use_aapt2 = True
android.add_assets = msyh.ttf
android.presplash_color = #FFFFFF
android.window_softinput_mode = adjustResize
android.ndk_path = ~/.buildozer/android/platform/android-ndk-r25b
android.sdk_path = ~/.buildozer/android/platform/android-sdk
android.logcat_filters = *:S python:D
android.allow_backup = True
