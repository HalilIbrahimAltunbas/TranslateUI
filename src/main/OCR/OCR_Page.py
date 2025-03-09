# OCR_Page.py - OCR Modülü, Ana Menü ile kullanılmak üzere düzenlenmiş
from io import BytesIO
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.graphics.texture import Texture
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
# from kivymd.uix.fitimage import FitImage
from kivy.uix.camera import Camera
from kivy.uix.relativelayout import RelativeLayout
from PIL import Image
import requests
from os.path import join
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image as kivyImg
import os
import platform
import tempfile

# Platform kontrolü
IS_ANDROID = platform.system() == "Android" or os.path.exists("/sdcard")

# Dosya yolu ayarlaması
if IS_ANDROID:
    DCIM = join('/sdcard', 'DCIM')
else:
    DCIM = tempfile.gettempdir()  # Geçici dizin

# OCR App KV
OCR_KV = """
MDScreen:
    name: "ocr_app"
    
    MDBoxLayout:
        orientation: "vertical"
        
        MDTopAppBar:
            title: "OCR Uygulaması"
            left_action_items: [["arrow-left", lambda x: app.back_to_menu()]]
            right_action_items: [["cog", lambda x: app.ocr_app.show_settings_dialog()]]
            elevation: 4
        
        MDBoxLayout:
            id: content_layout
            orientation: "vertical"
            padding: "16dp"
            spacing: "12dp"
            
            RelativeLayout:
                id: camera_layout
                size_hint_y: 1
            
            # RelativeLayout:
            #     id: image_layout
            #     size_hint_y: 0.5
            #     opacity: 0  # Başlangıçta gizli
            
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
                    text: "Algılanan metin burada görünecek."
                    halign: "center"
                    theme_text_color: "Secondary"
"""

class OCRApp:
    def __init__(self):
        self._url = "127.0.0.1"  # Varsayılan olarak localhost
        self.app = MDApp.get_running_app()
        self.root = None
        self.camera = None
        self.image_widget = None
        self.captured_image_data = None
        self.settings_dialog = None
        
    def build(self):
        self.root = Builder.load_string(OCR_KV)
        
        # Ana uygulamada kullanılabilmek için kendimize bir referans koy
        self.app.ocr_app = self
        
        # Kamera bileşeni ekleyelim
        self.camera = Camera(play=True,resolution=(-1,-1),allow_stretch=True)
        self.root.ids.camera_layout.add_widget(self.camera)
        
        return self.root
        
    def capture_image(self):
        """Kameradan fotoğraf çeker ve gösterir"""
        try:
            # Kamera görüntüsünü al
            texture = self.camera.texture
            image_data = texture.pixels
            image_size = (texture.width, texture.height)
            
            # Görüntüyü PIL Image'a dönüştür
            canvas_img = Image.frombytes(mode='RGBA', size=image_size, data=image_data)
            data = BytesIO()
            canvas_img.save(data, format='png')
            data.seek(0)
            
            # Görüntüyü kaydet (upload için)
            self.captured_image_data = BytesIO(data.getvalue())
            
            # Görüntüyü CoreImage'a dönüştür (gösterim için)
            data.seek(0)
            im = CoreImage(BytesIO(data.read()), ext='png')
            
            # Kamera gizlenir, çekilen resim gösterilir
            # self.root.ids.camera_layout.opacity = 0
            # self.root.ids.image_layout.opacity = 1
            
            # Resmi UI'ye ekle
            self.image_widget = kivyImg()
            self.image_widget.texture = im.texture

            # self.image_widget.fit_mode = "contain" 
            
            

            self.root.ids.camera_layout.clear_widgets()
            self.root.ids.camera_layout.add_widget(self.image_widget)
            
            
            # Butonları güncelle
            self.root.ids.send_button.disabled = False
            self.root.ids.cam_button.disabled = False
            self.root.ids.capture_button.disabled =True
            
        except Exception as e:
            self.root.ids.result_label.text = f"Hata: {e}"
            print(e)
            
    def upload_image(self):
        """Resmi API'ye gönderir ve sonucu gösterir"""
        try:
            if not self.captured_image_data:
                self.root.ids.result_label.text = "Hata: Görüntü bulunamadı!"
                return
                
            url = f"http://{self._url}:5000/detect-text"
            
            # API'ye istek gönder
            self.captured_image_data.seek(0)
            response = requests.post(
                url, 
                files={'image': ('image.png', self.captured_image_data, 'image/png')}
            )
            
            if response.ok:
                detected_text = response.json().get('text', 'Metin algılanamadı')
                self.root.ids.result_label.text = f"Algılanan Metin: {detected_text}"
            else:
                error_msg = response.json().get('error', 'Bilinmeyen hata')
                self.root.ids.result_label.text = f"Hata: {error_msg}"
                
        except Exception as e:
            self.root.ids.result_label.text = f"İstek hatası: {e}"
            
    def activate_camera(self):
        """Kamerayı yeniden açar ve resmi kaldırır"""
        # self.root.ids.camera_layout.opacity = 1
        # self.root.ids.image_layout.opacity = 0

        self.root.ids.camera_layout.clear_widgets()
        self.root.ids.camera_layout.add_widget(self.camera)
        
        # Buttonu deaktif hale getir
        self.root.ids.send_button.disabled = True
        self.root.ids.cam_button.disabled = True
        self.root.ids.capture_button.disabled = False

        # Kamerayı yeniden aktif hale getir
        if self.camera:
            self.camera.play = True
            
    def show_settings_dialog(self):
        # from components.SettingsModal import Dialog
        # Dialog.show_settings_dialog(self)
        """Ayarlar dialogunu gösterir"""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.textfield import MDTextField
        from kivymd.uix.snackbar import Snackbar
        
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
        """Ayarları kaydeder"""
        # from kivymd.uix.snackbar import Snackbar
        from components.SnackBar import SnackBar 
        self._url = self.settings_field.text
        self.settings_dialog.dismiss()
        SnackBar.callSnackBar(text="Ayarlar kaydedildi",bg_color=self.app.theme_cls.primary_color)
        