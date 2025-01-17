"""
Inventory Management System
Created by Landon Robertshaw
Original code by Claude AI Assistant
Licensed under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/)

This code is part of the Inventory Management System, a project that provides
a user-friendly interface for managing inventory items with image support
and cloud database integration.

Created: January 2024
"""
# components/login.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.progressbar import ProgressBar
import threading


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
            text='Login to Inventory Management System',
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

        # Password container (for input + toggle button)
        password_container = BoxLayout(
            size_hint_y=None,
            height=dp(40),
            spacing=dp(5)
        )

        # Password input
        self.password_input = TextInput(
            hint_text='Password',
            size_hint=(1, None),
            height=dp(40),
            multiline=False,
            password=True,
            write_tab=False,
            background_color=self.styles['colors']['surface'],
            foreground_color=self.styles['colors']['text'],
            padding=[dp(10), dp(10), 0, 0]
        )

        self.visibility_button = Button(
            text='Show',
            size_hint=(None, None),
            size=(dp(50), dp(40)),
            background_normal='',
            background_color=self.styles['colors']['surface'],
            color=self.styles['colors']['text']
        )
        self.visibility_button.bind(on_press=self.toggle_password_visibility)

        password_container.add_widget(self.password_input)
        password_container.add_widget(self.visibility_button)

        self.add_widget(password_container)

        # Progress bar (initially hidden)
        self.progress = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height=dp(20)
        )
        self.progress.opacity = 0
        self.add_widget(self.progress)

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
        self.add_widget(BoxLayout())

        self.username_input.bind(on_text_validate=self.focus_password)
        self.password_input.bind(on_text_validate=self.attempt_login)

    def show_progress(self, show=True):
        """Show or hide progress bar and update button state."""
        self.progress.opacity = 1 if show else 0
        self.login_button.disabled = show
        if show:
            self.error_label.text = 'Connecting to database...'
            self.error_label.color = self.styles['colors']['text']
        Clock.schedule_interval(self.update_progress, 0.1) if show else Clock.unschedule(self.update_progress)

    def update_progress(self, dt):
        """Update progress bar animation."""
        self.progress.value = (self.progress.value + 5) % 100
        return True

    def attempt_login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()

        if not username or not password:
            self.error_label.text = 'Please enter both username and password'
            self.error_label.color = self.styles['colors']['error']
            return

        # Show progress and disable button
        self.show_progress()

        # Build MongoDB connection string
        connection_string = f"mongodb+srv://{username}:{password}@cluster0.ce09o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

        # Start connection in separate thread
        thread = threading.Thread(target=self.connect_to_db, args=(connection_string,))
        thread.daemon = True
        thread.start()

    def connect_to_db(self, connection_string):
        """Connect to database in background thread."""
        try:
            # Try to connect
            Clock.schedule_once(lambda dt: self.callback(connection_string))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_error('Invalid credentials'))
        finally:
            Clock.schedule_once(lambda dt: self.show_progress(False))

    def show_error(self, message):
        """Show error message."""
        self.error_label.text = message
        self.error_label.color = self.styles['colors']['error']

    def focus_password(self, instance):
        """Move focus to password field."""
        self.password_input.focus = True

    def toggle_password_visibility(self, instance):
        """Toggle password visibility."""
        self.password_input.password = not self.password_input.password
        self.visibility_button.text = 'Show' if self.password_input.password else 'Hide'