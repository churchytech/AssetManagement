from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.metrics import dp
from kivy.app import App

class AddItemForm(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = dp(10)
        
        self.app = App.get_running_app()
        self.styles = self.app.get_common_styles()
        self.setup_form()
    
    def setup_form(self):
        """Create and setup the form layout."""
        scroll = ScrollView(size_hint=(1, 1))
        
        # Main container
        main_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(20),
            padding=dp(20)
        )
        main_layout.bind(minimum_height=main_layout.setter('height'))
        
        # Title
        main_layout.add_widget(Label(
            text='Add New Item',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(20),
            color=self.styles['colors']['text']
        ))
        
        # Create individual field containers instead of a grid
        self.inputs = {}
        
        # Fields definition with individual heights and multiline settings
        fields = [
            ('Asset ID', 'Enter Asset ID', dp(40), False),  # Updated hint text
            ('Item Name', 'Enter item name', dp(40), False),
            ('Description', 'Enter description', dp(100), True),
            ('Location', 'Enter location', dp(40), False),
            ('Department', 'Enter department', dp(40), False),
            ('Purchase Price', '0.00', dp(40), False),
            ('Model Number', 'Enter model number', dp(40), False),
            ('Serial Number', 'Enter serial number', dp(40), False)
        ]
        
        # Create each field with its own container
        for field, hint, height, is_multiline in fields:
            field_container = BoxLayout(
                size_hint_y=None,
                height=height + dp(20),  # Add padding
                spacing=dp(10)
            )
            
            # Label
            label = Label(
                text=field,
                size_hint_x=None,
                width=dp(150),
                halign='right',
                color=self.styles['colors']['text']
            )
            field_container.add_widget(label)
            
            # Input field
            if field == 'Purchase Price':
                self.inputs[field] = TextInput(
                    hint_text=hint,
                    multiline=is_multiline,
                    size_hint_y=None,
                    height=height,
                    input_filter='float',
                    background_color=self.styles['colors']['surface'],
                    foreground_color=self.styles['colors']['text'],
                    padding=(dp(10), dp(10))
                )
            else:
                self.inputs[field] = TextInput(
                    hint_text=hint,
                    multiline=is_multiline,
                    size_hint_y=None,
                    height=height,
                    background_color=self.styles['colors']['surface'],
                    foreground_color=self.styles['colors']['text'],
                    padding=(dp(10), dp(10))
                )
            field_container.add_widget(self.inputs[field])
            
            # Add the container to main layout
            main_layout.add_widget(field_container)
        
        # Add dropdowns
        for field, values in [
            ('Condition', ['New', 'Good', 'Fair', 'Poor']),
            ('Status', ['Available', 'In Use', 'Under Maintenance', 'Retired'])
        ]:
            dropdown_container = BoxLayout(
                size_hint_y=None,
                height=dp(40),
                spacing=dp(10)
            )
            
            label = Label(
                text=field,
                size_hint_x=None,
                width=dp(150),
                halign='right',
                color=self.styles['colors']['text']
            )
            dropdown_container.add_widget(label)
            
            self.inputs[field] = Spinner(
                text=values[0],
                values=values,
                background_normal='',
                background_color=self.styles['colors']['primary'],
                color=self.styles['colors']['text']
            )
            dropdown_container.add_widget(self.inputs[field])
            
            main_layout.add_widget(dropdown_container)
        
        # Submit button
        submit_button = Button(
            text='Submit',
            size_hint=(None, None),
            size=(dp(200), dp(50)),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=self.styles['colors']['success'],
            color=self.styles['colors']['text']
        )
        submit_button.bind(on_press=self.submit_form)
        
        button_container = BoxLayout(
            size_hint_y=None,
            height=dp(80),
            padding=dp(10)
        )
        button_container.add_widget(submit_button)
        main_layout.add_widget(button_container)
        
        scroll.add_widget(main_layout)
        self.add_widget(scroll)
    
    def submit_form(self, instance):
        """Handle form submission."""
        try:
            # Get database instance
            db = self.app.get_database()
            
            # Add item to database
            db.add_item(
                asset_id=self.inputs['Asset ID'].text.strip(),
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
            
            # Clear form and show success message
            self.clear_form()
            self.show_message("Item added successfully!", 'success')
            
        except Exception as e:
            self.show_message(str(e), 'error')
    
    def clear_form(self):
        """Clear all form inputs."""
        for input_field in self.inputs.values():
            if isinstance(input_field, TextInput):
                input_field.text = ''
            elif isinstance(input_field, Spinner):
                input_field.text = input_field.values[0]
    
    def show_message(self, message, message_type='info'):
        """Show a message to the user."""
        color = {
            'success': self.styles['colors']['success'],
            'error': self.styles['colors']['error'],
            'info': self.styles['colors']['text']
        }.get(message_type, self.styles['colors']['text'])
        
        self.clear_widgets()
        message_label = Label(
            text=message,
            color=color,
            size_hint_y=None,
            height=dp(40)
        )
        self.add_widget(message_label)
        
        # Re-setup form after short delay
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.setup_form(), 2)