from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
# from kivymd.uix.
from kivy.lang import Builder
from kivy.clock import Clock
from components.SnackBar import SnackBar
from config import config_reader
	
# Import the auth client
from Registiration.AuthClient import auth_client

import requests
import threading

SignIn_KV='''
MDScreen:
    name: "signin_screen"
    
    MDBoxLayout:
        orientation: "vertical"
            
        MDBoxLayout:
            orientation: "vertical"
            padding: "24dp"
            spacing: "24dp"
            
            Widget:
                size_hint_y: 0.15
            
            MDLabel:
                text: "Hoş Geldiniz"
                halign: "center"
                font_style: "H4"
                adaptive_height: True
            
            MDCard:
                orientation: "vertical"
                padding: "16dp"
                spacing: "16dp"
                elevation: 4
                radius: [12]
                size_hint: None, None
                size: "280dp", "360dp"
                pos_hint: {"center_x": .5}
                
                MDTextField:
                    id: email_field
                    hint_text: "E-posta"
                    helper_text: "Geçerli bir e-posta adresi giriniz"
                    helper_text_mode: "on_focus"
                    icon_right: "email"
                    mode: "rectangle"

                
                    
                MDTextField:
                    mode: "rectangle"
                    id: password_field
                    hint_text: "Şifre"
                    helper_text: "Şifrenizi giriniz"
                    helper_text_mode: "on_focus"
                    icon_right: "eye-off"
                    mode: "rectangle"
                    password: True
                    
                    
                    

                    

                

                MDBoxLayout:
                    adaptive_height: True
                    
                    Widget:
                        size_hint_x: 0.5
                        
                    MDFlatButton:
                        text: "Şifremi Unuttum"
                        theme_text_color: "Custom"
                        text_color: app.theme_cls.primary_color
                        on_release: app.sign_in_app.goto_forgot_password()
                
                MDRaisedButton:
                    text: "Giriş Yap"
                    pos_hint: {"center_x": .5}
                    size_hint_x: 0.8
                    on_release: app.sign_in_app.signin()
                    
                MDBoxLayout:
                    adaptive_height: True
                    orientation: "vertical"
                    spacing: "8dp"
                    
                    MDLabel:
                        text: "veya"
                        halign: "center"
                        theme_text_color: "Secondary"
                        adaptive_height: True
                        
                    MDRaisedButton:
                        text: "Google ile Giriş Yap"
                        pos_hint: {"center_x": .5}
                        size_hint_x: 0.8
                        md_bg_color: [0.9, 0.3, 0.3, 1]
                        on_release: app.sign_in_app.google_signin()
                        
            MDFlatButton:
                text: "Hesabınız yok mu? Kayıt Olun"
                theme_text_color: "Custom"
                text_color: app.theme_cls.primary_color
                pos_hint: {"center_x": .5}
                on_release: app.sign_in_app.goto_signup()
'''

class SignInScreen(MDScreen):
    """Authentication screens container"""
    pass

class SignIn:

    def __init__(self):
        
        
        self._url = config_reader.get_config_value('route')# "127.0.0.1"  # Varsayılan olarak localhost
        self.app = MDApp.get_running_app()
        self.root = None
        self.settings_dialog = None
        self.current_screen = "signin_screen"

    def build(self):
        self.root = Builder.load_string(SignIn_KV)
        # Ana uygulamada kullanılabilmek için kendimize bir referans koy
        self.app.sign_in_app = self
        
        
       
        # Check if user is already authenticated
        if auth_client.is_authenticated():
            # Redirect to main menu if already logged in
            
            Clock.schedule_once(lambda dt: self.app.load_menu(), 0.1)

        return self.root
    
        
    
    # def goto_signin(self):
    #     """Sign In ekranına geçiş yapar"""
    #     self.root.ids.auth_screen_manager.current = "signin_screen"
    #     self.current_screen = "signin_screen"

    def goto_signup(self):
        """Sign Up ekranına geçiş yapar"""
        from Registiration.SignUp import SignUp
        self.app.load_screen(SignUp, 'signup_screen')

    def  goto_forgot_password(self):
        """Forgot Password ekranına geçiş yapar"""
        from Registiration.Password import Password
        
        self.app.load_screen(Password, 'forgot_password_screen')

    def test(self):
        print("çalıştı")

    def signin(self):
        """Kullanıcı giriş işlemini yapar"""
        try:
            email = self.root.ids.email_field.text
            password = self.root.ids.password_field.text
            
            
            if not email.strip() or not password.strip():
                SnackBar.callSnackBar(text="Lütfen e-posta ve şifre girin", bg_color=self.app.theme_cls.error_color)
                return
            
            
            # API'ye istek gönder (gerçek implementasyon için)
            # url = f"http://{self._url}:5000/auth/signin"
            # response = requests.post(url, json={"email": email, "password": password})
            
            # Şimdilik basit bir simülasyon
            if auth_client.signin(email, password):
                SnackBar.callSnackBar(text="Giriş başarılı!", bg_color=self.app.theme_cls.primary_color)
                # Başarılı girişten sonra ana menüye yönlendirme
                # self.app.back_to_menu()
                self.app.load_menu()
            else:
                SnackBar.callSnackBar(text="Giriş başarısız. Bilgilerinizi kontrol edin.", bg_color=self.app.theme_cls.error_color)
                
        except Exception as e:
            SnackBar.callSnackBar(text=f"Hata: {e}", bg_color=self.app.theme_cls.error_color)

    def google_signin(self):
        """Google ile giriş işlemini gerçekleştirir"""
        SnackBar.callSnackBar(text="Google ile giriş işlemi başlatılıyor...", bg_color=self.app.theme_cls.primary_color)
        from Registiration.google_oauth import google_signin
        google_signin(self)
        # Bu fonksiyon Google OAuth entegrasyonu gerektirir (ileride implementasyonu yapılacak)

    def show_settings_dialog(self):
        from components.SettingsModal import Dialog
        Dialog.show_settings_dialog(self)