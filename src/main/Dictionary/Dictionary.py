from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import MDList, OneLineListItem, TwoLineListItem, ThreeLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.behaviors.elevation import CommonElevationBehavior
from kivy.lang import Builder
import threading
import requests
from kivymd.uix.snackbar import Snackbar
# import json
from kivy.metrics import dp

from config import config_reader

# Dictionary App KV
DICTIONARY_KV = '''
<SearchCard>:
    orientation: "vertical"
    padding: "16dp"
    size_hint: None, None
    size: "280dp", "120dp"
    pos_hint: {"center_x": .5, "center_y": .5}
    elevation: 4
    radius: [12]

    MDTextField:
        id: search_field
        hint_text: app.lang_conv.get_value('dict_search_hint')
        helper_text: app.lang_conv.get_value('dict_search_helper')
        helper_text_mode: "on_focus"
        icon_right: "book-search"
        icon_right_color: app.theme_cls.primary_color
        size_hint_x: 1
        font_size: "18sp"
        on_text_validate: app.dictionary_app.search_word(self.text)

    MDLabel:
        id: error_label
        text: ""
        halign: "center"
        theme_text_color: "Error"
        font_style: "Caption"
        size_hint_y: None
        height: self.texture_size[1]

<WordCard>:
    orientation: "vertical"
    padding: "16dp"
    size_hint_y: None
    height: self.minimum_height
    elevation: 2
    radius: [8]
    
    MDBoxLayout:
        orientation: "horizontal"
        size_hint_y: None
        height: self.minimum_height
        padding: [0, "4dp"]
        
        MDLabel:
            id: word_label
            text: ""
            halign: "left"
            theme_text_color: "Primary"
            font_style: "H5"
            bold: True
            size_hint_y: None
            height: self.texture_size[1]
            
        MDIconButton:
            id: audio_button
            icon: "volume-high"
            on_release: app.dictionary_app.play_audio(self.audio_url)
            disabled: True
            pos_hint: {"center_y": .5}
    
    MDLabel:
        id: phonetic_label
        text: ""
        halign: "left"
        theme_text_color: "Secondary"
        font_style: "Subtitle1"
        size_hint_y: None
        height: self.texture_size[1]
        
    MDLabel:
        id: origin_label
        text: ""
        halign: "left"
        theme_text_color: "Secondary"
        font_style: "Body2"
        size_hint_y: None
        height: self.texture_size[1]

<MeaningCard>:
    orientation: "vertical"
    padding: "16dp"
    size_hint_y: None
    height: self.minimum_height
    elevation: 1
    radius: [8]
    
    MDLabel:
        id: part_of_speech
        text: ""
        theme_text_color: "Primary"
        font_style: "H6"
        italic: True
        size_hint_y: None
        height: self.texture_size[1]
        
    MDList:
        id: definitions_list
        size_hint_y: None
        height: self.minimum_height
        spacing: "4dp"

MDScreen:
    name: "dictionary_app"

    MDBoxLayout:
        orientation: "vertical"
        padding: "16dp"
        spacing: "12dp"

        MDTopAppBar:
            title: app.lang_conv.get_value('dictionary_app')
            left_action_items: [["arrow-left", lambda x: app.back_to_menu()]]
            right_action_items: [["cog", lambda x: app.dictionary_app.show_settings_dialog()]]
            elevation: 4

        SearchCard:
            id: search_card
            
        MDBoxLayout:
            id: result_container
            orientation: "vertical"
            spacing: "8dp"
            size_hint_y: 1
            
            ScrollView:
                id: scroll_view
                size_hint: 1, 1
                do_scroll_x: False
                bar_width: dp(4)
                
                MDBoxLayout:
                    id: results_box
                    orientation: "vertical"
                    spacing: "8dp"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [0, "8dp"]
'''

class SearchCard(MDCard, CommonElevationBehavior):
    pass

class WordCard(MDCard, CommonElevationBehavior):
    pass

class MeaningCard(MDCard, CommonElevationBehavior):
    pass

