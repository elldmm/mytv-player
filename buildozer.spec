[app]
title = MyTVPlayer
package.name = mytv
package.domain = org.tvapp
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf
version = 1.0
requirements = python3,kivy==2.2.1,pillow,requests,urllib3
orientation = portrait
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = True
fullscreen = 0
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
p4a.index_url = https://mirrors.aliyun.com/pypi/simple/
build_dir = ./.buildozer
bin_dir = ./bin
