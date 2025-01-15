# components/add_item.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.app import App
from utils.file_chooser import choose_image
import os


class LabeledInput(BoxLayout):
    def __init__(self, label_text, input_widget, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(40)
        self.spacing = dp(10)

        # Label
        self.label = Label(
            text=label_text,
            size_hint_x=0.3,
            halign='right',
            valign='middle'
        )
        self.label.bind(size=self.label.setter('text_size'))

        # Input (TextInput or Spinner)
        input_widget.size_hint_x = 0.7

        self.add_widget(self.label)
        self.add_widget(input_widget)


class AddItemForm(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(20)
        self.spacing = dp(10)

        self.app = App.get_running_app()
        self.styles = self.app.get_common_styles()
        self.selected_image_path = None

        self.setup_form()

    def setup_form(self):
        # Title
        self.add_widget(Label(
            text='Add New Item',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(20)
        ))

        # Main container
        main_container = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None
        )
        main_container.bind(minimum_height=main_container.setter('height'))

        # Form fields
        self.inputs = {}
        fields = [
            ('Asset ID', 'Enter asset ID', False),
            ('Item Name', 'Enter item name', False),
            ('Description', 'Enter description', True),
            ('Location', 'Enter location', False),
            ('Department', 'Enter department', False),
            ('Purchase Price', '0.00', False),
            ('Quantity', '1', False),  # Add this line
            ('Model Number', 'Enter model number', False),
            ('Serial Number', 'Enter serial number', False)
        ]

        for field, hint, is_multiline in fields:
            if is_multiline:
                input_widget = TextInput(
                    hint_text=hint,
                    multiline=True,
                    height=dp(100),
                    size_hint_y=None,
                    background_color=self.styles['colors']['surface'],
                    foreground_color=self.styles['colors']['text']
                )
                container = LabeledInput(field, input_widget)
                container.height = dp(100)
            else:
                input_kwargs = {
                    'hint_text': hint,
                    'multiline': False,
                    'background_color': self.styles['colors']['surface'],
                    'foreground_color': self.styles['colors']['text']
                }
                if field == 'Purchase Price':
                    input_kwargs['input_filter'] = 'float'
                input_widget = TextInput(**input_kwargs)
                container = LabeledInput(field, input_widget)

            self.inputs[field] = input_widget
            main_container.add_widget(container)

        # Dropdowns
        for field, values in [
            ('Condition', ['New', 'Good', 'Fair', 'Poor']),
            ('Status', ['Available', 'In Use', 'Under Maintenance', 'Retired'])
        ]:
            spinner = Spinner(
                text=values[0],
                values=values,
                background_normal='',
                background_color=self.styles['colors']['primary'],
                color=self.styles['colors']['text']
            )
            container = LabeledInput(field, spinner)
            self.inputs[field] = spinner
            main_container.add_widget(container)

        # Image section
        image_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(200),
            spacing=dp(10)
        )

        self.image_preview = Image(
            size_hint_y=None,
            height=dp(150),
            fit_mode='contain'
        )
        image_container.add_widget(self.image_preview)

        # Image buttons
        button_container = BoxLayout(
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )

        self.choose_image_button = Button(
            text='Choose Image',
            size_hint_x=0.5,
            background_normal='',
            background_color=self.styles['colors']['primary']
        )
        self.choose_image_button.bind(on_press=self.select_image)

        self.remove_image_button = Button(
            text='Remove Image',
            size_hint_x=0.5,
            background_normal='',
            background_color=self.styles['colors']['error'],
            disabled=True
        )
        self.remove_image_button.bind(on_press=self.remove_image)

        button_container.add_widget(self.choose_image_button)
        button_container.add_widget(self.remove_image_button)
        image_container.add_widget(button_container)

        main_container.add_widget(image_container)

        # Submit button container for centering
        submit_container = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            padding=[0, dp(10)]
        )

        # Submit button
        submit_button = Button(
            text='Submit',
            size_hint=(None, None),
            size=(dp(200), dp(40)),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=self.styles['colors']['success']
        )
        submit_button.bind(on_press=self.submit_form)

        submit_container.add_widget(submit_button)
        main_container.add_widget(submit_container)

        # Add scroll view
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(main_container)
        self.add_widget(scroll)

    def select_image(self, instance):
        """Open native file dialog to select an image."""
        image_path = choose_image()
        if image_path:
            self.selected_image_path = image_path
            self.image_preview.source = image_path
            self.remove_image_button.disabled = False

    def remove_image(self, instance):
        """Remove the selected image."""
        self.selected_image_path = None
        self.image_preview.source = ''
        self.remove_image_button.disabled = True

    def submit_form(self, instance):
        try:
            db = self.app.get_database()

            db.add_item(
                asset_id=self.inputs['Asset ID'].text.strip(),
                item_name=self.inputs['Item Name'].text.strip(),
                description=self.inputs['Description'].text.strip(),
                location=self.inputs['Location'].text.strip(),
                department=self.inputs['Department'].text.strip(),
                purchase_price=float(self.inputs['Purchase Price'].text or 0),
                quantity=int(self.inputs['Quantity'].text or 1),  # Add this line
                condition=self.inputs['Condition'].text,
                model_number=self.inputs['Model Number'].text.strip(),
                serial_number=self.inputs['Serial Number'].text.strip(),
                status=self.inputs['Status'].text
            )

            if self.selected_image_path:
                db.add_image(self.inputs['Asset ID'].text.strip(), self.selected_image_path)

            self.clear_form()
            self.show_message("Item added successfully!", 'success')

        except Exception as e:
            self.show_message(str(e), 'error')

    def clear_form(self):
        for input_field in self.inputs.values():
            if isinstance(input_field, TextInput):
                input_field.text = ''
            elif isinstance(input_field, Spinner):
                input_field.text = input_field.values[0]

        self.selected_image_path = None
        self.image_preview.source = ''
        self.remove_image_button.disabled = True

    def show_message(self, message, message_type='info'):
        self.clear_widgets()
        message_label = Label(
            text=message,
            color=self.styles['colors'][message_type],
            size_hint_y=None,
            height=dp(40)
        )
        self.add_widget(message_label)

        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.setup_form(), 2)