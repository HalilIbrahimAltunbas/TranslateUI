import configparser

# config = configparser.ConfigParser()
# config.read('config.ini')
class configReader:
    
    # def __new__(self):
    #     self.config = configparser.ConfigParser()
    #     self.config.read('config.ini')
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('./src/main/config.ini')

    def get_config(self):
        return self.config
    def get_config_value (self,key:str):
        print(self.config.sections())
        return self.config.get('Section_Route',key)
    # def get_config(self,key:str):
    #     return self.config.__getitem__(key)

config_reader = configReader()