from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.utils import platform
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.popup import Popup
from kivy.core.text import LabelBase
import json
import os
import time
import urllib.request
import ssl

# 适配Android平台
IS_ANDROID = platform == 'android'

# 忽略SSL证书验证 (适配安卓/网络环境)
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except Exception as e:
    print(f"SSL context fix failed: {e}")

# 注册中文字体 (优先加载打包的字体文件)
try:
    if IS_ANDROID:
        # Android下字体路径适配
        font_path = os.path.join(os.environ.get('ANDROID_APP_PATH', '.'), 'msyh.ttf')
    else:
        font_path = 'msyh.ttf'
    
    if os.path.exists(font_path):
        LabelBase.register(name='MyFont', fn_regular=font_path)
    else:
        LabelBase.register(name='MyFont', fn_regular='DroidSans')
except Exception as e:
    print(f"Font register failed: {e}")
    LabelBase.register(name='MyFont', fn_regular='DroidSans')

# 默认频道列表
DEFAULT_CHANNELS = {
    'CCTV-1 综合': 'https://www.yangshipin.cn/tv/home?pid=600001859',
    'CCTV-2 财经': 'https://www.yangshipin.cn/tv/home?pid=600001800',
    'CCTV-3 综艺': 'https://www.yangshipin.cn/tv/home?pid=600001801',
    'CCTV-4 中文国际': 'https://www.yangshipin.cn/tv/home?pid=600001814',
    'CCTV-5 体育': 'https://www.yangshipin.cn/tv/home?pid=600001818',
    'CCTV-5+ 体育赛事': 'https://www.yangshipin.cn/tv/home?pid=600001817',
    'CCTV-6 电影': 'https://www.yangshipin.cn/tv/home?pid=600001802',
    'CCTV-7 国防军事': 'https://www.yangshipin.cn/tv/home?pid=600001803',
    'CCTV-8 电视剧': 'https://www.yangshipin.cn/tv/home?pid=600001804',
    'CCTV-9 纪录': 'https://www.yangshipin.cn/tv/home?pid=600001805',
    'CCTV-10 科教': 'https://www.yangshipin.cn/tv/home?pid=600001806',
    'CCTV-11 戏曲': 'https://www.yangshipin.cn/tv/home?pid=600001807',
    'CCTV-12 社会与法': 'https://www.yangshipin.cn/tv/home?pid=600001808',
    'CCTV-13 新闻': 'https://www.yangshipin.cn/tv/home?pid=600001809',
    'CCTV-14 少儿': 'https://www.yangshipin.cn/tv/home?pid=600001810',
    'CCTV-15 音乐': 'https://www.yangshipin.cn/tv/home?pid=600001811',
    'CCTV-17 农业农村': 'https://www.yangshipin.cn/tv/home?pid=600001812',
    'CCTV-4K 超高清': 'https://www.yangshipin.cn/tv/home?pid=600002264',
    '北京卫视': 'https://www.yangshipin.cn/tv/home?pid=600002309',
    '湖南卫视': 'https://www.yangshipin.cn/tv/home?pid=600002475',
    '浙江卫视': 'https://www.yangshipin.cn/tv/home?pid=600002520',
    '东方卫视': 'https://www.yangshipin.cn/tv/home?pid=600002483',
    '江苏卫视': 'https://www.yangshipin.cn/tv/home?pid=600002521',
    '广东卫视': 'https://www.yangshipin.cn/tv/home?pid=600002485',
}


