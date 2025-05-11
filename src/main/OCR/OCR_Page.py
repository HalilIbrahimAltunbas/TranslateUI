from io import BytesIO
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.app import MDApp  
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.uix.camera import Camera
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics.context_instructions import Rotate
from PIL import Image
import requests
from os.path import join
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image as kivyImg
import os
import platform
import tempfile
from config import config_reader
from Service.HttpService import httpservice
from Registiration import AuthClient

IS_ANDROID = platform.system() == "Android" or os.path.exists("/sdcard")

if IS_ANDROID:
    DCIM = join('/sdcard', 'DCIM')
else:
    DCIM = tempfile.gettempdir()  

OCR_KV = """
MDScreen:
    name: "ocr_app"

    MDBoxLayout:
        orientation: "vertical"
        
        MDTopAppBar:
            title: app.lang_conv.get_value('ocr_app')
            left_action_items: [["arrow-left", lambda x: app.ocr_app.back_to_menu()]]
            right_action_items: [["cog", lambda x: app.ocr_app.show_settings_dialog()]]
            elevation: 4

        RelativeLayout:
            id: camera_layout
            # position_hint: (.5,.5)
            # size_hint: (1,None)

        MDBoxLayout:
            id: content_layout
            orientation: "vertical"
            padding: "16dp"
            spacing: "12dp"
            
            MDBoxLayout:
                adaptive_height: True
                padding: "10dp"
                spacing: "10dp"
                
                MDRaisedButton:
                    text: "Capture"
                    on_release: app.ocr_app.capture_image()
                    id: capture_button
                
                MDRaisedButton:
                    text: "Send"
                    on_release: app.ocr_app.upload_image()
                    disabled: True
                    id: send_button
                
                MDRaisedButton:
                    text: "Camera"
                    on_release: app.ocr_app.activate_camera()
                    disabled: True
                    id: cam_button
            
            MDCard:
                size_hint_y: None
                height: "120dp"
                padding: "16dp"
                spacing: "8dp"
                elevation: 4
                radius: [12]
                
                MDLabel:
                    id: result_label
                    text: app.lang_conv.get_value('ocr_detected_text')
                    halign: "center"
                    theme_text_color: "Secondary"
"""

class RotatedCamera(Camera):
    """Extends the Camera class to handle rotation for Android devices"""
    def __init__(self, **kwargs):
        super(RotatedCamera, self).__init__(**kwargs)
        # Set rotation for Android - will be applied to the texture
        self.rotation = 90 if IS_ANDROID else 0
        
    def _camera_loaded(self, *largs):
        super(RotatedCamera, self)._camera_loaded(*largs)
        # Apply rotation to the texture on Android
        if IS_ANDROID and self._camera:
            self.texture = self._camera.texture
            self.texture_size = self.texture.size

class OCRApp:
    def __init__(self):
        self._url = config_reader.get_config_value('route')
        self.app = MDApp.get_running_app()
        self.root = None
        self.camera = None
        self.image_widget = None
        self.captured_image_data = None
        self.settings_dialog = None
        
    def back_to_menu(self):
        self.deactivate_camera()
        if self.camera:
            self.camera.on_play(self.camera, False)
        self.app.back_to_menu()
        
    def build(self):
        self.root = Builder.load_string(OCR_KV)
        
        #Reference into main app
        self.app.ocr_app = self
        
        # Use RotatedCamera instead of Camera
        self.camera = Camera(play=True, resolution=(-1,-1), allow_stretch=True)
        if IS_ANDROID:
        # Texture'ı döndür
            
            self.camera.canvas.before.add(Rotate(angle=270, axis=(0, 0, 1),  origin=self.camera.center))
            self.camera.pos[0] -= 300
            self.camera.pos[1] += 30
        self.root.ids.camera_layout.add_widget(self.camera)
        
        return self.root
        
    def capture_image(self):
        try:
            texture = self.camera.texture
            image_data = texture.pixels
            image_size = (texture.width, texture.height)
            
            # For rotated camera on Android, we may need to process the image differently
            canvas_img = Image.frombytes(mode='RGBA', size=image_size, data=image_data)
            
            # Rotate the image if we're on Android
            if IS_ANDROID:
                canvas_img = canvas_img.rotate(-90, expand=True)
                
            data = BytesIO()
            canvas_img.save(data, format='png')
            data.seek(0)
            
            self.captured_image_data = BytesIO(data.getvalue())
            
            data.seek(0)
            im = CoreImage(BytesIO(data.read()), ext='png')
            
            self.image_widget = kivyImg()
            self.image_widget.texture = im.texture

            self.root.ids.camera_layout.clear_widgets()
            self.root.ids.camera_layout.add_widget(self.image_widget)
        
            self.root.ids.send_button.disabled = False
            self.root.ids.cam_button.disabled = False
            self.root.ids.capture_button.disabled = True

            self.deactivate_camera()
            
        except Exception as e:
            self.root.ids.result_label.text = f"{self.app.lang_conv.get_value('error')}: {e}"
            print(e)
    
    def deactivate_camera(self):
        self.root.ids.send_button.disabled = False
        self.root.ids.cam_button.disabled = False
        self.root.ids.capture_button.disabled = True

        if self.camera:
            self.camera.play = False
            
    def upload_image(self):
        try:
            if not self.captured_image_data:
                self.root.ids.result_label.text = f"{self.app.lang_conv.get_value('error')}: {self.app.lang_conv.get_value('no_image_detected')}"
                return
                
            url = f"http://{self._url}:5000/detect-text"
            
            self.captured_image_data.seek(0)
            
            response = requests.post(
                url,
                headers = {"Authorization": f"Bearer {AuthClient.auth_client.get_token()}"},  
                files={'image': ('image.png', self.captured_image_data, 'image/png')}
            )
            
            if response.ok:
                detected_text = response.json().get('text', self.app.lang_conv.get_value('_ocr_detected_text'))
                self.root.ids.result_label.text = f"{self.app.lang_conv.get_value('_ocr_detected_text')}: {detected_text}"
            else:
                error_msg = response.json().get('error', self.app.lang_conv.get_value('unknown_error'))
                self.root.ids.result_label.text = f"{self.app.lang_conv.get_value('error')}: {error_msg}"
                
        except Exception as e:
            self.root.ids.result_label.text = f"{self.app.lang_conv.get_value('request_error')}: {e}"
            
    def activate_camera(self):
        """Activate camera and make passive Image """
        self.root.ids.camera_layout.clear_widgets()
        self.root.ids.camera_layout.add_widget(self.camera)
        
        # deactivate Image layout
        self.root.ids.send_button.disabled = True
        self.root.ids.cam_button.disabled = True
        self.root.ids.capture_button.disabled = False

        # makes activate Camera
        if self.camera:
            self.camera.play = True
            
    def show_settings_dialog(self):
        from components.SettingsModal import Dialog
        Dialog.show_settings_dialog(self)