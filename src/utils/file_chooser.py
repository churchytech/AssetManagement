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