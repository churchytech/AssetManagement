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
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.app import App
import os
from datetime import datetime

class ExportInterface(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(15)
        self.padding = dp(20)
        
        # Get app instance and styles
        self.app = App.get_running_app()
        self.styles = self.app.get_common_styles()
        
        # Initialize message label (needs to be created before setup_interface)
        self.message_label = Label(
            text='',
            size_hint_y=None,
            height=dp(40),
            color=self.styles['colors']['text']
        )

        # Setup the export interface
        self.setup_interface()

    def setup_interface(self):
        """Create the export interface layout."""
        # Title
        self.add_widget(Label(
            text='Export Inventory Data',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(20),
            color=self.styles['colors']['text']
        ))

        # File name input section
        filename_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(80),
            spacing=dp(5)
        )

        filename_layout.add_widget(Label(
            text='Export Filename:',
            size_hint_y=None,
            height=dp(30),
            color=self.styles['colors']['text'],
            halign='left'
        ))

        # Generate default filename
        default_filename = f"inventory_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        self.filename_input = TextInput(
            text=default_filename,
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            background_color=self.styles['colors']['surface'],
            foreground_color=self.styles['colors']['text'],
            padding=[dp(10), dp(10)]
        )
        filename_layout.add_widget(self.filename_input)
        self.add_widget(filename_layout)

        # Stats preview
        self.stats_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(10),
            padding=[0, dp(10)],
            height=dp(150)
        )

        self.stats_layout.add_widget(Label(
            text='Export Preview:',
            size_hint_y=None,
            height=dp(30),
            color=self.styles['colors']['text'],
            halign='left'
        ))

        # Update stats preview
        self.update_stats_preview()
        self.add_widget(self.stats_layout)

        # Export button
        export_button = Button(
            text='Export to CSV',
            size_hint=(None, None),
            size=(dp(200), dp(50)),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=self.styles['colors']['primary'],
            color=self.styles['colors']['text']
        )
        export_button.bind(on_press=self.perform_export)
        self.add_widget(export_button)

        # Add message label to layout
        self.add_widget(self.message_label)

    def update_stats_preview(self):
        """Update the statistics preview."""
        try:
            # Clear previous stats except title
            self.stats_layout.clear_widgets()
            self.stats_layout.add_widget(Label(
                text='Export Preview:',
                size_hint_y=None,
                height=dp(30),
                color=self.styles['colors']['text'],
                halign='left'
            ))

            # Get stats from database
            stats = self.app.get_database().get_statistics()

            # Add stats
            stats_text = [
                f"Total Items: {stats['total_items']}",
                f"Total Value: ${stats['total_value']:.2f}",
                f"Departments: {len(stats['items_by_department'])}",
                f"Item Conditions: {len(stats['items_by_condition'])}"
            ]

            for text in stats_text:
                self.stats_layout.add_widget(Label(
                    text=text,
                    size_hint_y=None,
                    height=dp(25),
                    color=self.styles['colors']['text_secondary'],
                    halign='left'
                ))

        except Exception as e:
            self.show_message(f"Error loading preview: {str(e)}", 'error')

    def perform_export(self, instance):
        """Execute the export operation."""
        try:
            filename = self.filename_input.text.strip()

            # Validate filename
            if not filename:
                raise ValueError("Please enter a filename")

            if not filename.endswith('.csv'):
                filename += '.csv'

            # Show progress message
            self.show_message('Exporting data...', 'info')

            # Perform export
            filepath = self.app.get_database().export_to_csv(filename)

            # Show success message with file path
            success_layout = BoxLayout(
                orientation='vertical',
                spacing=dp(10),
                padding=dp(10)
            )

            success_layout.add_widget(Label(
                text='✓ Export Successful!',
                color=self.styles['colors']['success'],
                font_size=dp(18)
            ))

            success_layout.add_widget(Label(
                text=f'File saved as:\n{os.path.abspath(filepath)}',
                color=self.styles['colors']['text'],
                font_size=dp(14)
            ))

            # Clear current widgets and show success
            self.clear_widgets()
            self.add_widget(success_layout)

            # Add return button
            return_button = Button(
                text='Export Another File',
                size_hint=(None, None),
                size=(dp(200), dp(50)),
                pos_hint={'center_x': 0.5},
                background_normal='',
                background_color=self.styles['colors']['primary'],
                color=self.styles['colors']['text']
            )
            return_button.bind(on_press=lambda x: self.setup_interface())
            self.add_widget(return_button)

        except Exception as e:
            self.show_message(str(e), 'error')

    def show_message(self, message, message_type='info'):
        """Display a message to the user."""
        color = {
            'success': self.styles['colors']['success'],
            'error': self.styles['colors']['error'],
            'info': self.styles['colors']['text']
        }.get(message_type, self.styles['colors']['text'])

        self.message_label.text = message
        self.message_label.color = color