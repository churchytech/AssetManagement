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
# utils/file_chooser.py
from tkinter import Tk, filedialog
import os


def choose_image():
    """Open native file dialog for image selection."""
    root = Tk()
    root.withdraw()  # Hide the main window

    filetypes = (
        ('Image files', '*.png *.jpg *.jpeg *.gif *.bmp'),
        ('All files', '*.*')
    )

    file_path = filedialog.askopenfilename(
        title='Choose an image',
        initialdir=os.path.expanduser("~"),
        filetypes=filetypes
    )

    root.destroy()
    return file_path if file_path else None