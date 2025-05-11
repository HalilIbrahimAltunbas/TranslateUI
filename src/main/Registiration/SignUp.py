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

from Registiration.AuthClient import auth_client

from config import config_reader


SignUp_Kv ='''
MDScreen:
    name: "signup_screen"
    
    MDBoxLayout:
        orientation: "vertical"
        
        # MDTopAppBar:
        #     title: app.lang_conv.get_value('sign_up')
        #     elevation: 4
        #     left_action_items: [["arrow-left", lambda x: app.sign_up_app.goto_signin()]]
            
        MDBoxLayout:
            orientation: "vertical"
            padding: "24dp"
            spacing: "24dp"
            
            Widget:
                size_hint_y: 0.1
            
            MDLabel:
                text: app.lang_conv.get_value('register_create_account')
                halign: "center"
                font_style: "H5"
                adaptive_height: True
            
            MDCard:
                orientation: "vertical"
                padding: "16dp"
                spacing: "16dp"
                elevation: 4
                radius: [12]
                size_hint: None, None
                size: "280dp", "440dp"
                pos_hint: {"center_x": .5}
                
                MDTextField:
                    id: signup_name_field
                    hint_text: app.lang_conv.get_value('register_name_input')
                    helper_text: app.lang_conv.get_value('register_name_input_hint')
                    helper_text_mode: "on_focus"
                    icon_right: "account"
                    mode: "rectangle"
                    
                MDTextField:
                    id: signup_email_field
                    hint_text: app.lang_conv.get_value('register_mail_input')
                    helper_text: app.lang_conv.get_value('register_mail_input_hint')
                    helper_text_mode: "on_focus"
                    icon_right: "email"
                    mode: "rectangle"
                    validator: "email"
                    
                MDTextField:
                    id: signup_password_field
                    hint_text: app.lang_conv.get_value('register_password')
                    helper_text: app.lang_conv.get_value('register_password_hint')
                    helper_text_mode: "on_focus"
                    icon_right: "eye-off"
                    mode: "rectangle"
                    password: True
                    
                MDTextField:
                    id: signup_confirm_field
                    hint_text: app.lang_conv.get_value('register_password_confirm')
                    helper_text: app.lang_conv.get_value('register_password_confirm_hint')
                    helper_text_mode: "on_focus"
                    icon_right: "eye-off"
                    mode: "rectangle"
                    password: True
                
                MDRaisedButton:
                    text: app.lang_conv.get_value('register_button')
                    pos_hint: {"center_x": .5}
                    size_hint_x: 0.8
                    on_release: app.sign_up_app.signup()
                    
                MDBoxLayout:
                    adaptive_height: True
                    orientation: "vertical"
                    spacing: "8dp"
                    
                    MDLabel:
                        text: app.lang_conv.get_value('register_text_or')
                        halign: "center"
                        theme_text_color: "Secondary"
                        adaptive_height: True
                        
                    MDRaisedButton:
                        text: app.lang_conv.get_value('register_button_google')
                        pos_hint: {"center_x": .5}
                        size_hint_x: 0.8
                        md_bg_color: [0.9, 0.3, 0.3, 1]
                        on_release: app.sign_up_app.google_signup()
            
            MDFlatButton:
                text: app.lang_conv.get_value('register_go_to_sign')
                theme_text_color: "Custom"
                text_color: app.theme_cls.primary_color
                pos_hint: {"center_x": .5}
                on_release: app.sign_up_app.goto_signin()
'''

class SignUpScreen(MDScreen):
    """Authentication screens container"""
    pass

class SignUp:
    def __init__(self):
        self._url = config_reader.get_config_value('route')#"127.0.0.1"  # Varsayılan olarak localhost
        self.app = MDApp.get_running_app()
        self.root = None
        self.settings_dialog = None
        self.current_screen = "signin_screen"

    def build(self):
        self.root = Builder.load_string(SignUp_Kv)
        
        # Ana uygulamada kullanılabilmek için kendimize bir referans koy
        self.app.sign_up_app = self
        
        return self.root
    
    # def goto_signup(self):
    #     """Sign Up ekranına geçiş yapar"""
    #     self.root.ids.auth_screen_manager.current = "signup_screen"
    #     self.current_screen = "signup_screen"

    def goto_signin(self):
        """Sign In ekranına geçiş yapar"""
        
        
        # self.app.screen_manager.current = "signin_screen"
        # self.current_screen = "signin_screen"
        from Registiration.SignIn import SignIn
        self.app.load_screen(SignIn, 'signin_screen')
        

    def signup(self):
        """Yeni kullanıcı kaydı yapar"""
        try:
            name = self.root.ids.signup_name_field.text
            email = self.root.ids.signup_email_field.text
            password = self.root.ids.signup_password_field.text
            confirm = self.root.ids.signup_confirm_field.text
            
            if not name.strip() or not email.strip() or not password.strip():
                SnackBar.callSnackBar(text=self.app.lang_conv.get_value('register_fill_blank'), bg_color=self.app.theme_cls.error_color)
                return
                
            if password != confirm:
                SnackBar.callSnackBar(text=self.app.lang_conv.get_value('register_warn_password_not_match'), bg_color=self.app.theme_cls.error_color)
                return
                
            if len(password) < 8:
                SnackBar.callSnackBar(text=self.app.lang_conv.get_value('register_password_hint'), bg_color=self.app.theme_cls.error_color)
                return
            
            # API'ye istek gönder (gerçek implementasyon için)
            # url = f"http://{self._url}:5000/auth/signup"
            # response = requests.post(url, json={"name": name, "email": email, "password": password})
            
            # Şimdilik basit bir simülasyon
            #------------------28-04-2025-sign up------------------------------
            if auth_client.signup(name=name,email=email,password=password):
                SnackBar.callSnackBar(text=self.app.lang_conv.get_value('register_success'), bg_color=self.app.theme_cls.primary_color)
                self.goto_signin()
            #------------------28-04-2025-sign up------------------------------
        except Exception as e:
            SnackBar.callSnackBar(text=f"{self.app.lang_conv.get_value('error')}: {e}", bg_color=self.app.theme_cls.error_color)
            
    def google_signup(self):
        """Google ile kayıt işlemini gerçekleştirir"""
        SnackBar.callSnackBar(text=self.app.lang_conv.get_value('register_begin_google_sign'), bg_color=self.app.theme_cls.primary_color)
        # Bu fonksiyon Google OAuth entegrasyonu gerektirir (ileride implementasyonu yapılacak)

    def show_settings_dialog(self):
        from components.SettingsModal import Dialog
        Dialog.show_settings_dialog(self)
    