# components/edit_item.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.metrics import dp
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.core.window import Window


class EditItemForm(Popup):
    def __init__(self, item_data, **kwargs):
        super().__init__(**kwargs)
        self.item_data = item_data
        self.title = f'Edit Item: {item_data["asset_id"]}'

        # Make popup 90% of window size
        window_width = Window.width * 0.9
        window_height = Window.height * 0.9
        self.size = (window_width, window_height)
        self.size_hint = (None, None)  # Disable size_hint to use explicit size

        self.app = App.get_running_app()
        self.styles = self.app.get_common_styles()

        # Create main layout
        main_layout = BoxLayout(orientation='vertical', spacing=dp(10))

        # Create scroll view for form content
        scroll = ScrollView()
        self.form_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(20),
            size_hint_y=None
        )
        self.form_layout.bind(minimum_height=self.form_layout.setter('height'))

        # Fields definition with relative width calculations
        content_width = window_width - dp(60)  # Account for padding
        label_width = content_width * 0.2  # 20% for labels
        input_width = content_width * 0.75  # 75% for inputs (leaving 5% for spacing)

        fields = [
            ('Asset ID', 'Enter asset ID', dp(40), False),  # Add this line at the start
            ('Item Name', 'Enter item name', dp(40), False),
            ('Description', 'Enter description', dp(120), True),
            ('Location', 'Enter location', dp(40), False),
            ('Department', 'Enter department', dp(40), False),
            ('Purchase Price', '0.00', dp(40), False),
            ('Model Number', 'Enter model number', dp(40), False),
            ('Serial Number', 'Enter serial number', dp(40), False)
        ]

        # Create input fields
        self.inputs = {}

        for field, hint, height, is_multiline in fields:
            field_container = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=height + dp(10),
                spacing=dp(10)
            )

            # Label with calculated width
            label = Label(
                text=field,
                size_hint=(None, None),
                size=(label_width, height),
                halign='right',
                valign='middle',
                color=self.styles['colors']['text']
            )
            label.bind(size=label.setter('text_size'))
            field_container.add_widget(label)

            # Input field with calculated width
            if field == 'Description':
                self.inputs[field] = TextInput(
                    text=str(item_data.get(field.lower().replace(' ', '_'), '')),
                    multiline=True,
                    size_hint=(None, None),
                    size=(input_width, height),
                    background_color=self.styles['colors']['surface'],
                    foreground_color=self.styles['colors']['text'],
                    padding=[dp(10), dp(10)],
                    do_wrap=True  # Enable text wrapping
                )
            elif field == 'Purchase Price':
                self.inputs[field] = TextInput(
                    text=str(item_data.get(field.lower().replace(' ', '_'), '')),
                    multiline=False,
                    size_hint=(None, None),
                    size=(input_width, height),
                    input_filter='float',
                    background_color=self.styles['colors']['surface'],
                    foreground_color=self.styles['colors']['text'],
                    padding=[dp(10), dp(10)]
                )
            else:
                self.inputs[field] = TextInput(
                    text=str(item_data.get(field.lower().replace(' ', '_'), '')),
                    multiline=False,
                    size_hint=(None, None),
                    size=(input_width, height),
                    background_color=self.styles['colors']['surface'],
                    foreground_color=self.styles['colors']['text'],
                    padding=[dp(10), dp(10)]
                )
            field_container.add_widget(self.inputs[field])
            self.form_layout.add_widget(field_container)

        # Add dropdowns
        for field, values in [
            ('Condition', ['New', 'Good', 'Fair', 'Poor']),
            ('Status', ['Available', 'In Use', 'Under Maintenance', 'Retired'])
        ]:
            dropdown_container = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(40),
                spacing=dp(10)
            )

            label = Label(
                text=field,
                size_hint=(None, None),
                size=(label_width, dp(40)),
                halign='right',
                valign='middle',
                color=self.styles['colors']['text']
            )
            label.bind(size=label.setter('text_size'))
            dropdown_container.add_widget(label)

            current_value = item_data.get(field.lower(), values[0])
            self.inputs[field] = Spinner(
                text=current_value,
                values=values,
                size_hint=(None, None),
                size=(input_width, dp(40)),
                background_normal='',
                background_color=self.styles['colors']['primary'],
                color=self.styles['colors']['text']
            )
            dropdown_container.add_widget(self.inputs[field])
            self.form_layout.add_widget(dropdown_container)

        # Add form to scroll view
        scroll.add_widget(self.form_layout)
        main_layout.add_widget(scroll)

        # Buttons container
        buttons_container = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(20),
            padding=[dp(20), dp(10)]
        )

        # Save button
        save_button = Button(
            text='Save Changes',
            size_hint=(None, None),
            size=(dp(150), dp(40)),
            background_normal='',
            background_color=self.styles['colors']['success'],
            color=self.styles['colors']['text']
        )
        save_button.bind(on_press=self.save_changes)

        # Cancel button
        cancel_button = Button(
            text='Cancel',
            size_hint=(None, None),
            size=(dp(150), dp(40)),
            background_normal='',
            background_color=self.styles['colors']['error'],
            color=self.styles['colors']['text']
        )
        cancel_button.bind(on_press=self.dismiss)

        buttons_container.add_widget(save_button)
        buttons_container.add_widget(cancel_button)
        main_layout.add_widget(buttons_container)

        self.content = main_layout

    def save_changes(self, instance):
        try:
            db = self.app.get_database()

            # Check if asset ID has changed
            new_asset_id = self.inputs['Asset ID'].text.strip()
            old_asset_id = self.item_data['asset_id']

            if new_asset_id != old_asset_id:
                # Update asset ID first
                db.update_asset_id(old_asset_id, new_asset_id)
                # Update the rest of the data with new asset ID
                db.update_item(
                    new_asset_id,
                    item_name=self.inputs['Item Name'].text.strip(),
                    description=self.inputs['Description'].text.strip(),
                    location=self.inputs['Location'].text.strip(),
                    department=self.inputs['Department'].text.strip(),
                    purchase_price=float(self.inputs['Purchase Price'].text or 0),
                    condition=self.inputs['Condition'].text,
                    model_number=self.inputs['Model Number'].text.strip(),
                    serial_number=self.inputs['Serial Number'].text.strip(),
                    status=self.inputs['Status'].text
                )
            else:
                # Normal update without changing asset ID
                db.update_item(
                    old_asset_id,
                    item_name=self.inputs['Item Name'].text.strip(),
                    description=self.inputs['Description'].text.strip(),
                    location=self.inputs['Location'].text.strip(),
                    department=self.inputs['Department'].text.strip(),
                    purchase_price=float(self.inputs['Purchase Price'].text or 0),
                    condition=self.inputs['Condition'].text,
                    model_number=self.inputs['Model Number'].text.strip(),
                    serial_number=self.inputs['Serial Number'].text.strip(),
                    status=self.inputs['Status'].text
                )

            self.dismiss()
            if hasattr(self, 'on_save_callback'):
                self.on_save_callback()

        except Exception as e:
            error_popup = Popup(
                title='Error',
                content=Label(text=str(e)),
                size_hint=(0.6, 0.3)
            )
            error_popup.open()