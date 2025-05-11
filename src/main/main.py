from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen,Screen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.list import MDList, OneLineAvatarIconListItem
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty
from kivymd.uix.button import MDIconButton
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivymd.uix.behaviors.elevation import CommonElevationBehavior
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.toolbar.toolbar import MDTopAppBar

# SpeechApp için import (kodunuzu içe aktarıyoruz)
from SpeechRecognation.Speech_Page import SpeechApp
from OCR.OCR_Page import OCRApp
from Text.Text_Page import TranslateApp
from QuizPage.QuizPage import WordGameApp
from Dictionary.Dictionary import DictionaryApp
from Registiration.SignUp import SignUp
from Registiration.SignIn import SignIn
from Registiration.Password import Password
from Registiration.AuthClient import auth_client
from Chat.geminiUI import GeminiApp


# Ana ekran ve butonlar için KV dili tanımı
KV = '''
<MenuButton>:
   
    orientation: "horizontal"
    adaptive_height: True
    spacing: "12dp"
    padding: "16dp"
    radius: [8]
    elevation: 2
    md_bg_color: app.theme_cls.bg_light
    ripple_behavior: True

    MDBoxLayout:
        id:BoxLayout1
        adaptive_width: True
        padding: ["0dp", "0dp", "12dp", "0dp"]

        MDIconButton:
            id:IconButtoninBoxLayout1
            icon: root.icon
            theme_icon_color: "Custom"
            icon_color: app.theme_cls.primary_color

    MDBoxLayout:
        id:BoxLayout2
        orientation: "vertical"
        adaptive_height: True
        spacing: "4dp"

        MDLabel:
            id:LabelinBoxLayout2
            text: root.text
            font_style: "H6"
            adaptive_height: True

        MDLabel:
            id:Label2inBoxLayout2
            text: root.description
            font_style: "Caption"
            theme_text_color: "Secondary"
            adaptive_height: True

    Widget:
MDScreen:
    name:'MainScreen'
    MDBoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            id:topbar
            title: app.lang_conv.get_value('app_menu')
            elevation: 4
            right_action_items: [["dots-vertical", lambda x: app.show_about()],["logout", lambda x: app.log_out()],["translate-variant" ,lambda x: app.menu_open(x)],["theme-light-dark" ,lambda x: app.active_Dark_Theme()]]


        ScrollView:
            do_scroll_y: True
            MDList:
                id: menu_list
                padding: "16dp"
                spacing: "16dp"
'''

class MenuButton(MDCard, RectangularRippleBehavior, CommonElevationBehavior):
    """Özel oluşturulmuş menü butonu sınıfı."""
    id = StringProperty("Id")
    icon = StringProperty("android")
    text = StringProperty("Uygulama")
    description = StringProperty("Uygulama açıklaması")
    screen_cls = ObjectProperty(None)
    screen_name = StringProperty("")

        
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_touch_up=self._on_touch_up)
    
    def _on_touch_up(self, instance, touch):
        """Butona tıklama olayını işler."""
        if instance.collide_point(*touch.pos) and not touch.is_mouse_scrolling:
            if touch.is_double_tap or touch.is_triple_tap:
                return False
            if touch.button == 'left':
                self.on_release()
                return True
        return False

    
    def on_release(self):
        """Butona tıklandığında çağrılır ve ilgili ekranı yükler."""
        app = MDApp.get_running_app()
        app.load_screen(self.screen_cls, self.screen_name)


        

    

import i18n

