from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.utils import platform
from kivy.properties import StringProperty
from kivy.uix.popup import Popup
from kivy.core.text import LabelBase
from kivy.uix.widget import Widget
import json
import os
import time

IS_ANDROID = platform == 'android'

try:
    if os.path.exists('msyh.ttf'):
        LabelBase.register(name='MyFont', fn_regular='msyh.ttf')
    else:
        LabelBase.register(name='MyFont', fn_regular='Roboto')
except:
    LabelBase.register(name='MyFont', fn_regular='Roboto')

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
        self.webview = None
    
    def get_data_dir(self):
        if IS_ANDROID:
            try:
                from android.storage import app_storage_path
                path = app_storage_path()
            except:
                path = os.path.join(os.getcwd(), 'data')
        else:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        return path
    
    def load_channels(self):
        try:
            if os.path.exists(self.channels_file):
                with open(self.channels_file, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    merged = DEFAULT_CHANNELS.copy()
                    merged.update(saved)
                    return merged
        except:
            pass
        return DEFAULT_CHANNELS.copy()
    
    def save_channels(self):
        try:
            with open(self.channels_file, 'w', encoding='utf-8') as f:
                json.dump(self.channels, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def load_history(self):
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def save_history(self):
        try:
            history = self.history[-20:] if len(self.history) > 20 else self.history
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def add_to_history(self, name, url):
        entry = {'name': name, 'url': url, 'time': time.strftime('%Y-%m-%d %H:%M')}
        self.history = [h for h in self.history if h['name'] != name]
        self.history.append(entry)
        self.save_history()
    
    def build(self):
        Window.clearcolor = (0.08, 0.08, 0.12, 1)
        Window.bind(on_keyboard=self.on_key)
        self.root_layout = BoxLayout(orientation='vertical', padding=12, spacing=10)
        self.build_main_ui()
        return self.root_layout
    
    def build_main_ui(self):
        self.root_layout.clear_widgets()
        self.webview = None
        
        header = BoxLayout(size_hint_y=None, height=55, spacing=10)
        header.add_widget(Label(
            text='📺 我的电视', 
            font_size='24sp', 
            color=(0.3, 0.7, 1, 1), 
            bold=True, 
            font_name='MyFont'
        ))
        self.root_layout.add_widget(header)
        
        func_bar = BoxLayout(size_hint_y=None, height=45, spacing=8)
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
        
        self.status_label = Label(
            text=f'共 {len(self.channels)} 个频道 | 历史 {len(self.history)} 条', 
            font_size='12sp', 
            size_hint_y=None, 
            height=30, 
            color=(0.5, 0.8, 0.6, 1), 
            font_name='MyFont'
        )
        self.root_layout.add_widget(self.status_label)
        
        scroll = ScrollView()
        cols = 3 if Window.width > 600 else 2
        grid = GridLayout(cols=cols, spacing=10, size_hint_y=None, padding=8)
        grid.bind(minimum_height=grid.setter('height'))
        
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
        
        self.root_layout.add_widget(Label(
            text='点击频道打开播放', 
            font_size='11sp', 
            size_hint_y=None, 
            height=35, 
            color=(0.5, 0.6, 0.7, 1), 
            font_name='MyFont'
        ))
    
    def play_channel(self, name, url):
        self.current_url = url
        self.add_to_history(name, url)
        self.status_label.text = f'正在播放: {name}'
        
        if IS_ANDROID:
            self.show_android_webview(url)
        else:
            import webbrowser
            webbrowser.open(url)
    
    def show_android_webview(self, url):
        try:
            from jnius import autoclass, cast
            from android.runnable import run_on_ui_thread
            
            @run_on_ui_thread
            def create_webview():
                try:
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                    WebView = autoclass('android.webkit.WebView')
                    WebSettings = autoclass('android.webkit.WebSettings')
                    ViewGroup = autoclass('android.view.ViewGroup')
                    LayoutParams = autoclass('android.view.ViewGroup$LayoutParams')
                    LinearLayout = autoclass('android.widget.LinearLayout')
                    Button = autoclass('android.widget.Button')
                    Gravity = autoclass('android.view.Gravity')
                    Color = autoclass('android.graphics.Color')
                    WebViewClient = autoclass('android.webkit.WebViewClient')
                    
                    activity = PythonActivity.mActivity
                    
                    if not activity:
                        return
                    
                    self.webview_layout = LinearLayout(activity)
                    self.webview_layout.setOrientation(LinearLayout.VERTICAL)
                    self.webview_layout.setBackgroundColor(Color.parseColor('#14141f'))
                    
                    top_bar = LinearLayout(activity)
                    top_bar.setOrientation(LinearLayout.HORIZONTAL)
                    top_bar.setBackgroundColor(Color.parseColor('#1f1f2e'))
                    top_bar_params = LinearLayout.LayoutParams(
                        LayoutParams.MATCH_PARENT,
                        int(120 * activity.getResources().getDisplayMetrics().density)
                    )
                    top_bar.setLayoutParams(top_bar_params)
                    
                    back_btn = Button(activity)
                    back_btn.setText('← 返回频道列表')
                    back_btn.setTextColor(Color.WHITE)
                    back_btn.setBackgroundColor(Color.parseColor('#2d4a6f'))
                    back_btn_params = LinearLayout.LayoutParams(
                        LayoutParams.WRAP_CONTENT,
                        LayoutParams.MATCH_PARENT
                    )
                    back_btn_params.weight = 1.0
                    back_btn.setLayoutParams(back_btn_params)
                    
                    class BackClickListener(autoclass('android.view.View$OnClickListener')):
                        def onClick(self, view):
                            self.close_webview()
                    
                    back_btn.setOnClickListener(BackClickListener())
                    top_bar.addView(back_btn)
                    
                    self.webview_layout.addView(top_bar)
                    
                    self.webview = WebView(activity)
                    webview_params = LinearLayout.LayoutParams(
                        LayoutParams.MATCH_PARENT,
                        LayoutParams.MATCH_PARENT
                    )
                    webview_params.weight = 1.0
                    self.webview.setLayoutParams(webview_params)
                    
                    settings = self.webview.getSettings()
                    settings.setJavaScriptEnabled(True)
                    settings.setDomStorageEnabled(True)
                    settings.setUserAgentString('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0')
                    
                    self.webview.setWebViewClient(WebViewClient())
                    self.webview.loadUrl(url)
                    
                    self.webview_layout.addView(self.webview)
                    
                    content_view = activity.findViewById(autoclass('android.R$id').content)
                    if content_view:
                        self.original_content = content_view.getChildAt(0)
                        content_view.removeAllViews()
                        content_view.addView(self.webview_layout)
                    
                except Exception as e:
                    print(f"WebView error: {e}")
                    self.open_external_browser(url)
            
            create_webview()
            
        except Exception as e:
            print(f"JNI error: {e}")
            self.open_external_browser(url)
    
    def close_webview(self):
        try:
            from jnius import autoclass
            from android.runnable import run_on_ui_thread
            
            @run_on_ui_thread
            def do_close():
                try:
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                    activity = PythonActivity.mActivity
                    
                    if self.webview:
                        self.webview.stopLoading()
                        self.webview.loadUrl('about:blank')
                        self.webview.clearHistory()
                        self.webview = None
                    
                    content_view = activity.findViewById(autoclass('android.R$id').content)
                    if content_view and hasattr(self, 'original_content'):
                        content_view.removeAllViews()
                        content_view.addView(self.original_content)
                    
                    self.webview_layout = None
                    self.status_label.text = f'共 {len(self.channels)} 个频道 | 历史 {len(self.history)} 条'
                    
                except Exception as e:
                    print(f"Close error: {e}")
            
            do_close()
            
        except Exception as e:
            print(f"Close JNI error: {e}")
            self.build_main_ui()
    
    def open_external_browser(self, url):
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
                    activity = PythonActivity.mActivity
                    activity.startActivity(intent)
                except Exception as e:
                    print(f"Browser error: {e}")
            
            open_browser()
            
        except Exception as e:
            print(f"External browser error: {e}")
    
    def show_history(self, instance):
        content = BoxLayout(orientation='vertical', padding=10)
        
        if not self.history:
            content.add_widget(Label(text='暂无播放历史', font_name='MyFont', font_size='13sp'))
        else:
            scroll = ScrollView()
            grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
            grid.bind(minimum_height=grid.setter('height'))
            
            for entry in reversed(self.history):
                btn = Button(
                    text=f"{entry['name']}\n{entry['time']}", 
                    size_hint_y=None, 
                    height=60, 
                    font_size='12sp', 
                    halign='center', 
                    font_name='MyFont'
                )
                btn.bind(on_press=lambda x, e=entry: [self.play_channel(e['name'], e['url']), popup.dismiss()])
                grid.add_widget(btn)
            
            scroll.add_widget(grid)
            content.add_widget(scroll)
        
        content.add_widget(Button(
            text='清空历史', 
            size_hint_y=None, 
            height=45, 
            background_color=(0.7, 0.3, 0.3, 1), 
            on_press=self.clear_history, 
            font_name='MyFont'
        ))
        
        popup = Popup(title='播放历史', content=content, size_hint=(0.85, 0.7))
        popup.open()
    
    def clear_history(self, instance):
        self.history = []
        self.save_history()
        self.status_label.text = '历史已清空'
    
    def show_about(self, instance):
        content = Label(
            text='网络电视播放器 v1.0\n\n支持 Win11 WSA 和安卓平板\n基于央视频官网播放\n\n数据保存在本地，无隐私风险', 
            font_size='13sp', 
            halign='center', 
            font_name='MyFont'
        )
        Popup(title='关于', content=content, size_hint=(0.8, 0.6)).open()
    
    def on_key(self, window, key, scancode, codepoint, modifier):
        if key in (27, 1001, 4):
            if self.webview:
                self.close_webview()
                return True
            for widget in Window.children:
                if isinstance(widget, Popup):
                    widget.dismiss()
                    return True
            return False
        return False
    
    def on_pause(self):
        return True


if __name__ == '__main__':
    if not IS_ANDROID:
        Window.size = (480, 800)
    TVPlayerApp().run()
