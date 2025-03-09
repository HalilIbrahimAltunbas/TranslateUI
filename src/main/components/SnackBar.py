from kivymd.uix.snackbar.snackbar import MDSnackbar,MDLabel

class SnackBar :
    def callSnackBar(text,bg_color):
        MDSnackbar(
            MDLabel(
                text=text,
            ),
            snackbar_x="10dp",
            snackbar_y="10dp",
            size_hint_x=0.7,
            _md_bg_color=bg_color
        ).open()