class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Builder.load_string()
        self.screen_manager = None
        self.menu_items = []
        self.current_screen = None
        self.about_dialog = None
        self.lang = 'EN'
        self.lang_conv = i18n.lang
        



    def build(self):
        """Ana uygulamayı oluşturur."""
        self.Dark_theme_active = 0
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.accent_palette = "Amber"
        self.theme_cls.theme_style = "Light"

        # self.theme_cls.primary_color = "Blue"
        # self.theme_cls.error_color = "Red"

        # Ekran yöneticisi oluştur
        self.screen_manager = MDScreenManager()
        self.sign_in_screen()
        # Ana ekranı oluştur
        # main_screen = Builder.load_string(KV)
        # self.screen_manager.add_widget(main_screen)

        # Menü öğelerini ekle
        # self.setup_menu_items()
        # self.populate_menu()
        

        return self.screen_manager
    
    def active_Dark_Theme(self):
        #  auth_client.is_token_valid()
        self.Dark_theme_active = not self.Dark_theme_active
        self.theme_cls.theme_style = ("Dark" if self.Dark_theme_active else "Light")

    def sign_in_screen(self):
        self.load_screen(SignIn,'sign_in_screen')

    def menu_open(self,a):
        menu_options = [
            {
                "text": "TR",
                "on_release": lambda x ="tr": self.menu_callback(x),
            },
            {
                "text": "EN",
                "on_release": lambda x="en": self.menu_callback(x),
            }
        ]

        MDDropdownMenu(
            caller= a, items=menu_options
        ).open()

    def menu_callback(self, text_item:str):
        if text_item.lower() == self.lang.lower():
            return
        self.lang = text_item
        self.lang_conv.set_lang(text_item)
        self.load_menu()



    def load_menu(self):
        # Ana ekranı oluştur
        if(not self.screen_manager.has_screen('MainScreen')):
           
            self.main_screen = Builder.load_string(KV)
            self.screen_manager.clear_widgets()
            self.screen_manager.add_widget(self.main_screen)
#----------------28-4-25-SignIn bug fix-----------------------------------------------
        else:
            self.screen_manager.switch_to(self.main_screen)
