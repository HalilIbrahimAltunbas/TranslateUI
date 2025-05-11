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
import tempfile
from Registiration import AuthClient

from config import config_reader

IS_ANDROID = platform.system() == "Android" or os.path.exists("/sdcard")

if IS_ANDROID:
    from jnius import autoclass
    MediaRecorder = autoclass('android.media.MediaRecorder')
    AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
    OutputFormat = autoclass('android.media.MediaRecorder$OutputFormat')
    AudioEncoder = autoclass('android.media.MediaRecorder$AudioEncoder')
    file_path = join('/sdcard', 'DCIM')
else:
    import pyaudio
    import wave
    file_path = tempfile.gettempdir()

# Speech App KV
SPEECH_KV = '''
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
        text: app.lang_conv.get_value('speech_instruction')
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
            text: app.lang_conv.get_value('speech_start_recording')
            on_release: app.speech_app.start_recording()
            md_bg_color: app.theme_cls.primary_color

        MDRaisedButton:
            id: stop_button
            text: app.lang_conv.get_value('speech_stop_recording')
            disabled: True
            on_release: app.speech_app.stop_recording()
            md_bg_color: app.theme_cls.accent_color

MDScreen:
    name: "speech_app"

    MDBoxLayout:
        orientation: "vertical"
        padding: "16dp"
        spacing: "12dp"

        MDTopAppBar:
            title: app.lang_conv.get_value('speech_recognition_app')
            left_action_items: [["arrow-left", lambda x: app.back_to_menu()]]
            right_action_items: [["cog", lambda x: app.speech_app.show_settings_dialog()]]
            elevation: 4

        RecordCard:
            id: record_card

        Widget:
'''

class RecordCard(MDCard, CommonElevationBehavior):    
    pass

class SpeechApp:
    def __init__(self):
        self._url = config_reader.get_config_value('route')#"127.0.0.1" default localhost
        self.recording = False
        self.recorder = None
        self.settings_dialog = None
        self.app = MDApp.get_running_app()
        self.root = None


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
        try:
            
                
            self.root = Builder.load_string(SPEECH_KV) 
            print(self.root.ids.record_card.children)
            self.app.speech_app = self
            return self.root
        except Exception as e:
            print(e)

    def start_recording(self):
        try:
            if IS_ANDROID:
                # Record for Android
                self.recorder = MediaRecorder()
                self.recorder.setAudioSource(AudioSource.MIC)
                self.recorder.setOutputFormat(OutputFormat.THREE_GPP)
                self.recorder.setAudioEncoder(AudioEncoder.AMR_NB)
                self.recorder.setOutputFile(join(file_path, "test.3gp"))

                self.recorder.prepare()
                self.recorder.start()
            else:
                # Record for Windows
                self.frames = []
                self.audio = pyaudio.PyAudio()
                self.stream = self.audio.open(format=self.FORMAT,
                                              channels=self.CHANNELS,
                                              rate=self.RATE,
                                              input=True,
                                              frames_per_buffer=self.CHUNK)

                # initiation a new thread for voice record process
                self.recording = True
                threading.Thread(target=self._record_windows).start()

            self.root.ids.record_card.ids.status_label.text = self.app.lang_conv.get_value('speech_listening')
            self.root.ids.record_card.ids.status_label.theme_text_color = "Primary"
            self.root.ids.record_card.ids.start_button.disabled = True
            self.root.ids.record_card.ids.stop_button.disabled = False

        except Exception as e:
            self.root.ids.record_card.ids.error_label.text = f"Error: {e}"

    def _record_windows(self):
        try:
            while self.recording:
                data = self.stream.read(self.CHUNK)
                self.frames.append(data)
        except Exception as e:
            def update_error(dt):
                self.root.ids.record_card.ids.error_label.text = f"{self.app.lang_conv.get_value('record_error')}: {e}"
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
                self.recording = False
                if self.stream:
                    self.stream.stop_stream()
                    self.stream.close()

                if self.audio:
                    wf = wave.open(self.output_filename, 'wb')
                    wf.setnchannels(self.CHANNELS)
                    wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                    wf.setframerate(self.RATE)
                    wf.writeframes(b''.join(self.frames))
                    wf.close()
                    self.audio.terminate()

                file_to_upload = self.output_filename

            self.root.ids.record_card.ids.status_label.text =self.app.lang_conv.get_value('speech_processing')
            self.root.ids.record_card.ids.stop_button.disabled = True

            threading.Thread(target=self.upload_voice, args=(file_to_upload,)).start()

        except Exception as e:
            self.root.ids.record_card.ids.error_label.text = f"{self.app.lang_conv.get_value('stop_recording_error')}: {e}"

    def upload_voice(self, file_path_to_upload=None):
        try:
            if not file_path_to_upload:
                file_path_to_upload = join(file_path, "test.3gp" if IS_ANDROID else "test.wav")

            url = f"http://{self._url}:5000/voice"
            response = self.get(url, file_path_to_upload)


            def update_ui(dt):
                self.root.ids.record_card.ids.status_label.text = f"{self.app.lang_conv.get_value('speech_detected_text')}: {response}"
                self.root.ids.record_card.ids.start_button.disabled = False

            from kivy.clock import Clock
            Clock.schedule_once(update_ui, 0)
            return response

        except Exception as e:
            def update_error(dt):
                self.root.ids.record_card.ids.error_label.text = f"{self.app.lang_conv.get_value('download_error')}: {e}"
                self.root.ids.record_card.ids.start_button.disabled = False

            from kivy.clock import Clock
            Clock.schedule_once(update_error, 0)

    def get(self, url, file_path1):
        try:
            with open(file_path1, 'rb') as file:
                response = requests.post(url,  headers = {"Authorization": f"Bearer {AuthClient.auth_client.get_token()}"} ,files={'file': file})

            if response.ok:
                return response.json().get('text', self.app.lang_conv.get_value('no_text_detected'))
            else:
                return f"Error: {response.json().get('error', self.app.lang_conv.get_value('unknown_error'))}"

        except Exception as e:
            return f"{self.app.lang_conv.get_value('download_error')}: {e}"

    def show_settings_dialog(self):
        from components.SettingsModal import Dialog
        Dialog.show_settings_dialog(self)
