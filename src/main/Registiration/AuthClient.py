# import jwt.algorithms
import requests
# import json
# import os
from kivymd.app import MDApp 
from kivy.storage.jsonstore import JsonStore
from components.SnackBar import SnackBar
from Registiration.google_oauth import GoogleAuthHelper
import jwt 
class AuthClient:
    """Client for authentication API interactions"""
    def __init__(self, api_url="http://127.0.0.1:5000"):
        self.api_url = api_url
        self.app = MDApp.get_running_app()
        self.token_store = JsonStore('token_store.json')
        
    def signup(self, name, email, password):
        """Register a new user with email and password"""
        try:
            url = f"{self.api_url}/register/auth/signup"
            response = requests.post(
                url, 
                json={
                    #------------------28-04-2025-sign up------------------------------
                    "username": name,
                    #------------------28-04-2025-sign up------------------------------
                    "email": email,
                    "password": password
                },
                timeout=10
            )
            
            #------------------28-04-2025-sign up------------------------------
            if response.status_code == 201:
                SnackBar.callSnackBar(text="Kayıt başarılı! Giriş yapabilirsiniz.", bg_color=MDApp.get_running_app().theme_cls.primary_color)
                return True
            else:
                error_data = response.json()
                SnackBar.callSnackBar(text=f"Kayıt hatası: {error_data.get('message', 'Bilinmeyen hata')}", 
                                     bg_color=MDApp.get_running_app().theme_cls.primary_color)
                return False
                
        except Exception as e:
            SnackBar.callSnackBar(text=f"Bağlantı hatası: {str(e)}", bg_color=MDApp.get_running_app().theme_cls.primary_color)
            return False
        #------------------28-04-2025-sign up------------------------------
            
    def signin(self, email, password):
        """Login with email and password"""
        try:
            url = f"{self.api_url}/register/auth/signin"
            response = requests.post(
                url, 
                json={
                    "email": email,
                    "password": password
                },
                timeout=10
            )

            
            
            
            
            if response.status_code == 200:
                data = response.json()
                self._save_token(data['token'], data['user'])
                SnackBar.callSnackBar(text="Giriş başarılı!", bg_color=MDApp.get_running_app().theme_cls.primary_color)
                return True
            else:
                error_data = response.json()
                SnackBar.callSnackBar(text=f"Giriş hatası: {error_data.get('message', 'Bilinmeyen hata')}", 
                                     bg_color=MDApp.get_running_app().theme_cls.error_color)
                return False
                
        except Exception as e:
            SnackBar.callSnackBar(text=f"Bağlantı hatası: {str(e)}", bg_color=MDApp.get_running_app().theme_cls.error_color)
            return False
            
    def google_auth(self, id_token):
        """Authenticate with Google ID token"""
        try:
            url = f"{self.api_url}/auth/google"
            response = requests.post(
                url, 
                json={"id_token": id_token},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self._save_token(data['token'], data['user'])
                SnackBar.callSnackBar(text="Google ile giriş başarılı!", bg_color=self.app.theme_cls.primary_color)
                return True
            else:
                error_data = response.json()
                SnackBar.callSnackBar(text=f"Google giriş hatası: {error_data.get('message', 'Bilinmeyen hata')}", 
                                     bg_color=self.app.theme_cls.error_color)
                return False
                
        except Exception as e:
            SnackBar.callSnackBar(text=f"Bağlantı hatası: {str(e)}", bg_color=self.app.theme_cls.error_color)
            return False
            
    def reset_password(self, email):
        """Request password reset"""
        try:
            url = f"{self.api_url}/auth/reset-password"
            response = requests.post(
                url, 
                json={"email": email},
                timeout=10
            )
            
            if response.status_code == 200:
                SnackBar.callSnackBar(text=f"Şifre sıfırlama bağlantısı e-postanıza gönderildi", 
                                     bg_color=self.app.theme_cls.primary_color)
                return True
            else:
                error_data = response.json()
                SnackBar.callSnackBar(text=f"Şifre sıfırlama hatası: {error_data.get('message', 'Bilinmeyen hata')}", 
                                     bg_color=self.app.theme_cls.error_color)
                return False
                
        except Exception as e:
            SnackBar.callSnackBar(text=f"Bağlantı hatası: {str(e)}", bg_color=self.app.theme_cls.error_color)
            return False
    
    def get_user_profile(self):
        """Get current user profile"""
        try:
            if not self.is_authenticated():
                return None
                
            token = self.get_token()
            url = f"{self.api_url}/user/profile"
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                # Token may be expired, logout user
                if response.status_code == 401:
                    self.logout()
                return None
                
        except Exception as e:
            print(f"Profile fetch error: {str(e)}")
            return None
    
    def logout(self):
        """Clear authentication token"""
        if self.token_store.exists('user_token'):
            self.token_store.delete('user_token')
            
        if self.token_store.exists('user_data'):
            self.token_store.delete('user_data')

        
            
        SnackBar.callSnackBar(text="Çıkış yapıldı", bg_color=MDApp.get_running_app().theme_cls.primary_color)
        
    def is_authenticated(self):
        """Check if user is authenticated"""
        return self.token_store.exists('user_token')
    
    def is_token_valid(self):
        token = self.get_token()
        print(jwt.decode(token, 'your-secret-key-replace-this-in-production',algorithms=["HS256"]))
        
    def get_token(self):
        """Get the stored authentication token"""
        if self.token_store.exists('user_token'):
            return self.token_store.get('user_token')['value']
        return None
        
    def get_current_user(self):
        """Get the current user data"""
        if self.token_store.exists('user_data'):
            return self.token_store.get('user_data')['value']
        return None
        
    def _save_token(self, token, user_data):
        """Save authentication token and user data"""
        self.token_store.put('user_token', value=token)
        self.token_store.put('user_data', value=user_data)

# Create a global instance
auth_client = AuthClient()