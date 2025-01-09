# components/login.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.app import App

class LoginScreen(BoxLayout):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.orientation = 'vertical'
        self.padding = dp(20)
        self.spacing = dp(10)
        
        self.app = App.get_running_app()
        self.styles = self.app.get_common_styles()
        
        # Title
        self.add_widget(Label(
            text='Login to Inventory System',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(24),
            color=self.styles['colors']['text']
        ))
        
        # Username input
        self.username_input = TextInput(
            hint_text='Username',
            size_hint_y=None,
            height=dp(40),
            multiline=False,
            write_tab=False,
            background_color=self.styles['colors']['surface'],
            foreground_color=self.styles['colors']['text'],
            padding=[dp(10), dp(10), 0, 0]
        )
        self.add_widget(self.username_input)
        
        # Password input
        self.password_input = TextInput(
            hint_text='Password',
            size_hint_y=None,
            height=dp(40),
            multiline=False,
            password=True,
            write_tab=False,
            background_color=self.styles['colors']['surface'],
            foreground_color=self.styles['colors']['text'],
            padding=[dp(10), dp(10), 0, 0]
        )
        self.add_widget(self.password_input)
        
        # Login button
        self.login_button = Button(
            text='Login',
            size_hint_y=None,
            height=dp(50),
            background_normal='',
            background_color=self.styles['colors']['primary'],
            color=self.styles['colors']['text']
        )
        self.login_button.bind(on_press=self.attempt_login)
        self.add_widget(self.login_button)
        
        # Error message label
        self.error_label = Label(
            text='',
            color=self.styles['colors']['error'],
            size_hint_y=None,
            height=dp(30)
        )
        self.add_widget(self.error_label)
        
        # Center the form
        self.add_widget(BoxLayout())  # Adds space at bottom

    def attempt_login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        
        if not username or not password:
            self.error_label.text = 'Please enter both username and password'
            return
            
        # Build MongoDB connection string
        connection_string = f"mongodb+srv://{username}:{password}@cluster0.ce09o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        
        # Try to connect
        try:
            self.callback(connection_string)
        except Exception as e:
            self.error_label.text = 'Invalid credentials'