#----------------28-4-25-SignIn bug fix-----------------------------------------------
        
        # Menü öğelerini ekle
        self.setup_menu_items()
        self.populate_menu()
    
    def setup_menu_items(self):
        """Menü öğelerini yapılandırır."""
        # Menü öğesi eklemek için burayı kullanabilirsiniz
        self.menu_items.clear()

        self.add_menu_item(
            icon="microphone",
            text=self.lang_conv.get_value('speech_recognition'),#"Ses Tanıma",
            description=self.lang_conv.get_value('speech_recognition_desc'),
            screen_cls=SpeechApp,
            screen_name="speech_app"
        )

        # OCR Uygulaması örneği
        self.add_menu_item(
            icon="text-recognition",
            text=self.lang_conv.get_value('ocr_tool'),
            description=self.lang_conv.get_value('ocr_tool_desc'),
            screen_cls=OCRApp,  
            screen_name="ocr_app"
        )

        self.add_menu_item(
            icon="chat",
            text=self.lang_conv.get_value('chat_app'),
            description=self.lang_conv.get_value('chat_page_desc'),
            screen_cls=GeminiApp,  
            screen_name="chat_page"
        )

        self.add_menu_item(
            icon="translate",
            text=self.lang_conv.get_value('translation_tool'),
            description=self.lang_conv.get_value('translation_tool_desc'),
            screen_cls=TranslateApp,  
            screen_name="translate_app"
        )

        self.add_menu_item(
            icon="book-alphabet",
            text=self.lang_conv.get_value('dictionary_app'),
            description=self.lang_conv.get_value('dictionary_app_desc'),
            screen_cls=DictionaryApp,  
            screen_name="dict_app"
        )

        self.add_menu_item(
            icon="file-word-outline",
            text=self.lang_conv.get_value('word_game'),
            description=self.lang_conv.get_value('word_game_instruction'),
            screen_cls=WordGameApp,  
            screen_name="word_game"
        )

        # self.add_menu_item(
        #     icon="text-to-speech",
        #     text=self.lang_conv.get_value('text_to_speech'),
        #     description=self.lang_conv.get_value('text_to_speech_desc'),
        #     screen_cls=None,  
        #     screen_name="tts_app"
        # )

    def add_menu_item(self, icon, text, description, screen_cls, screen_name):
        """Menüye yeni bir öğe ekler."""

        self.menu_items.append({
            "icon": icon,
            "text": text,
            "description": description,
            "screen_cls": screen_cls,
            "screen_name": screen_name
        })

    def populate_menu(self):
        """Menü listesini öğelerle doldurur."""
        menu_list = self.screen_manager.get_screen("MainScreen").ids.menu_list
        menu_list.clear_widgets()
        i = 0
        
        for item in self.menu_items:
            button = MenuButton(
                id= f"button_{i}",
                icon=item["icon"],
                text=item["text"],
                description=item["description"],
                screen_cls=item["screen_cls"],
                screen_name=item["screen_name"]
            )
            i += 1

            ### find a solution for this
            '''
            denote for me: MenuButton object take 3 widgets every new instance,
            our need is just 3 widget 
            '''
            # if len(button.children) > 3:
            #     for i in range(3,len(button.children)):
                    
            #         button.remove_widget(button.children[3])

            # Butona tıklama olayını bağla
            # button.bind(on_touch_up=self.on_button_touch)

            # Butonu listeye ekle
            menu_list.add_widget(button)
            
            # print(menu_list.children[0]._proxy_ref.__dir__())
            
            
    
    def on_button_touch(self, instance, touch):
        """Butona tıklama olayını işler."""
        if instance.collide_point(*touch.pos) and touch.is_mouse_scrolling is False:
            if touch.is_double_tap or touch.is_triple_tap:
                return False
            if touch.button == 'left' and instance.collide_point(*touch.pos):
                instance.on_release()
                return True
        return False
    
    def load_screen(self, screen_cls, screen_name):
        """Belirtilen ekranı yükler ve gösterir."""
        if screen_cls is None:
            # Uygulama henüz uygulanmamışsa bildir
            from kivymd.uix.snackbar import Snackbar
            Snackbar(text=f"{screen_name} {self.lang_conv.get_value('not_implemented')}").open()
            return
        
        # Eğer ekran zaten oluşturulmuşsa, ona geç
        if self.screen_manager.has_screen(screen_name):
            self.screen_manager.current = screen_name
            print(f"{screen_name} has already registered")
            return

        try:
            # Yeni bir ekran örneği oluştur
            print(f"screen manager's children: {self.screen_manager._get_screen_names()}")

            print(f"{screen_name} registering")
            screen_instance = screen_cls().build()
           
            # Eğer bir MDScreen döndürülmediyse, onu bir MDScreen içine yerleştir
            if not isinstance(screen_instance, MDScreen):
                container = MDScreen(name=screen_name)
                container.add_widget(screen_instance)
                screen_instance = container
            else:
                screen_instance.name = screen_name

            # Ekranı ekran yöneticisine ekle
            self.screen_manager.add_widget(screen_instance)
            print(f"screen manager's children: {self.screen_manager._get_screen_names()}")


            # Ekrana geç
            self.screen_manager.current = screen_name

            # Mevcut ekranı kaydet (ana menüye dönmek için)
            self.current_screen = screen_name

        except Exception as e:
            from components.SnackBar import SnackBar
            SnackBar.callSnackBar(text=f"Error: {e}",bg_color=self.theme_cls.primary_color)
            # Snackbar(text=f"Hata: {e}").open()

    def show_about(self):
        """Uygulama hakkında bilgi gösterir."""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton

        if not self.about_dialog:
            self.about_dialog = MDDialog(
                title=self.lang_conv.get_value('about'),
                text="Modüler Uygulama Menüsü v1.0\n\nBu uygulama, farklı işlevler için tek bir arayüz sağlar.",
                buttons=[
                    MDFlatButton(
                        text=self.lang_conv.get_value('close'),
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.about_dialog.dismiss()
                    )
                ],
            )
        self.about_dialog.open()

    def back_to_menu(self):
        """Go back to Main Menu"""
        self.screen_manager.current = "MainScreen"

    def log_out(self):
        auth_client.logout()
        self.sign_in_screen()

# Ana ekrana isim ver


if __name__ == "__main__":
    MainApp().run()