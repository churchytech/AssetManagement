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
# main.py
from kivy.config import Config

# This must be done before any other kivy imports
Config.set('input', 'mouse', 'mouse,disable_multitouch')
#Config.set('modules', 'monitor', '')
Config.set('kivy', 'kivy_clock', 'default')

from kivy.core.window import Window
from kivy.resources import resource_add_path
from app import InventoryApp
import os
import sys


def main():
    # Set minimum window size
    Window.minimum_width = 800
    Window.minimum_height = 600

    # Set dark theme background
    Window.clearcolor = (0.1, 0.1, 0.1, 1)

    # Set the window icon
    if os.path.exists('icon.ico'):
        Window.set_icon('icon.ico')

    # Initialize and run the application
    app = InventoryApp()
    app.run()


if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    main()