class TVPlayerApp(App):
    current_url = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_dir = self.get_data_dir()
        self.channels_file = os.path.join(self.data_dir, 'channels.json')
        self.history_file = os.path.join(self.data_dir, 'history.json')
        self.channels = self.load_channels()
        self.history = self.load_history()
        self.is_playing = False
    
    def get_data_dir(self):
        """适配Android/iOS/桌面端的本地数据存储路径"""
        if IS_ANDROID:
            try:
                from android.storage import app_storage_path
                path = app_storage_path()
            except ImportError:
                # 备用路径
                path = os.path.join(os.getcwd(), 'data')
        else:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        
        # 确保目录存在
        os.makedirs(path, exist_ok=True)
        return path
    
    def load_channels(self):
        """加载频道列表 (优先本地保存，无则用默认)"""
        try:
            if os.path.exists(self.channels_file):
                with open(self.channels_file, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    # 合并默认频道和本地保存的频道 (本地覆盖默认)
                    merged = DEFAULT_CHANNELS.copy()
                    merged.update(saved)
                    return merged
        except Exception as e:
            print(f"Load channels failed: {e}")
        return DEFAULT_CHANNELS.copy()
    
    def save_channels(self):
        """保存频道列表到本地"""
        try:
            with open(self.channels_file, 'w', encoding='utf-8') as f:
                json.dump(self.channels, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Save channels failed: {e}")
    
    def load_history(self):
        """加载播放历史"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Load history failed: {e}")
        return []
    
    def save_history(self):
        """保存播放历史 (最多保留20条)"""
        try:
            # 只保留最近20条
            history = self.history[-20:] if len(self.history) > 20 else self.history
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Save history failed: {e}")
    
    def add_to_history(self, name, url):
        """添加播放记录"""
        entry = {
            'name': name,
            'url': url,
            'time': time.strftime('%Y-%m-%d %H:%M')
        }
        # 去重 (同一频道只保留最新记录)
        self.history = [h for h in self.history if h['name'] != name]
        self.history.append(entry)
        self.save_history()
    
    def build(self):
        """构建UI"""
        # 设置窗口背景
        Window.clearcolor = (0.08, 0.08, 0.12, 1)
        # 绑定返回键
        Window.bind(on_keyboard=self.on_key)
        
        # 根布局
        self.root_layout = BoxLayout(orientation='vertical', padding=12, spacing=10)
        self.build_main_ui()
        return self.root_layout
    
    def build_main_ui(self):
        """构建主界面"""
        self.root_layout.clear_widgets()
        self.is_playing = False
        
        # 标题栏
        header = BoxLayout(size_hint_y=None, height=55, spacing=10)
        header.add_widget(Label(
            text='📺 我的电视',
            font_size='24sp',
            color=(0.3, 0.7, 1, 1),
            bold=True,
            font_name='MyFont'
        ))
        self.root_layout.add_widget(header)
        
        # 功能按钮栏
        func_bar = BoxLayout(size_hint_y=None, height=45, spacing=8)
        func_bar.add_widget(Button(
            text='🔄 更新源',
            font_size='12sp',
            background_color=(0.3, 0.5, 0.4, 1),
            on_press=self.check_update,
            font_name='MyFont'
        ))
        func_bar.add_widget(Button(
            text='📜 历史',
            font_size='12sp',
            background_color=(0.4, 0.4, 0.6, 1),
            on_press=self.show_history,
            font_name='MyFont'
        ))
        func_bar.add_widget(Button(
            text='ℹ️ 关于',
            font_size='12sp',
            background_color=(0.5, 0.5, 0.5, 1),
            on_press=self.show_about,
            font_name='MyFont'
        ))
        self.root_layout.add_widget(func_bar)
        
        # 状态提示
        self.status_label = Label(
            text=f'共 {len(self.channels)} 个频道 | 历史 {len(self.history)} 条',
            font_size='12sp',
            size_hint_y=None,
            height=30,
            color=(0.5, 0.8, 0.6, 1),
            font_name='MyFont'
        )
        self.root_layout.add_widget(self.status_label)
        
        # 频道列表 (滚动布局)
        scroll = ScrollView()
        # 根据屏幕宽度适配列数
        cols = 3 if Window.width > 600 else 2
        grid = GridLayout(cols=cols, spacing=10, size_hint_y=None, padding=8)
        grid.bind(minimum_height=grid.setter('height'))
        
        # 添加频道按钮
        for name, url in sorted(self.channels.items()):
            btn = Button(
                text=name,
                size_hint_y=None,
                height=70,
                font_size='15sp',
                background_color=(0.15, 0.28, 0.48, 1),
                background_normal='',
                color=(0.95, 0.95, 0.95, 1),
                font_name='MyFont'
            )
            btn.bind(on_press=lambda x, n=name, u=url: self.play_channel(n, u))
            grid.add_widget(btn)
        
        scroll.add_widget(grid)
        self.root_layout.add_widget(scroll)
        
        # 底部提示
        self.root_layout.add_widget(Label(
            text='点击频道打开央视频官网播放',
            font_size='11sp',
            size_hint_y=None,
            height=35,
            color=(0.5, 0.6, 0.7, 1),
            font_name='MyFont'
        ))
    
    def play_channel(self, name, url):
        """播放指定频道"""
        self.current_url = url
        self.is_playing = True
        self.add_to_history(name, url)
        self.status_label.text = f'正在播放: {name}'
        
        if IS_ANDROID:
            self.open_android_browser(url)
        else:
            # 桌面端用默认浏览器打开
            import webbrowser
            webbrowser.open(url)
    
    def open_android_browser(self, url):
        """Android端打开系统浏览器"""
        try:
            from jnius import autoclass
            from android.runnable import run_on_ui_thread
            
            @run_on_ui_thread
            def open_browser():
                try:
                    Intent = autoclass('android.content.Intent')
                    Uri = autoclass('android.net.Uri')
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                    
                    intent = Intent(Intent.ACTION_VIEW)
                    intent.setData(Uri.parse(url))
                    # 避免浏览器选择弹窗 (可选)
                    intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                    
                    activity = PythonActivity.mActivity
                    activity.startActivity(intent)
                except Exception as e:
                    print(f"Open browser failed: {e}")
                    # 备用方案：用webview或其他方式
                    import webbrowser
                    webbrowser.open(url)
            
            open_browser()
        except Exception as e:
            print(f"Android browser init failed: {e}")
            import webbrowser
            webbrowser.open(url)
    
    def check_update(self, instance):
        """检查频道源更新"""
        self.status_label.text = '正在检查更新...'
        self.status_label.color = (1, 0.8, 0.3, 1)
        # 异步执行更新 (避免UI卡顿)
        Clock.schedule_once(self.do_update, 0.5)
    
    def do_update(self, dt):
        """执行频道源更新"""
        try:
            # 从公开源获取频道列表
            url = 'https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            req = urllib.request.Request(url, headers=headers, timeout=15)
            
            with urllib.request.urlopen(req) as response:
                content = response.read().decode('utf-8', errors='ignore')
            
            # 解析M3U格式
            new_channels = self.parse_m3u(content)
            
            if new_channels:
                # 计算新增数量
                added = sum(1 for name in new_channels if name not in self.channels)
                # 更新频道列表
                self.channels.update(new_channels)
                self.save_channels()
                # 刷新UI
                self.build_main_ui()
                self.status_label.text = f'更新完成: 新增 {added} 个频道'
                self.status_label.color = (0.5, 1, 0.5, 1)
            else:
                self.status_label.text = '暂无新频道'
                self.status_label.color = (0.8, 0.8, 0.5, 1)
        except Exception as e:
            self.status_label.text = f'更新失败: {str(e)[:30]}'
            self.status_label.color = (1, 0.5, 0.5, 1)
    
    def parse_m3u(self, content):
        """解析M3U格式的频道列表"""
        channels = {}
        lines = content.split('\n')
        current_name = None
        
        for line in lines:
            line = line.strip()
            # 提取频道名称
            if line.startswith('#EXTINF:'):
                if ',' in line:
                    current_name = line.split(',')[-1].strip()
                else:
                    current_name = None
            # 提取播放链接
            elif line.startswith('http') and current_name:
                # 只保留央视频相关链接
                if 'yangshipin' in line or 'cctv' in current_name.lower():
                    channels[current_name] = line.strip()
                current_name = None
        
        return channels
    
    def show_history(self, instance):
        """显示播放历史弹窗"""
        content = BoxLayout(orientation='vertical', padding=10)
        
        if not self.history:
            content.add_widget(Label(
                text='暂无播放历史',
                font_name='MyFont',
                font_size='13sp'
            ))
        else:
            # 历史记录滚动布局
            scroll = ScrollView()
            grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
            grid.bind(minimum_height=grid.setter('height'))
            
            # 倒序显示 (最新的在最上面)
            for entry in reversed(self.history):
                btn = Button(
                    text=f"{entry['name']}\n{entry['time']}",
                    size_hint_y=None,
                    height=60,
                    font_size='12sp',
                    halign='center',
                    font_name='MyFont'
                )
                btn.bind(on_press=lambda x, e=entry: self.play_channel(e['name'], e['url']))
                grid.add_widget(btn)
            
            scroll.add_widget(grid)
            content.add_widget(scroll)
        
        # 清空历史按钮
        content.add_widget(Button(
            text='清空历史',
            size_hint_y=None,
            height=45,
            background_color=(0.7, 0.3, 0.3, 1),
            on_press=self.clear_history,
            font_name='MyFont'
        ))
        
        # 弹出窗口
        Popup(
            title='播放历史',
            content=content,
            size_hint=(0.85, 0.7)
        ).open()
    
    def clear_history(self, instance):
        """清空播放历史"""
        self.history = []
        self.save_history()
        self.status_label.text = '历史已清空'
        # 关闭弹窗并刷新UI
        for widget in Window.children:
            if isinstance(widget, Popup):
                widget.dismiss()
        self.build_main_ui()
    
    def show_about(self, instance):
        """显示关于弹窗"""
        content = Label(
            text='网络电视播放器 v1.0\n\n支持 Win11 WSA 和安卓平板\n基于央视频官网播放\n\n数据保存在本地，无隐私风险',
            font_size='13sp',
            halign='center',
            font_name='MyFont'
        )
        Popup(
            title='关于',
            content=content,
            size_hint=(0.8, 0.6)
        ).open()
    
    def on_key(self, window, key, scancode, codepoint, modifier):
        """处理键盘/返回键事件"""
        # Android返回键/ESC键
        if key in (27, 1001, 4):
            # 关闭弹窗
            for widget in Window.children:
                if isinstance(widget, Popup):
                    widget.dismiss()
                    return True
            # 播放中返回主界面
            if self.is_playing:
                self.build_main_ui()
                return True
            # 退出应用
            else:
                self.stop()
                return True
        return False
    
    def on_pause(self):
        """Android暂停处理"""
        return True


if __name__ == '__main__':
    # 桌面端默认窗口大小
    if not IS_ANDROID:
        Window.size = (480, 800)
    # 启动应用
    TVPlayerApp().run()
