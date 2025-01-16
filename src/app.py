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
# app.py
from kivy.app import App
from kivy.metrics import dp
from database import InventoryDatabase
from ui import InventoryUI
from components.login import LoginScreen
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout


class RootWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'


class InventoryApp(App):
    icon = 'icon.ico'

    def build(self):
        """Initialize the application and return the root widget."""
        Config.set('kivy', 'window_icon', 'icon.ico')

        # Create root widget
        self.root_widget = RootWidget()

        # Start with login screen
        self.login_screen = LoginScreen(callback=self.on_login_success)
        self.root_widget.add_widget(self.login_screen)

        return self.root_widget

    def on_login_success(self, connection_string):
        """Called when login is successful."""
        try:
            # Initialize database with connection string
            self.inventory_db = InventoryDatabase(connection_string)

            # Create the main UI
            main_ui = InventoryUI()

            # Switch to main UI
            self.root_widget.clear_widgets()
            self.root_widget.add_widget(main_ui)
        except Exception as e:
            # More specific error handling
            error_msg = str(e)
            if "Authentication failed" in error_msg:
                error_msg = "Invalid credentials. Please check your username and password."
            elif "connection" in error_msg.lower():
                error_msg = "Unable to connect to database. Please check your internet connection."
            self.login_screen.error_label.text = error_msg

    def get_database(self):
        """Get the database instance."""
        return self.inventory_db

    def on_stop(self):
        """Clean up resources when the application closes."""
        if hasattr(self, 'inventory_db'):
            if hasattr(self.inventory_db, 'client'):
                self.inventory_db.client.close()

    def get_common_styles(self):
        """Return common styles used throughout the application."""
        return {
            'button_style': {
                'size_hint_y': None,
                'height': dp(45),
                'background_normal': '',
                'background_color': (0.2, 0.6, 0.8, 1),
                'color': (1, 1, 1, 1)
            },
            'input_style': {
                'size_hint': (None, None),
                'size': (dp(400), dp(40)),
                'multiline': False,
                'background_color': (0.2, 0.2, 0.2, 1),
                'foreground_color': (1, 1, 1, 1),
                'padding': (dp(10), dp(10))
            },
            'label_style': {
                'size_hint': (None, None),
                'size': (dp(150), dp(40)),
                'halign': 'right',
                'valign': 'middle',
                'color': (0.9, 0.9, 0.9, 1)
            },
            'colors': {
                'primary': (0.2, 0.6, 0.8, 1),
                'success': (0.2, 0.8, 0.2, 1),
                'error': (0.8, 0.2, 0.2, 1),
                'background': (0.1, 0.1, 0.1, 1),
                'surface': (0.15, 0.15, 0.15, 1),
                'text': (0.9, 0.9, 0.9, 1),
                'text_secondary': (0.7, 0.7, 0.7, 1)
            }
        }