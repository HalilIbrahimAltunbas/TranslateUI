# word_game_page.py - Ana Menü ile kullanılması için kelime bilme oyunu modülü
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.behaviors.elevation import CommonElevationBehavior
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
import threading
import requests
from kivymd.uix.progressbar import MDProgressBar

from config import config_reader
from Service.HttpService import httpservice

# Word Game KV
WORD_GAME_KV = '''
<GameCard>:
    orientation: "vertical"
    padding: "16dp"
    size_hint: None, None
    size: "320dp", "300dp"
    pos_hint: {"center_x": .5, "center_y": .5}
    elevation: 4
    radius: [12]

    MDLabel:
        id: question_label
        text: "Oyun başlatılıyor..."
        halign: "center"
        theme_text_color: "Primary"
        font_style: "H6"
        size_hint_y: None
        height: self.texture_size[1]

    MDLabel:
        id: instruction_label
        text: "Boşlukları doğru harflerle doldurun"
        halign: "center"
        theme_text_color: "Secondary"
        font_style: "Caption"
        size_hint_y: None
        height: self.texture_size[1]

    Widget:
        size_hint_y: 0.05

    MDBoxLayout:
        id: letter_boxes
        orientation: "horizontal"
        spacing: "4dp"
        size_hint_y: None
        height: "50dp"
        pos_hint: {"center_x": .5}

    Widget:
        size_hint_y: 0.1

    MDLabel:
        id: result_label
        text: ""
        halign: "center"
        theme_text_color: "Secondary"
        font_style: "Subtitle1"
        size_hint_y: None
        height: self.texture_size[1]

    MDLabel:
        id: score_label
        text: "Puan: 0"
        halign: "center"
        theme_text_color: "Primary"
        font_style: "Subtitle2"
        size_hint_y: None
        height: self.texture_size[1]

    MDProgressBar:
        id: timer_bar
        value: 100
        size_hint_y: None
        height: "6dp"

    Widget:
        size_hint_y: 0.1

    MDBoxLayout:
        spacing: "10dp"
        size_hint_y: None
        height: "48dp"
        pos_hint: {"center_x": .5}

        MDRaisedButton:
            id: next_button
            text: "Sonraki Soru"
            disabled: True
            on_release: app.word_game.next_question()
            md_bg_color: app.theme_cls.primary_color

        MDRaisedButton:
            id: restart_button
            text: "Yeniden Başlat"
            on_release: app.word_game.start_game()
            md_bg_color: app.theme_cls.accent_color

<LetterInput>:
    size_hint: None, None
    size: "40dp", "40dp"
    multiline: False
    input_filter: None
    font_size: "20sp"
    halign: "center"
    write_tab: False
    background_color: 1, 1, 1, 1
    background_normal: ""
    foreground_color: 0, 0, 0, 1
    max_length: 1

MDScreen:
    name: "word_game"

    MDBoxLayout:
        orientation: "vertical"
        padding: "16dp"
        spacing: "12dp"

        MDTopAppBar:
            title: "Kelime Bilme Oyunu"
            left_action_items: [["arrow-left", lambda x: app.back_to_menu()]]
            right_action_items: [["cog", lambda x: app.word_game.show_settings_dialog()]]
            elevation: 4

        GameCard:
            id: game_card

        Widget:
'''

class GameCard(MDCard, CommonElevationBehavior):
    pass

class LetterInput(TextInput):
    def __init__(self, **kwargs):
        self.next_input = None
        self.app = MDApp.get_running_app()

        super(LetterInput, self).__init__(**kwargs)

    def keyboard_on_key_up(self, window, keycode):
        print(self.app.word_game._url)
        if keycode[1] in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' and len(self.text) >= 1:
            self.text = keycode[1].upper()
            if self.next_input:
                next_inputs = [inp for inp in self.parent.children if isinstance(inp, LetterInput) and not inp.disabled]
                next_inputs.reverse()
                current_index = next_inputs.index(self)
                if current_index < len(next_inputs) - 1:  
                    next_inputs[current_index + 1].focus = True
                else:
                    self.app.word_game.check_answer()
            else :
                self.app.word_game.check_answer()
                # self.next_input.focus = True
                
            return True
        # Backspace tuşuna basıldığında bir önceki kutucuğa geç
        elif keycode[1] == 'backspace' and not self.text:
            # Bu, silme tuşuna basıldığında bir önceki TextInput'a odaklanır
            prev_inputs = [inp for inp in self.parent.children if isinstance(inp, LetterInput) and not inp.disabled]
            current_index = prev_inputs.index(self)
            if current_index < len(prev_inputs) - 1:  # Eğer ilk kutucuk değilse
                prev_inputs[current_index + 1].focus = True
            return True
        return super().keyboard_on_key_up(window, keycode)


    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        
        if keycode[1] == "enter" and not self.app.word_game.root.ids.game_card.ids.next_button.disabled:
            self.app.word_game.next_question()
        return super(LetterInput, self).keyboard_on_key_down(window, keycode, text, modifiers)

    

from components.SettingsModal import Dialog

