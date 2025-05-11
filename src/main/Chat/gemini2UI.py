from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty
import requests
import threading
from kivy.clock import Clock
from config import config_reader
from Service.HttpService import httpservice
from Registiration import AuthClient
from components.SettingsModal import Dialog

# Chat message bubble design
CHAT_KV = '''
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
        color: [1, 1, 1, 1] if root.is_user else [0, 0, 0, 1]
        markup: True

MDScreen:
    name: "chat_page"
    
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: app.lang_conv.get_value('chat_app')
            left_action_items: [["arrow-left", lambda x: app.back_to_menu()]]
            right_action_items: [["cog", lambda x: app.gemini_app.show_settings_dialog()]]
            elevation: 4

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

class MessageBubble(MDCard):
    text = StringProperty()
    is_user = BooleanProperty()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class GeminiApp:
    def __init__(self):
        try:
            self._url = config_reader.get_config_value('route')  # API host from config
            self.app = MDApp.get_running_app()
            self.root = None
            self.settings_dialog = None
        except Exception as e:
            print(e)

    def build(self):
        try:
            # Builder.load_string(CHAT_KV)
            self.root = Builder.load_string(CHAT_KV)
            self.app.gemini_app = self  # Reference into main app
            return self.root
        except Exception as e:
            print(e)

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
            # API call to Gemini
            url = f"http://{self._url}:5000/gemini"
            
            # Use the authorized request via httpservice
            payload = {"message": message}
            response = httpservice.post(url, json=payload)
            
            if response.ok:
                reply = response.json().get("response", self.app.lang_conv.get_value('error_no_response'))
                # Update UI on main thread
                Clock.schedule_once(lambda dt: self._add_chat_message(reply, is_user=False), 0)
            else:
                error_msg = response.json().get("error", self.app.lang_conv.get_value('unknown_error'))
                Clock.schedule_once(lambda dt: self._add_chat_message(
                    f"API Error: {error_msg}", is_user=False), 0)
        except Exception as e:
            # Handle connection errors
            err =e
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
        self.root.ids.chat_messages.add_widget(message)
        
        # Scroll to bottom after message is added (with a small delay to ensure proper rendering)
        Clock.schedule_once(lambda dt: self._scroll_to_bottom(), 0.1)
    
    def _scroll_to_bottom(self):
        """Scroll the chat to the bottom to see the latest messages"""
        scroll_view = self.root.ids.scroll_view
        scroll_view.scroll_y = 0
    
    def back_to_menu(self):
        self.app.back_to_menu()
    
    def show_settings_dialog(self):
        Dialog.show_settings_dialog(self)