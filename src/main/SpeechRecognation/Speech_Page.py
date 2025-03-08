from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.behaviors.elevation import CommonElevationBehavior
from kivy.lang import Builder
import threading
from os.path import join, exists
import requests
from kivymd.uix.snackbar import Snackbar
import os
import platform
import wave
import tempfile

# Platform kontrolü
IS_ANDROID = platform.system() == "Android" or os.path.exists("/sdcard")

# Android için sınıflar sadece Android'de import edilecek
if IS_ANDROID:
    from jnius import autoclass
    MediaRecorder = autoclass('android.media.MediaRecorder')
    AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
    OutputFormat = autoclass('android.media.MediaRecorder$OutputFormat')
    AudioEncoder = autoclass('android.media.MediaRecorder$AudioEncoder')
    file_path = join('/sdcard', 'DCIM')
else:
    # Windows için PyAudio kullanacağız
    import pyaudio
    import wave
    file_path = tempfile.gettempdir()  # Geçici dosya dizini

KV = '''
<RecordCard>:
    orientation: "vertical"
    padding: "16dp"
    size_hint: None, None
    size: "280dp", "180dp"
    pos_hint: {"center_x": .5, "center_y": .5}
    elevation: 4
    radius: [12]
    
    MDLabel:
        id: status_label
        text: "Butona basıp konuşabilirsiniz."
        halign: "center"
        theme_text_color: "Primary"
        font_style: "Subtitle1"
        size_hint_y: None
        height: self.texture_size[1]
        
    MDLabel:
        id: error_label
        text: ""
        halign: "center"
        theme_text_color: "Error"
        font_style: "Caption"
        size_hint_y: None
        height: self.texture_size[1]

    Widget:
        size_hint_y: 0.1

    MDBoxLayout:
        spacing: "10dp"
        size_hint_y: None
        height: "48dp"
        pos_hint: {"center_x": .5}
        
        MDRaisedButton:
            id: start_button
            text: "Konuşmayı Başlat"
            on_release: app.start_recording()
            md_bg_color: app.theme_cls.primary_color
            
        MDRaisedButton:
            id: stop_button
            text: "Durdur"
            disabled: True
            on_release: app.stop_recording()
            md_bg_color: app.theme_cls.accent_color

MDScreen:
    md_bg_color: app.theme_cls.bg_normal
    
    MDBoxLayout:
        orientation: "vertical"
        padding: "16dp"
        spacing: "12dp"
        
        MDTopAppBar:
            title: "Ses Tanıma Uygulaması"
            right_action_items: [["cog", lambda x: app.show_settings_dialog()]]
            elevation: 4
        
        RecordCard:
            id: record_card
            
        Widget:
'''

class RecordCard(MDCard, CommonElevationBehavior):
    pass

class SpeechApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._url = "127.0.0.1"  # Varsayılan olarak localhost
        self.recording = False
        self.recorder = None
        self.settings_dialog = None
        
        # Windows için ses kaydetme değişkenleri
        if not IS_ANDROID:
            self.frames = []
            self.audio = None
            self.stream = None
            self.CHUNK = 1024
            self.FORMAT = pyaudio.paInt16
            self.CHANNELS = 1
            self.RATE = 44100
            self.output_filename = join(file_path, "test.wav")

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Red"
        self.theme_cls.theme_style = "Light"
        return Builder.load_string(KV)
    
    def start_recording(self):
        try:
            if IS_ANDROID:
                # Android için kayıt işlemi
                self.recorder = MediaRecorder()
                self.recorder.setAudioSource(AudioSource.MIC)
                self.recorder.setOutputFormat(OutputFormat.THREE_GPP)
                self.recorder.setAudioEncoder(AudioEncoder.AMR_NB)
                self.recorder.setOutputFile(join(file_path, "test.3gp"))
                
                self.recorder.prepare()
                self.recorder.start()
            else:
                # Windows için kayıt işlemi
                self.frames = []
                self.audio = pyaudio.PyAudio()
                self.stream = self.audio.open(format=self.FORMAT,
                                              channels=self.CHANNELS,
                                              rate=self.RATE,
                                              input=True,
                                              frames_per_buffer=self.CHUNK)
                
                # Ses kaydı için ayrı bir thread başlat
                self.recording = True
                threading.Thread(target=self._record_windows).start()
            
            self.root.ids.record_card.ids.status_label.text = "Dinleniyor..."
            self.root.ids.record_card.ids.status_label.theme_text_color = "Primary"
            self.root.ids.record_card.ids.start_button.disabled = True
            self.root.ids.record_card.ids.stop_button.disabled = False
            
        except Exception as e:
            self.root.ids.record_card.ids.error_label.text = f"Hata: {e}"
    
    def _record_windows(self):
        """Windows için ses kayıt işlemi."""
        try:
            while self.recording:
                data = self.stream.read(self.CHUNK)
                self.frames.append(data)
        except Exception as e:
            def update_error(dt):
                self.root.ids.record_card.ids.error_label.text = f"Kayıt hatası: {e}"
            from kivy.clock import Clock
            Clock.schedule_once(update_error, 0)
            
    def stop_recording(self):
        try:
            if IS_ANDROID:
                if self.recorder:
                    self.recorder.stop()
                    self.recorder.release()
                    self.recorder = None
                file_to_upload = join(file_path, "test.3gp")
            else:
                # Windows kayıt durdurma
                self.recording = False
                if self.stream:
                    self.stream.stop_stream()
                    self.stream.close()
                
                if self.audio:
                    # Kaydedilen sesi dosyaya yaz
                    wf = wave.open(self.output_filename, 'wb')
                    wf.setnchannels(self.CHANNELS)
                    wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                    wf.setframerate(self.RATE)
                    wf.writeframes(b''.join(self.frames))
                    wf.close()
                    self.audio.terminate()
                
                file_to_upload = self.output_filename
                
            self.root.ids.record_card.ids.status_label.text = "Kaydedilen ses işleniyor..."
            self.root.ids.record_card.ids.stop_button.disabled = True
            
            # Ses dosyasını sunucuya yükle
            threading.Thread(target=self.upload_voice, args=(file_to_upload,)).start()
            
        except Exception as e:
            self.root.ids.record_card.ids.error_label.text = f"Kayıt durdurma hatası: {e}"

    def upload_voice(self, file_path_to_upload=None):
        try:
            if not file_path_to_upload:
                file_path_to_upload = join(file_path, "test.3gp" if IS_ANDROID else "test.wav")
                
            url = f"http://{self._url}:5000/detect-text-from-voice"
            response = self.get(url, file_path_to_upload)
            
            # UI güncellemelerini ana thread'de yap
            def update_ui(dt):
                self.root.ids.record_card.ids.status_label.text = f"Algılanan Metin: {response}"
                self.root.ids.record_card.ids.start_button.disabled = False
                
            from kivy.clock import Clock
            Clock.schedule_once(update_ui, 0)
            return response
            
        except Exception as e:
            def update_error(dt):
                self.root.ids.record_card.ids.error_label.text = f"Yükleme hatası: {e}"
                self.root.ids.record_card.ids.start_button.disabled = False
                
            from kivy.clock import Clock
            Clock.schedule_once(update_error, 0)

    def get(self, url, file_path1):
        try:
            with open(file_path1, 'rb') as file:
                response = requests.post(url, files={'file': file})
                
            if response.ok:
                return response.json().get('text', 'Metin algılanamadı')
            else:
                return f"Hata: {response.json().get('error', 'Bilinmeyen hata')}"
                
        except Exception as e:
            return f"İstek hatası: {e}"

    def show_settings_dialog(self):
        if not self.settings_dialog:
            self.settings_field = MDTextField(
                hint_text="Sunucu IP adresi",
                text=self._url,
                mode="rectangle",
            )
            
            self.settings_dialog = MDDialog(
                title="Ayarlar",
                type="custom",
                content_cls=MDBoxLayout(
                    self.settings_field,
                    orientation="vertical",
                    spacing="12dp",
                    size_hint_y=None,
                    height="80dp",
                    padding=["24dp", "0dp", "24dp", "0dp"]
                ),
                buttons=[
                    MDRaisedButton(
                        text="İPTAL",
                        on_release=lambda x: self.settings_dialog.dismiss()
                    ),
                    MDRaisedButton(
                        text="KAYDET",
                        on_release=lambda x: self.save_settings()
                    ),
                ],
            )
        self.settings_dialog.open()
    
    def save_settings(self):
        self._url = self.settings_field.text
        self.settings_dialog.dismiss()
        Snackbar(
            text="Ayarlar kaydedildi",
            snackbar_x="10dp",
            snackbar_y="10dp",
            size_hint_x=0.7,
            bg_color=self.theme_cls.primary_color,
        ).open()
        
if __name__ == "__main__":
    SpeechApp().run()