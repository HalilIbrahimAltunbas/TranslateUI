from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import Screen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout


KV = '''
MDScreen:
    md_bg_color: 1, 1, 1, 1

    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(20)
        padding: dp(20)

        MDLabel:
            text: "Çeviri Uygulaması"
            halign: "center"
            theme_text_color: "Primary"
            font_style: "H5"

        MDTextField:
            id: input_text
            hint_text: "Çevrilecek metni gir"
            mode: "rectangle"
            size_hint_x: 0.9
            pos_hint: {"center_x": 0.5}

        MDRaisedButton:
            text: "Çevir"
            size_hint_x: 0.5
            pos_hint: {"center_x": 0.5}
            on_release: app.translate_text()

        MDLabel:
            id: output_text
            text: "Çeviri sonucu burada görünecek"
            halign: "center"
            theme_text_color: "Secondary"
            font_style: "H6"
'''

class Text_Page(MDApp):
    def build(self):
        return Builder.load_string(KV)

    def translate_text(self):
        input_text = self.root.ids.input_text.text
        translated_text = f'"{input_text}" çevirildi!'  # Burada gerçek API ile çeviri yapabilirsin.
        self.root.ids.output_text.text = translated_text

Text_Page().run()
