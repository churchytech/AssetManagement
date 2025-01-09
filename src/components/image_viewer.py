# components/image_viewer.py
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.core.image import Image as CoreImage
from kivy.app import App
import io
import os
from kivy.uix.filechooser import FileChooserListView


class ImageViewer(Popup):
    def __init__(self, asset_id, **kwargs):
        super().__init__(**kwargs)
        self.asset_id = asset_id
        self.app = App.get_running_app()
        self.styles = self.app.get_common_styles()

        self.title = f'Image Viewer - {asset_id}'
        self.size_hint = (0.8, 0.8)

        # Main layout
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        # Image display
        self.image_display = Image(
            size_hint=(1, 0.9),
            fit_mode='contain'  # Replaces allow_stretch and keep_ratio
        )
        content.add_widget(self.image_display)

        # Button layout
        button_layout = BoxLayout(
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )

        # Add image button
        self.add_button = Button(
            text='Add/Change Image',
            size_hint_x=0.5,
            background_normal='',
            background_color=self.styles['colors']['primary'],
            color=self.styles['colors']['text']
        )
        self.add_button.bind(on_press=self.show_file_chooser)
        button_layout.add_widget(self.add_button)

        # Remove image button
        self.remove_button = Button(
            text='Remove Image',
            size_hint_x=0.5,
            background_normal='',
            background_color=self.styles['colors']['error'],
            color=self.styles['colors']['text']
        )
        self.remove_button.bind(on_press=self.remove_image)
        button_layout.add_widget(self.remove_button)

        content.add_widget(button_layout)
        self.content = content

        # Load image if exists
        self.load_image()

    def load_image(self):
        """Load image from database."""
        try:
            image_data = self.app.get_database().get_image(self.asset_id)
            if image_data:
                # Convert binary data to Kivy image
                data = io.BytesIO(image_data)
                img = CoreImage(data, ext='png')
                self.image_display.texture = img.texture
                self.remove_button.disabled = False
            else:
                self.image_display.source = ''
                self.remove_button.disabled = True
        except Exception as e:
            print(f"Error loading image: {e}")

    def show_file_chooser(self, instance):
        """Show file chooser popup."""
        content = BoxLayout(orientation='vertical')

        # File chooser
        file_chooser = FileChooserListView(
            path=os.path.expanduser("~"),
            filters=['*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp']
        )
        content.add_widget(file_chooser)

        # Buttons
        button_layout = BoxLayout(
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )

        # Select button
        select_button = Button(
            text='Select',
            size_hint_x=0.5,
            background_normal='',
            background_color=self.styles['colors']['success'],
            color=self.styles['colors']['text']
        )

        # Cancel button
        cancel_button = Button(
            text='Cancel',
            size_hint_x=0.5,
            background_normal='',
            background_color=self.styles['colors']['error'],
            color=self.styles['colors']['text']
        )

        button_layout.add_widget(select_button)
        button_layout.add_widget(cancel_button)
        content.add_widget(button_layout)

        # Create popup
        file_popup = Popup(
            title='Choose Image',
            content=content,
            size_hint=(0.9, 0.9)
        )

        def on_select(instance):
            if file_chooser.selection:
                self.add_image(file_chooser.selection[0])
                file_popup.dismiss()

        select_button.bind(on_press=on_select)
        cancel_button.bind(on_press=file_popup.dismiss)

        file_popup.open()

    def add_image(self, file_path):
        """Add or update image in database."""
        try:
            self.app.get_database().add_image(self.asset_id, file_path)
            self.load_image()
        except Exception as e:
            error_popup = Popup(
                title='Error',
                content=Label(text=str(e)),
                size_hint=(0.6, 0.3)
            )
            error_popup.open()

    def remove_image(self, instance):
        """Remove image from database."""
        try:
            self.app.get_database().remove_image(self.asset_id)
            self.image_display.source = ''
            self.remove_button.disabled = True
        except Exception as e:
            error_popup = Popup(
                title='Error',
                content=Label(text=str(e)),
                size_hint=(0.6, 0.3)
            )
            error_popup.open()