class DictionaryApp:
    def __init__(self):
        self._url = config_reader.get_config_value('route')  # "127.0.0.1" default localhost
        self.app = MDApp.get_running_app()
        self.settings_dialog = None
        self.root = None
        self.current_word_data = None

    def build(self):
        try:
            self.root = Builder.load_string(DICTIONARY_KV)
            self.app.dictionary_app = self
            return self.root
        except Exception as e:
            print(f"Error building dictionary app: {e}")
            
    def search_word(self, word):
        if not word or word.strip() == "":
            self.show_error(self.app.lang_conv.get_value('dict_empty_search'))
            return
            
        self.clear_results()
        self.show_loading()
        
        # Start search in background thread
        threading.Thread(target=self._search_word_thread, args=(word,)).start()
    
    def _search_word_thread(self, word):
        try:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            response = requests.get(url)
            
            if response.status_code == 200:
                word_data = response.json()
                
                # Using the Clock to update UI from the main thread
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: self.display_word_data(word_data[0]), 0)
            else:
                error_msg = response.json().get('error', self.app.lang_conv.get_value('unknown_error'))
                self.show_error(f"{self.app.lang_conv.get_value('dict_api_error')}: {error_msg}")
                
        except Exception as e:
            self.show_error(f"{self.app.lang_conv.get_value('dict_search_error')}: {str(e)}")
    
    def display_word_data(self, word_data):
        self.hide_loading()
        self.current_word_data = word_data
        
        if not word_data:
            self.show_error(self.app.lang_conv.get_value('dict_no_results'))
            return
            
        # Create word card
        word_card = WordCard()
        word_card.ids.word_label.text = word_data.get('word', '')
        word_card.ids.phonetic_label.text = word_data.get('phonetic', '')
        word_card.ids.origin_label.text = word_data.get('origin', '')
        
        # Check for audio
        audio_url = None
        for phonetic in word_data.get('phonetics', []):
            if phonetic.get('audio'):
                audio_url = phonetic.get('audio')
                break
                
        if audio_url:
            word_card.ids.audio_button.disabled = False
            word_card.ids.audio_button.audio_url = audio_url
        
        self.root.ids.results_box.add_widget(word_card)
        
        # Create meaning cards
        for meaning in word_data.get('meanings', []):
            meaning_card = MeaningCard()
            meaning_card.ids.part_of_speech.text = meaning.get('partOfSpeech', '')
            
            for definition in meaning.get('definitions', []):
                definition_text = definition.get('definition', '')
                example = definition.get('example', '')
                
                if example:
                    item = ThreeLineListItem(
                        text=f"• {definition_text}",
                        secondary_text=f"{self.app.lang_conv.get_value('dict_example')}: {example}",
                        tertiary_text=self._format_syn_ant(definition)
                    )
                elif definition.get('synonyms') or definition.get('antonyms'):
                    item = TwoLineListItem(
                        text=f"• {definition_text}",
                        secondary_text=self._format_syn_ant(definition)
                    )
                else:
                    item = OneLineListItem(text=f"• {definition_text}")
                
                meaning_card.ids.definitions_list.add_widget(item)
            
            self.root.ids.results_box.add_widget(meaning_card)
    
    def _format_syn_ant(self, definition):
        texts = []
        
        if definition.get('synonyms'):
            synonyms = ', '.join(definition.get('synonyms')[:5])  # Limit to 5 for display
            if synonyms:
                texts.append(f"{self.app.lang_conv.get_value('dict_synonyms')}: {synonyms}")
                
        if definition.get('antonyms'):
            antonyms = ', '.join(definition.get('antonyms')[:5])  # Limit to 5 for display
            if antonyms:
                texts.append(f"{self.app.lang_conv.get_value('dict_antonyms')}: {antonyms}")
                
        return '\n'.join(texts)
    
    def play_audio(self, audio_url):
        try:
            pass
            # from plyer import audio
            
            # # Download the audio file and play it
            # threading.Thread(target=self._download_and_play_audio, args=(audio_url,)).start()
            
        except Exception as e:
            self.show_error(f"{self.app.lang_conv.get_value('dict_audio_error')}: {str(e)}")
    
    def _download_and_play_audio(self, audio_url):
        try:
            # Implementation for downloading and playing audio
            # This is a placeholder and would need to be implemented based on your app's requirements
            pass
        except Exception as e:
            self.show_error(f"{self.app.lang_conv.get_value('dict_audio_error')}: {str(e)}")
    
    def clear_results(self):
        self.root.ids.results_box.clear_widgets()
    
    def show_loading(self):
        loading_label = MDLabel(
            text=self.app.lang_conv.get_value('dict_loading'),
            halign="center",
            theme_text_color="Primary",
            font_style="Subtitle1"
        )
        self.root.ids.results_box.add_widget(loading_label)
    
    def hide_loading(self):
        self.root.ids.results_box.clear_widgets()
    
    def show_error(self, error_message):
        from kivy.clock import Clock
        
        def update_error(dt):
            self.root.ids.search_card.ids.error_label.text = error_message
            
        Clock.schedule_once(update_error, 0)
    
    def show_settings_dialog(self):
        from components.SettingsModal import Dialog
        Dialog.show_settings_dialog(self)