class WordGameApp:
    def __init__(self):
        self._url = config_reader.get_config_value('route')
        self.current_question = None
        self.questions = []
        self.score = 0
        self.question_index = 0
        self.timer = None
        self.timer_value = 100
        self.settings_dialog = None
        self.letter_inputs = []
        self.app = MDApp.get_running_app()
        self.root = None

    def build(self):
        self.root = Builder.load_string(WORD_GAME_KV)
        # Ana uygulamada kullanılabilmek için kendimize bir referans koy
        self.app.word_game = self
        return self.root

    def start_game(self):
        """Oyunu başlat, soruları API'den al"""
        self.score = 0
        self.question_index = 0
        self.root.ids.game_card.ids.score_label.text = f"Puan: {self.score}"
        self.root.ids.game_card.ids.result_label.text = ""

        # Soruları API'den almak için ayrı bir thread başlat
        threading.Thread(target=self.fetch_questions).start()

    def fetch_questions(self):
        """API'den soruları al"""
        try:
            url = f"http://{self._url}:5000/quiz/quiz"
            # response = requests.get(url)
            response = httpservice.get(url)
            print(response)

            if response.ok:
                self.questions = response.json()
                # Ana thread'de UI'ı güncelle
                Clock.schedule_once(lambda dt: self.load_question(), 0)
            else:
                # Hata durumunda UI'ı güncelle
                Clock.schedule_once(lambda dt: self.update_error(f"Sorular alınamadı: {response.json().get('error', 'Bilinmeyen hata')}"), 0)

        except Exception as e:
            print(e)
            # Bağlantı hatası durumunda
            # Clock.schedule_once(lambda dt: self.update_error(f"Bağlantı hatası: {e}"), 0)
            # Test soruları yükle (gerçek uygulamada kaldırılabilir)
            self.questions = [
                {"soru": "E_a__le", "cevap": "Example"},
                {"soru": "P_t_on", "cevap": "Python"},
                {"soru": "M__ile", "cevap": "Mobile"}
            ]
            Clock.schedule_once(lambda dt: self.load_question(), 0)

    def update_error(self, error_message):
        """Hata mesajını göster"""
        self.root.ids.game_card.ids.question_label.text = "Hata!"
        self.root.ids.game_card.ids.instruction_label.text = error_message

    def load_question(self):
        """Yeni bir soru yükle"""
        if self.question_index < len(self.questions):
            self.current_question = self.questions[self.question_index]
            self.root.ids.game_card.ids.question_label.text = f"Soru {self.question_index + 1}/{len(self.questions)}"

            # Harf kutucuklarını temizle
            letter_box = self.root.ids.game_card.ids.letter_boxes
            letter_box.clear_widgets()
            self.letter_inputs = []

            # Soru formatına göre harf kutucukları oluştur
            word = self.current_question["soru"]
            answer = self.current_question["cevap"]

            # Her harf için input oluştur
            for i, char in enumerate(word):
                text_input = LetterInput(readonly=(char != '_'))
                if char != '_':
                    text_input.text = char
                    text_input.disabled = True
                self.letter_inputs.append(text_input)
                letter_box.add_widget(text_input)

            # TextInput'ların birbirine bağlanması
            for i in range(len(self.letter_inputs) - 1):
                self.letter_inputs[i].next_input = self.letter_inputs[i + 1]

            # İlk boş kutucuğa odaklan
            for input_box in self.letter_inputs:
                if input_box.text == '':
                    input_box.focus = True
                    break

            # Zamanı sıfırla ve zamanlayıcıyı başlat
            self.reset_timer()

            # Sonuç etiketini temizle ve düğme durumlarını ayarla
            self.root.ids.game_card.ids.result_label.text = ""
            self.root.ids.game_card.ids.next_button.disabled = True
        else:
            # Tüm sorular bittiğinde
            self.root.ids.game_card.ids.question_label.text = "Oyun Bitti!"
            self.root.ids.game_card.ids.instruction_label.text = f"Toplam puanınız: {self.score}"
            self.root.ids.game_card.ids.letter_boxes.clear_widgets()

    def reset_timer(self):
        """Zaman sayacını sıfırla ve başlat"""
        if self.timer:
            self.timer.cancel()

        self.timer_value = 100
        self.root.ids.game_card.ids.timer_bar.value = 100
        self.timer = Clock.schedule_interval(self.update_timer, 0.1)

    def update_timer(self, dt):
        """Zaman sayacını güncelle"""
        self.timer_value -= 0.5
        self.root.ids.game_card.ids.timer_bar.value = self.timer_value

        if self.timer_value <= 0:
            self.timer.cancel()
            self.check_answer(timeout=True)

    def check_answer(self, timeout=False):
        """Kullanıcının cevabını kontrol et"""
        if self.timer:
            self.timer.cancel()

        user_answer = ""
        for input_box in self.letter_inputs:
            user_answer += input_box.text

        correct_answer = self.current_question["cevap"]

        if timeout:
            self.root.ids.game_card.ids.result_label.text = f"Süre doldu! Doğru cevap: {correct_answer}"
            self.root.ids.game_card.ids.result_label.theme_text_color = "Error"
        elif user_answer.upper() == correct_answer.upper():
            # Doğru cevap, puan ekle
            self.score += int(self.timer_value / 10)  # Kalan süreye göre puan ver
            self.root.ids.game_card.ids.score_label.text = f"Puan: {self.score}"
            self.root.ids.game_card.ids.result_label.text = "Doğru Cevap!"
            self.root.ids.game_card.ids.result_label.theme_text_color = "Custom"
            self.root.ids.game_card.ids.result_label.text_color = (0, 0.7, 0, 1)  # Yeşil
        else:
            self.root.ids.game_card.ids.result_label.text = f"Yanlış! Doğru cevap: {correct_answer}"
            self.root.ids.game_card.ids.result_label.theme_text_color = "Error"

        # Tüm giriş kutularını salt okunur yap
        for input_box in self.letter_inputs:
            input_box.readonly = True

        # Sonraki soru düğmesini etkinleştir
        self.root.ids.game_card.ids.next_button.disabled = False

    def next_question(self):
        """Bir sonraki soruya geç"""
        self.question_index += 1
        self.load_question()

    def show_settings_dialog(self):
        Dialog.show_settings_dialog(self)