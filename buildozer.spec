[app]
# 应用基本信息
title = MyTVPlayer
package.name = mytvplayer
package.domain = org.mytv
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf  # 包含字体文件
source.exclude_exts = spec
source.exclude_dirs = venv,.git,.gradle
version = 1.0

# Android 版本适配（和 GitHub Action 里的 SDK 版本对齐）
android.api = 33
android.ndk = 25b
android.ndk_path = ~/.buildozer/android/platform/android-ndk-r25b
android.sdk_path = ~/.buildozer/android/platform/android-sdk
android.build_tool = 33.0.0
android.arch = arm64-v8a,x86_64  # 支持主流架构

# 关键：添加 Android 权限（打开浏览器/网络请求必须）
android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACTION_VIEW
# 把字体文件加入 Android 资源目录
android.add_android_assets = msyh.ttf

# 依赖（固定版本避免兼容问题）
requirements = python3,kivy==2.2.1,pyjnius,urllib3,android

[buildozer]
log_level = 2  # 输出详细日志便于调试
warn_on_root = 1
