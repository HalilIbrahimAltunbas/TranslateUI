from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.gridlayout import MDGridLayout
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
import requests
import threading
from kivy.clock import Clock
from config import config_reader
from Service.HttpService import httpservice
from Registiration import AuthClient
from components.SettingsModal import Dialog

# Rol seçim ekranı ve Sohbet arayüzü tasarımı
KV = '''

<RoleCard>:
    orientation: "vertical"
    size_hint_y: None
    height: dp(120)
    padding: dp(10)
    spacing: dp(5)
    elevation: 2
    radius: [10]
    ripple_behavior: True
    
    MDIcon:
        icon: root.icon
        halign: "center"
        font_size: "48sp"
        theme_text_color: "Primary"
    
    MDLabel:
        text: root.role_name
        halign: "center"
        valign: "top"
        size_hint_y: None
        height: dp(30)

<MessageBubble>:
    orientation: "vertical"
    size_hint_y: None
    height: self.minimum_height
    padding: dp(12)
    spacing: dp(5)
    md_bg_color: app.theme_cls.primary_color if root.is_user else [0.7, 0.7, 0.7, 1]
    radius: [15, 15, 3 if root.is_user else 15, 15 if root.is_user else 3]
    pos_hint: {"right": 0.98} if root.is_user else {"x": 0.02}
    size_hint_x: 0.7
    elevation: 2
    
    MDLabel:
        text: root.text
        size_hint_y: None
        height: self.texture_size[1]
        # font_name: 'Segoe UI Emoji'
        color: [1, 1, 1, 1] if root.is_user else [0, 0, 0, 1]
        markup: True

ScreenManager:
    id: screen_manager
    
    MDScreen:
        name: "role_selection"
        
        MDBoxLayout:
            orientation: "vertical"
            
            MDTopAppBar:
                title: app.lang_conv.get_value('role_selection')
                left_action_items: [["arrow-left", lambda x: app.gemini_app.back_to_menu()]]
                elevation: 4
            
            MDLabel:
                text: app.lang_conv.get_value('select_role')
                halign: "center"
                size_hint_y: None
                height: dp(50)
                
            ScrollView:
                do_scroll_x: False
                
                MDBoxLayout:
                    orientation: "vertical"
                    padding: dp(20)
                    spacing: dp(20)
                    adaptive_height: True
                    
                    RoleGrid:
                        id: role_grid
                        cols: 2
                        spacing: dp(15)
                        adaptive_height: True

    MDScreen:
        name: "chat_page"
        
        MDBoxLayout:
            orientation: "vertical"

            MDTopAppBar:
                title: app.lang_conv.get_value('chat_app')
                left_action_items: [["arrow-left", lambda x: app.gemini_app.back_to_role_selection()]]
                right_action_items: [["cog", lambda x: app.gemini_app.show_settings_dialog()]]
                elevation: 4

            MDLabel:
                id: active_role_label
                text: ""
                halign: "center"
                size_hint_y: None
                height: dp(30)
                theme_text_color: "Secondary"

            ScrollView:
                id: scroll_view
                effect_cls: "ScrollEffect"
                scroll_type: ['bars', 'content']
                bar_width: dp(0)
                
                MDBoxLayout:
                    id: chat_messages
                    orientation: "vertical"
                    spacing: dp(10)
                    padding: dp(10)
                    adaptive_height: True
                    size_hint_y: None
                    height: self.minimum_height
            
            MDBoxLayout:
                size_hint_y: None
                height: dp(60)
                padding: dp(5)
                spacing: dp(5)
                md_bg_color: app.theme_cls.bg_normal
                
                MDCard:
                    padding: dp(2)
                    radius: [20]
                    line_color: [0, 0, 0, 0]
                    elevation: 3
                    size_hint_y: None
                    height: message_input.height + 5
                    
                    MDBoxLayout:
                        orientation: "horizontal"
                        padding: [dp(15), 0, dp(5), 0]
                        
                        MDTextField:
                            id: message_input
                            hint_text: app.lang_conv.get_value('chat_input_hint')
                            multiline: True
                            max_height: "100dp"
                            mode: "fill"
                            fill_color: 0, 0, 0, 0
                            size_hint: 1, None
                            height: max(dp(40), self.minimum_height)
                            hint_text_color_normal: app.theme_cls.disabled_hint_text_color
                            line_color_normal: [0, 0, 0, 0]
                            line_color_focus: [0, 0, 0, 0]
                        
                        MDIconButton:
                            icon: "send"
                            theme_text_color: "Custom"
                            text_color: app.theme_cls.primary_color
                            on_release: app.gemini_app.send_message()
'''

