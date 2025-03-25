from functools import wraps
from Registiration.AuthClient import auth_client
from kivymd.app import MDApp
from kivy.clock import Clock

class HttpInterceptor:

    def http_interceptor(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            print(args)
            print(kwargs)
            response = f(*args, **kwargs)

            if  response.status_code == 401:
                print('test')
                Clock.schedule_once(lambda dt: MDApp.get_running_app().log_out(), 0)
                
                
                
                
            else :
                return response
        return decorated