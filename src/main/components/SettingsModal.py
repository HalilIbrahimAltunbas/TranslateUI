class Dialog:
    def show_settings_dialog(self):
        """Ayarlar dialogunu gösterir"""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.textfield import MDTextField
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.button import MDRaisedButton
        
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
                        on_release=lambda x: Dialog.save_settings(self)
                    ),
                ],
            )
        self.settings_dialog.open()
        
    def save_settings(self):
        """Ayarları kaydeder"""
        from components.SnackBar import SnackBar 
        self._url = self.settings_field.text
        self.settings_dialog.dismiss()
        SnackBar.callSnackBar(text="Ayarlar kaydedildi",bg_color=self.app.theme_cls.primary_color)
        