# Role seçim kutucuğu tasarımı
# ROLE_CARD_KV = '''
# <RoleCard>:
#     orientation: "vertical"
#     size_hint_y: None
#     height: dp(120)
#     padding: dp(10)
#     spacing: dp(5)
#     elevation: 2
#     radius: [10]
#     ripple_behavior: True
    
#     MDIcon:
#         # icon: root.icon
#         # halign: "center"
#         # font_size: "48sp"
#         # theme_text_color: "Primary"
    
#     MDLabel:
#         text: root.role_name
#         halign: "center"
#         valign: "top"
#         size_hint_y: None
#         height: dp(30)
# '''

# # Mesaj balonu tasarımı
# CHAT_MESSAGE_KV = '''
# <MessageBubble>:
#     orientation: "vertical"
#     size_hint_y: None
#     height: self.minimum_height
#     padding: dp(12)
#     spacing: dp(5)
#     md_bg_color: app.theme_cls.primary_color if root.is_user else [0.7, 0.7, 0.7, 1]
#     radius: [15, 15, 3 if root.is_user else 15, 15 if root.is_user else 3]
#     pos_hint: {"right": 0.98} if root.is_user else {"x": 0.02}
#     size_hint_x: 0.7
#     elevation: 2
    
#     MDLabel:
#         text: root.text
#         size_hint_y: None
#         height: self.texture_size[1]
#         color: [1, 1, 1, 1] if root.is_user else [0, 0, 0, 1]
#         markup: True
# '''


class MessageBubble(MDCard):
    text = StringProperty()
    is_user = BooleanProperty()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class RoleGrid(MDGridLayout):
    pass


class RoleCard(MDCard):
    role_name = StringProperty()
    role_id = StringProperty()
    icon = StringProperty("android")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.role_id = kwargs.get('role_id', '')
        self.role_name = kwargs.get('role_name', '')
        self.icon = kwargs.get('icon', 'android')
    
    def on_release(self):
        app = MDApp.get_running_app()
        app.gemini_app.select_role(self.role_id, self.role_name)


