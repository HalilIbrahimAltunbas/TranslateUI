import json


class Convert:
    def __init__(self,lang):
        self.lang = lang.lower()
        self.pool = json.load(open('./src/main/i18n.json',encoding='utf-8'))

    def set_lang(self,value:str) :
         self.lang = value.lower()

    def get_value(self,value) -> str:
        return self.pool[self.lang][value]
    
lang = Convert('EN')
    
    # print(b[self.lang ]["app_menu"])