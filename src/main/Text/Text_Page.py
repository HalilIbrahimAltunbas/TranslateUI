# Translate_Page.py - Çeviri Modülü, Ana Menü ile kullanılmak üzere düzenlenmiş
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
import requests.auth
import requests.help
# from kivymd.uix.snackbar import Snackbar
# from kivymd.uix.snackbar.snackbar import MDSnackbar,MDLabel 
from components.SnackBar import SnackBar
import requests
from Registiration import AuthClient

from Service import HttpService 

from config import config_reader

# Çeviri App KV
TRANSLATE_KV = '''
MDScreen:
    name: "translate_app"
    
    MDBoxLayout:
        orientation: "vertical"
        
        MDTopAppBar:
            title: "Çeviri Uygulaması"
            left_action_items: [["arrow-left", lambda x: app.back_to_menu()]]
            right_action_items: [["cog", lambda x: app.translate_app.show_settings_dialog()]]
            elevation: 4
        
        MDBoxLayout:
            orientation: 'vertical'
            spacing: dp(20)
            padding: dp(20)

            MDTextField:
                id: input_text
                hint_text: "Çevrilecek metni gir"
                mode: "rectangle"
                size_hint_x: 0.9
                pos_hint: {"center_x": 0.5}
                multiline: True

            MDBoxLayout:
                size_hint_y: None
                height: "56dp"
                spacing: "10dp"
                padding: [0, 10, 0, 10]
                pos_hint: {"center_x": 0.5}
                
                MDRaisedButton:
                    text: "Çevir"
                    size_hint_x: 0.5
                    pos_hint: {"center_x": 0.5}
                    on_release: app.translate_app.translate_text()

            MDCard:
                padding: "16dp"
                size_hint_y: None
                height: "150dp"
                elevation: 4
                radius: [12]
                
                MDLabel:
                    id: output_text
                    text: "Çeviri sonucu burada görünecek"
                    halign: "center"
                    theme_text_color: "Secondary"
'''


class TranslateApp:
    def __init__(self):
        self._url = config_reader.get_config_value('route')#"127.0.0.1"  # Varsayılan olarak localhost
        self.app = MDApp.get_running_app()
        self.root = None
        self.settings_dialog = None
        
    def build(self):
        self.root = Builder.load_string(TRANSLATE_KV)
        
        # Ana uygulamada kullanılabilmek için kendimize bir referans koy
        self.app.translate_app = self
        
        return self.root

      

    def translate_text(self):
        """Metni çevirir"""
        try:
            input_text = self.root.ids.input_text.text
            
            if not input_text.strip():
                self.root.ids.output_text.text = "Lütfen çevrilecek metin girin."
                return
                
            # Burada gerçek API ile çeviri yapabilirsiniz
            # Örnek olarak, gerçek API'ye istek gönderme kodu:
            url = f"http://{self._url}:5000/translate-text"

            response = HttpService.HttpService().post(url,{"json":{"text": input_text}})
            # response = requests.post(url, headers = {"Authorization": f"Bearer {AuthClient.auth_client.get_token()}"}  ,json={"text": input_text})
            
            if response.ok:
                translated_text = response.json().get('text', 'Çeviri yapılamadı')
            else:
                translated_text = f"Hata: {response.json().get('error', 'Bilinmeyen hata')}"
            
            # Şimdilik basit bir simülasyon
            # translated_text = f'"{translated_text}" çevirildi!'
            
            self.root.ids.output_text.text = translated_text
            
        except Exception as e:
            self.root.ids.output_text.text = f"Çeviri hatası: {e}"

    
            
    def show_settings_dialog(self):
        from components.SettingsModal import Dialog
        Dialog.show_settings_dialog(self)
       