class GeminiApp:
    def __init__(self):
        try:
            self._url = config_reader.get_config_value('route')  # API host from config
            self.app = MDApp.get_running_app()
            self.root = None
            self.settings_dialog = None
            self.selected_role = None
            self.selected_role_name = ""
            
            # Roller array'i - Gerçek uygulamada config dosyasından veya API'den çekilebilir
            self.roles = [
                {"id": "assistant", "name": "Genel Asistan", "icon": "robot"},
                {"id": "teacher", "name": "Öğretmen", "icon": "school"},
                {"id": "doctor", "name": "Doktor", "icon": "doctor"},
                {"id": "chef", "name": "Şef", "icon": "food"},
                {"id": "programmer", "name": "Programcı", "icon": "code-tags"},
                {"id": "storyteller", "name": "Hikaye Anlatıcısı", "icon": "book-open-variant"}
            ]
        except Exception as e:
            print(f"init error: {e}")

    def build(self):
        try:
            # self.role_s = Builder.load_string(ROLE_CARD_KV)
            # self.chat_msg_s= Builder.load_string(CHAT_MESSAGE_KV)
            
            self.root = Builder.load_string(KV)
            self.app.gemini_app = self  # Reference into main app
            
            # Rol kartlarını oluştur
            self._create_role_cards()
            
            return self.root
        except Exception as e:
            print(f"Build error: {e}")

    def _create_role_cards(self):
        role_grid = self.root.ids.role_grid
        
        for role in self.roles:
            role_card = RoleCard(
                role_id=role["id"],
                role_name=role["name"],
                icon=role["icon"]
            )
            role_card.bind(on_release=lambda instance=role_card: self.select_role(instance.role_id, instance.role_name))
            role_grid.add_widget(role_card)

    def select_role(self, role_id, role_name):
        """Kullanıcı bir rol seçtiğinde çağrılır"""
        self.selected_role = role_id
        self.selected_role_name = role_name
        
        # Rol seçimini etiket olarak göster
        role_label = self.root.ids.active_role_label
        role_label.text = f"{self.app.lang_conv.get_value('active_role')}: {role_name}"
        
        # Sohbet ekranına geç
        self.clear_chat()
        self.root.current = "chat_page"
        
        # Seçilen rol için karşılama mesajını göster
        # welcome_msg = f"{self.app.lang_conv.get_value('welcome_message')} {role_name} {self.app.lang_conv.get_value('mode')}"
        print("a")
        # self._add_chat_message(welcome_msg, is_user=False)

    def send_message(self):
        user_input = self.root.ids.message_input.text.strip()
        if not user_input:
            return

        # Add user message to chat
        self._add_chat_message(user_input, is_user=True)

        # Clear input field
        self.root.ids.message_input.text = ""

        # Start a thread to get AI response to avoid UI freeze
        threading.Thread(target=self._get_ai_response, args=(user_input,)).start()

    def _get_ai_response(self, message):
        try:
            # API call to Gemini - Now including the selected role
            url = f"http://{self._url}:5000/gemini"
            
            # Use the authorized request via httpservice
            payload = {
                "message": message,
                "role": self.selected_role  # Seçilen rolü API'ye gönder
            }

            response = requests.post(url,headers = {"Authorization": f"Bearer {AuthClient.auth_client.get_token()}"} ,json=payload)
            #response = httpservice.post(url, json=payload)
           
            if response.ok:
                print("calisiyor")
                reply = response.json().get('response', self.app.lang_conv.get_value('error_no_response'))
                print(reply)
                # Update UI on main thread
                Clock.schedule_once(lambda dt: self._add_chat_message(reply, is_user=False), 0)
                print("bitti")
            else:
                error_msg = response.json().get("error", self.app.lang_conv.get_value('unknown_error'))
                Clock.schedule_once(lambda dt: self._add_chat_message(
                    f"API Error: {error_msg}", is_user=False), 0)
        except Exception as e:
            # Handle connection errors
            err = e
            print(e)
            Clock.schedule_once(lambda dt: self._add_chat_message(
                f"{self.app.lang_conv.get_value('error')}: {str(err)}", is_user=False), 0)

    def _add_chat_message(self, text, is_user=False):
        # Create message bubble
        message = MessageBubble(
            text=text,
            is_user=is_user
        )
        
        # Add message to chat
        chat_messages = self.root.ids.chat_messages
        chat_messages.add_widget(message)
        
        # Scroll to bottom after message is added (with a small delay to ensure proper rendering)
        Clock.schedule_once(lambda dt: self._scroll_to_bottom(), 0.1)

    def clear_chat(self):
        chat_messages = self.root.ids.chat_messages
        chat_messages.clear_widgets()

    def _scroll_to_bottom(self):
        """Scroll the chat to the bottom to see the latest messages"""
        scroll_view = self.root.ids.scroll_view
        scroll_view.scroll_y = 0
    
    def back_to_role_selection(self):
        if self.root.current == "chat_page":
            self.root.current = "role_selection"
        # if self.selected_role_name == self.self.root.ids.active_role_label.text:

    def back_to_menu(self):
        # Eğer sohbet ekranındaysa rol seçim ekranına dön
        
        # if self.root.current == "chat_page":
        #     self.root.current = "role_selection"
        # else:
            # Ana menüye dön (orijinal back_to_menu işlevi)
            self.back_to_role_selection()
            self.app.back_to_menu()
    
    def show_settings_dialog(self):
        Dialog.show_settings_dialog(self)