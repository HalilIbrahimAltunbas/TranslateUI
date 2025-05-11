from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivy.lang import Builder
from components.SnackBar import SnackBar
import requests
import threading

from config import config_reader

Password_Kv='''
MDScreen:
    name: "forgot_password_screen"
    
    MDBoxLayout:
        orientation: "vertical"
        
        MDTopAppBar:
            title: app.lang_conv.get_value('forgot_password')
            elevation: 4
            left_action_items: [["arrow-left", lambda x: app.password_app.goto_signin()]]
            
        MDBoxLayout:
            orientation: "vertical"
            padding: "24dp"
            spacing: "24dp"
            
            Widget:
                size_hint_y: 0.2
            
            MDLabel:
                text: app.lang_conv.get_value('password_reset')
                halign: "center"
                font_style: "H5"
                adaptive_height: True
                
            MDLabel:
                text: app.lang_conv.get_value('password_inform')
                halign: "center"
                theme_text_color: "Secondary"
                adaptive_height: True
            
            MDCard:
                orientation: "vertical"
                padding: "16dp"
                spacing: "16dp"
                elevation: 4
                radius: [12]
                size_hint: None, None
                size: "280dp", "200dp"
                pos_hint: {"center_x": .5}
                
                MDTextField:
                    id: reset_email_field
                    hint_text: app.lang_conv.get_value('mail')
                    helper_text: app.lang_conv.get_value('password_mail_text')
                    helper_text_mode: "on_focus"
                    icon_right: "email"
                    mode: "rectangle"
                
                MDRaisedButton:
                    text: app.lang_conv.get_value('password_send_link_button')
                    pos_hint: {"center_x": .5}
                    on_release: app.password_app.reset_password()
'''

class PasswordScreen(MDScreen):
    """Authentication screens container"""
    pass

class Password:
    def __init__(self):
        self._url = config_reader.get_config_value('route')#"127.0.0.1"  # Varsayılan olarak localhost
        self.app = MDApp.get_running_app()
        self.root = None
        self.settings_dialog = None
        self.current_screen = "password_screen"
        
    def build(self):
        self.root = Builder.load_string(Password_Kv)
        
        # Ana uygulamada kullanılabilmek için kendimize bir referans koy
        self.app.password_app = self
        
        return self.root
    
    def goto_signin(self):
        """Sign In ekranına geçiş yapar"""
        
        
        # self.app.screen_manager.current = "signin_screen"
        # self.current_screen = "signin_screen"
        from Registiration.SignIn import SignIn
        self.app.load_screen(SignIn, 'signin_screen')
    
    def reset_password(self):
        """Şifre sıfırlama bağlantısı gönderir"""
        try:
            print(self.root.ids)
            email = self.root.ids.reset_email_field.text
            
            if not email.strip():
                SnackBar.callSnackBar(text=self.app.lang_conv.get_value('password_mail_text'), bg_color=self.app.theme_cls.error_color)
                return
            
            # API'ye istek gönder (gerçek implementasyon için)
            # url = f"http://{self._url}:5000/auth/reset-password"
            # response = requests.post(url, json={"email": email})
            
            # Şimdilik basit bir simülasyon
            SnackBar.callSnackBar(text=f"{self.app.lang_conv.get_value('password_reset_inform')}: {email} ", bg_color=self.app.theme_cls.primary_color)
            # Giriş ekranına yönlendir
            self.goto_signin()
                
        except Exception as e:
            SnackBar.callSnackBar(text=f"{self.app.lang_conv.get_value('error')}: {e}", bg_color=self.app.theme_cls.error_color)
        