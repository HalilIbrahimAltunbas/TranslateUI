import base64
from io import BytesIO
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.graphics.texture import Texture
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.fitimage import FitImage
from kivy.uix.camera import Camera
from kivy.uix.relativelayout import RelativeLayout
from PIL import Image
import requests
from os.path import join
from kivy.core.image import Image as CoreImage

# Çekilen görüntüyü geçici olarak kaydetmek için
DCIM = join('/sdcard', 'DCIM')

KV = """
MDBoxLayout:
    orientation: "vertical"

    MDTopAppBar:
        title: "AI Translator"
        elevation: 5
        pos_hint: {"top": 1}
    
    RelativeLayout:
        id: camera_layout
        size_hint_y: 0.5
        opacity: 1
        


    MDBoxLayout:
        id: image_layout
        size_hint_y: 0.5
        size_hint_x: None
        opacity: 0  # Başlangıçta gizli

    MDBoxLayout:
        adaptive_height: True
        padding: "10dp"
        spacing: "10dp"
        
        MDRaisedButton:
            text: "Capture"
            on_release: app.capture_image()
        
        MDRaisedButton:
            text: "Send"
            on_release: app.upload_image()
            disabled: True
            id: send_button
        
        MDRaisedButton:
            text: "Camera"
            on_release: app.activate_camera()
            disabled: True
            id: cam_button

    MDBoxLayout:
        id: result_box
        padding: "10dp"
        adaptive_height: True
        opacity: 0  # Başlangıçta gizli

        MDCard:
            size_hint: None, None
            size: "280dp", "120dp"
            elevation: 5
            padding: "10dp"

            MDLabel:
                id: result_label
                text: "Detected text will appear here."
                halign: "center"
                theme_text_color: "Secondary"
"""

class TranslateApp(MDApp):
    def build(self):
        self._url = "1.1.2.147"
        self.root = Builder.load_string(KV)

        # Kamera bileşeni ekleyelim
        self.camera = Camera()#resolution=(-1,-1), allow_stretch=True)
        self.root.ids.camera_layout.add_widget(self.camera)
        self.camera.play = True

        return self.root

    def capture_image(self):
        """Kameradan fotoğraf çeker ve gösterir"""
        try:
            
             #
            texture = self.camera.texture
            image_data = texture.pixels
            image_size = (texture.width, texture.height)


            canvas_img = Image.frombytes(mode='RGBA', size=image_size, data=image_data)
            # canvas_img = canvas_img.transpose(Image.FLIP_TOP_BOTTOM)
            data = BytesIO()
            canvas_img.save(data, format='png')
            data.seek(0) 
            im = CoreImage(BytesIO(data.read()), ext='png')
            
            # image.save(DCIM + "/translate.png")

            # Kamera gizlenir, çekilen resim gösterilir
            
            self.root.ids.camera_layout.opacity = 0
            self.root.ids.camera_layout.height = 0
            self.root.ids.image_layout.opacity = 1
            
            
            # Resmi UI'ye ekle
            # image_widget = FitImage(source=DCIM + "/translate.png")
            self.image_widget = FitImage(source = im.texture)
            self.image_widget.size_hint = (None,None)
            self.image_widget.pos_hint = {'top':0.5,'right':0.5}

            # print(self.image_widget.Properties)
        
            self.root.ids.image_layout.clear_widgets()
            self.root.ids.image_layout.add_widget(self.image_widget)
            # self.image_widget =

            # Butonları güncelle
            self.root.ids.send_button.disabled = False
            self.root.ids.cam_button.disabled = False
            
        except Exception as e:
            self.root.ids.result_label.text = f"Error: {e}"
            print(e)

    def upload_image(self):
        """Resmi API'ye gönderir ve sonucu gösterir"""
        file_path = DCIM + "/translate.png"
        url = f"http://{self._url}:5000/detect-text"
        response_text = self.get(url, file_path)

        # Çeviri sonucunu ekrana yaz
        self.root.ids.result_label.text = f"Detected Text: {response_text}"
        self.root.ids.result_box.opacity = 1  # Çeviri sonucunu görünür yap

    def activate_camera(self):
        """Kamerayı yeniden açar ve resmi kaldırır"""
        self.root.ids.camera_layout.opacity = 1
        self.root.ids.image_layout.opacity = 0
        self.root.ids.result_box.opacity = 0

        self.root.ids.send_button.disabled = True
        self.root.ids.cam_button.disabled = True

    def get(self, url, file_path):
        """API'ye istek atar ve sonucu döndürür"""
        with open(file_path, 'rb') as file:
            response = requests.post(url, files={'image': file})

        if response.ok:
            return response.json().get('text', 'No text detected')
        else:
            return f"Error: {response.json().get('error', 'Unknown error')}"

if __name__ == '__main__':
    TranslateApp().run()
