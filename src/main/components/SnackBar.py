from kivymd.uix.snackbar.snackbar import MDSnackbar,MDLabel
from kivy.utils import get_hex_from_color

class SnackBar :
    
    
    def callSnackBar(text,bg_color):
        MDSnackbar(
            MDLabel(
                text=text,
            ),
            # snackbar_x="10dp",
            # snackbar_y="10dp",
            size_hint_x=0.7,
            md_bg_color = get_hex_from_color(bg_color)
        ).open()

    