import requests
from Registiration.AuthClient import auth_client 

from Service.HttpInterceptor import HttpInterceptor

'''
This service includes common Http Requests Type.
Service's purpose is make customize and manage all request in a service 
'''
class HttpService:
    def __init__(self):
        self.token = auth_client.get_token()
        
        
    # def token_refresh(self):
    #     self.token = AuthClient.auth_client.get_token()
       
    
    '''
    Params:
        url: API's Url,
        args: request parameters
            args can includes:
                params: _Params | None = None,
                data: _Data | None = ...,
                cookies: CookieJar | _TextMapping | None = ...,
                files: _Files | None = ...,
                auth: _Auth | None = ...,
                timeout: _Timeout | None = ...,
                allow_redirects: bool = ...,
                proxies: _TextMapping | None = ...,
                hooks: _HooksInput | None = ...,

    for more information see requests.request parameters.
    '''
    @HttpInterceptor.http_interceptor
    def get(self,url:str,args:dict = {})-> requests.Response:
        # self.token_refresh()
        return requests.get(url,headers={"Authorization": f"Bearer {auth_client.get_token()}"},**args)
        
    
    def post(self,url:str,args:dict) -> requests.Response:
        return requests.post(url,headers={"Authorization": f"Bearer {self.token}"},**args)
    
    def put(self,url:str,args:dict) -> requests.Response:
        return requests.put(url,headers={"Authorization": f"Bearer {self.token}"},**args)
    
    def delete(self,url:str,args:dict) -> requests.Response:
        return requests.delete(url,headers={"Authorization": f"Bearer {self.token}"},**args)
    
httpservice = HttpService()