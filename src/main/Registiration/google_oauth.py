# This is a simplified example for Google authentication integration

from kivy.app import App
from kivy.clock import Clock
import threading
import os
import platform
import requests

from components.SnackBar import SnackBar

# For Android
IS_ANDROID = platform.system() == "Android" or os.path.exists("/sdcard")

if IS_ANDROID:
    pass
    # Android implementation
    # from jnius import autoclass
    # from android.runnable import run_on_ui_thread
    
    # # Java classes
    # Activity = autoclass('android.app.Activity')
    # GoogleSignIn = autoclass('com.google.android.gms.auth.api.signin.GoogleSignIn')
    # GoogleSignInOptions = autoclass('com.google.android.gms.auth.api.signin.GoogleSignInOptions')
    # GoogleSignInAccount = autoclass('com.google.android.gms.auth.api.signin.GoogleSignInAccount')
    
    # class GoogleAuthHelper:
    #     def __init__(self, web_client_id):
    #         self.web_client_id = web_client_id
            
    #     @run_on_ui_thread
    #     def setup_google_signin(self):
    #         # Get current activity
    #         PythonActivity = autoclass('org.kivy.android.PythonActivity')
    #         currentActivity = PythonActivity.mActivity
            
    #         # Configure sign-in options
    #         gso = GoogleSignInOptions.Builder(GoogleSignInOptions.DEFAULT_SIGN_IN) \
    #             .requestIdToken(self.web_client_id) \
    #             .requestEmail() \
    #             .build()
                
    #         # Build GoogleSignInClient with options
    #         self.mGoogleSignInClient = GoogleSignIn.getClient(currentActivity, gso)
            
    #     def sign_in(self, callback):
    #         # Start sign-in Intent
    #         PythonActivity = autoclass('org.kivy.android.PythonActivity')
    #         currentActivity = PythonActivity.mActivity
            
    #         signInIntent = self.mGoogleSignInClient.getSignInIntent()
    #         currentActivity.startActivityForResult(signInIntent, 1001)
            
    #         # Use callback to process the result once available
    #         # This would require setting up activity result handling in your Android part
            
else:
    # Web or desktop implementation using OAuth flows
    import webbrowser
    from google_auth_oauthlib.flow import Flow
    
    class GoogleAuthHelper:
        def __init__(self, client_secrets_file):
            self.client_secrets_file = client_secrets_file
            
        def create_flow(self):
            return Flow.from_client_secrets_file(
                self.client_secrets_file,
                scopes=['https://www.googleapis.com/auth/userinfo.email', 
                        'https://www.googleapis.com/auth/userinfo.profile'],
                redirect_uri='http://127.0.0.1:5000/register/auth/google'
            )
            
        def sign_in(self, callback):
            
            flow = self.create_flow()
            print(flow)
            auth_url, _ = flow.authorization_url(prompt='select_account')
            
            print(auth_url)
            # Open browser for authentication
            webbrowser.open(auth_url)
            
            # In real implementation, you would need a local server to capture redirect
            # and complete the OAuth flow, then call the callback with result
            
# Example usage in your app
def process_google_signin(id_token, user_info):
    print('2')
    # Validate token with your backend
    # authenticate user or create account
    pass
    
# In your AuthApp class:
def google_signin(self):
    """Google ile giriş işlemini gerçekleştirir"""
    try:
        if IS_ANDROID:
            helper = GoogleAuthHelper("974074287339-d1dou49kvo0c6bvf1rt4mi6ldm79iemg.apps.googleusercontent.com")
        else:
            helper = GoogleAuthHelper("client_secret_974074287339-qnkoltb0dhorldc2iherkq7l100m8gfl.apps.googleusercontent.com.json")
        
        helper.sign_in(lambda token, user: process_google_signin(token, user))
        SnackBar.callSnackBar(text="Google ile giriş işlemi başlatılıyor...", bg_color=self.app.theme_cls.primary_color)
    except Exception as e:
        SnackBar.callSnackBar(text=f"Google giriş hatası: {e}", bg_color=self.app.theme_cls.error_color)