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

# SpeechApp için import (kodunuzu içe aktarıyoruz)
from SpeechRecognation.Speech_Page import SpeechApp
from OCR.OCR_Page import OCRApp
from Text.Text_Page import TranslateApp
from Registiration.SignUp import SignUp  
from Registiration.SignIn import SignIn 
from Registiration.Password import Password 
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
        adaptive_width: True
        padding: ["0dp", "0dp", "12dp", "0dp"]
        
        MDIconButton:
            icon: root.icon
            theme_icon_color: "Custom"
            icon_color: app.theme_cls.primary_color
    
    MDBoxLayout:
        orientation: "vertical"
        adaptive_height: True
        spacing: "4dp"
        
        MDLabel:
            text: root.text
            font_style: "H6"
            adaptive_height: True
            
        MDLabel:
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
            title: "Uygulama Menüsü"
            elevation: 4
            right_action_items: [["dots-vertical", lambda x: app.show_about()]]
        ScrollView:
            do_scroll_x: False
            do_scroll_y: True
            MDList:
                id: menu_list
                padding: "16dp"
                spacing: "16dp"
'''

class MenuButton(MDCard, RectangularRippleBehavior, CommonElevationBehavior):
    """Özel oluşturulmuş menü butonu sınıfı."""
    icon = StringProperty("android")
    text = StringProperty("Uygulama")
    description = StringProperty("Uygulama açıklaması")
    screen_cls = ObjectProperty(None)
    screen_name = StringProperty("")
    
    def on_release(self):
        """Butona tıklandığında çağrılır ve ilgili ekranı yükler."""
        app = MDApp.get_running_app()
        app.load_screen(self.screen_cls, self.screen_name)

class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Builder.load_string()
        self.screen_manager = None
        self.menu_items = []
        self.current_screen = None
        self.about_dialog = None
        
    def build(self):
        """Ana uygulamayı oluşturur."""
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.accent_palette = "Amber"
        self.theme_cls.theme_style = "Light"
        
        # Ekran yöneticisi oluştur
        self.screen_manager = MDScreenManager()
        
        # Ana ekranı oluştur
        main_screen = Builder.load_string(KV)
        self.screen_manager.add_widget(main_screen)
        
        # Menü öğelerini ekle
        self.setup_menu_items()
        self.populate_menu()
        
        
        return self.screen_manager
    
    def setup_menu_items(self):
        """Menü öğelerini yapılandırır."""
        # Menü öğesi eklemek için burayı kullanabilirsiniz

        
        
        self.add_menu_item(
            icon="microphone", 
            text="Ses Tanıma", 
            description="Konuşmayı metne çevirme uygulaması",
            screen_cls=SpeechApp,
            screen_name="speech_app"
        )
        
        # OCR Uygulaması örneği (gerçek uygulamanız ile değiştirin)
        self.add_menu_item(
            icon="text-recognition", 
            text="OCR Aracı", 
            description="Görselden metin tanıma uygulaması",
            screen_cls=OCRApp,  # Gerçek OCR uygulamanızı buraya ekleyin
            screen_name="ocr_app"
        )
        
        # Daha fazla uygulama ekleyebilirsiniz
        self.add_menu_item(
            icon="translate", 
            text="Çeviri Aracı", 
            description="Metni farklı dillere çevirme uygulaması",
            screen_cls=TranslateApp,  # Gerçek çeviri uygulamanızı buraya ekleyin
            screen_name="translate_app"
        )
        
        self.add_menu_item(
            icon="text-to-speech", 
            text="Metin Okuma", 
            description="Metni sesli okuma uygulaması",
            screen_cls=None,  # Gerçek TTS uygulamanızı buraya ekleyin
            screen_name="tts_app"
        )
    
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
        
        for item in self.menu_items:
            button = MenuButton(
                icon=item["icon"],
                text=item["text"],
                description=item["description"],
                screen_cls=item["screen_cls"],
                screen_name=item["screen_name"]
            )
            
            # Bütona tıklama olayını bağla
            button.bind(on_touch_up=self.on_button_touch)
            
            # Butonu listeye ekle
            menu_list.add_widget(button)
    
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
            Snackbar(text=f"{screen_name} henüz uygulanmadı").open()
            return
        
        # Eğer ekran zaten oluşturulmuşsa, ona geç
        if self.screen_manager.has_screen(screen_name):
            self.screen_manager.current = screen_name
            return
            
        try:
            # Yeni bir ekran örneği oluştur
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
            
            # Ekrana geç
            self.screen_manager.current = screen_name
            
            # Mevcut ekranı kaydet (ana menüye dönmek için)
            self.current_screen = screen_name
            
        except Exception as e:
            from components.SnackBar import SnackBar
            SnackBar.callSnackBar(text=f"Hata: {e}",bg_color=self.theme_cls.primary_color)
            # Snackbar(text=f"Hata: {e}").open()
    
    def show_about(self):
        """Uygulama hakkında bilgi gösterir."""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton
        
        if not self.about_dialog:
            self.about_dialog = MDDialog(
                title="Hakkında",
                text="Modüler Uygulama Menüsü v1.0\n\nBu uygulama, farklı işlevler için tek bir arayüz sağlar.",
                buttons=[
                    MDFlatButton(
                        text="KAPAT",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.about_dialog.dismiss()
                    )
                ],
            )
        self.about_dialog.open()
    
    def back_to_menu(self):
        """Ana menüye geri döner."""
        self.screen_manager.current = "MainScreen"

# Ana ekrana isim ver


if __name__ == "__main__":
    MainApp().run()