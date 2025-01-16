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
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.app import App
from kivy.graphics import Color, Rectangle
from .image_viewer import ImageViewer
from .edit_item import EditItemForm

class SearchInterface(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = dp(10)

        self.app = App.get_running_app()
        self.styles = self.app.get_common_styles()

        # Initialize pagination variables
        self.current_page = 1
        self.items_per_page = 20
        self.total_pages = 1

        self.setup_interface()

    def setup_interface(self):
        """Setup the main UI components."""
        # Title
        self.add_widget(Label(
            text='Search Inventory',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(20),
            color=self.styles['colors']['text']
        ))

        # Search bar container
        search_layout = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10),
            padding=[0, dp(5)]
        )

        # Search input
        self.search_input = TextInput(
            multiline=False,
            hint_text='Enter search term...',
            size_hint=(0.7, None),
            height=dp(40),
            background_color=self.styles['colors']['surface'],
            foreground_color=self.styles['colors']['text'],
            padding=[dp(10), dp(10)]
        )
        self.search_input.bind(
            on_text_validate=self.perform_search,
            focus=self.on_search_focus,
            text=self.on_search_text_change
        )
        search_layout.add_widget(self.search_input)

        # Search button
        search_button = Button(
            text='Search',
            size_hint=(0.3, None),
            height=dp(40),
            background_normal='',
            background_color=self.styles['colors']['primary'],
            color=self.styles['colors']['text']
        )
        search_button.bind(on_press=self.perform_search)
        search_layout.add_widget(search_button)

        self.add_widget(search_layout)

        # Results area
        self.results_scroll = ScrollView(size_hint=(1, 1))
        self.results_grid = GridLayout(
            cols=1,
            spacing=dp(10),
            size_hint_y=None,
            padding=dp(5)
        )
        self.results_grid.bind(minimum_height=self.results_grid.setter('height'))
        self.results_scroll.add_widget(self.results_grid)
        self.add_widget(self.results_scroll)

        # Pagination controls
        self.pagination_layout = BoxLayout(
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10),
            padding=[dp(10), dp(5)]
        )

        # Previous page button
        self.prev_button = Button(
            text='Previous',
            size_hint_x=None,
            width=dp(100),
            background_normal='',
            background_color=self.styles['colors']['primary'],
            color=self.styles['colors']['text'],
            disabled=True
        )
        self.prev_button.bind(on_press=self.previous_page)
        self.pagination_layout.add_widget(self.prev_button)

        # Page indicator
        self.page_label = Label(
            text='Page 1',
            size_hint_x=None,
            width=dp(100),
            color=self.styles['colors']['text']
        )
        self.pagination_layout.add_widget(self.page_label)

        # Next page button
        self.next_button = Button(
            text='Next',
            size_hint_x=None,
            width=dp(100),
            background_normal='',
            background_color=self.styles['colors']['primary'],
            color=self.styles['colors']['text'],
            disabled=True
        )
        self.next_button.bind(on_press=self.next_page)
        self.pagination_layout.add_widget(self.next_button)

        self.add_widget(self.pagination_layout)

    def perform_search(self, instance):
        """Execute search and display results."""
        self.results_grid.clear_widgets()
        search_term = self.search_input.text.strip()

        try:

        try:
            # Get paginated results
            results = self.app.get_database().search_items(
                search_term,
                page=self.current_page,
                per_page=self.items_per_page
            )

            # Update pagination info
            self.total_pages = results['total_pages']
            self.update_pagination_controls()

            if not results['items']:
                self.show_message('No items found')
                return

            # Add results count
            self.results_grid.add_widget(Label(
                text=f"Found {results['total_items']} item(s) - Page {self.current_page} of {self.total_pages}",
                color=self.styles['colors']['text'],
                size_hint_y=None,
                height=dp(30)
            ))

            # Display results
            for item in results['items']:
                self.add_result_card(item)

        except Exception as e:
            self.show_message(f'Error: {str(e)}')

    def add_result_card(self, item):
        """Create and add a result card for an item."""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(180),
            padding=dp(10),
            spacing=dp(5)
        )

        # Add background color
        with card.canvas.before:
            Color(*self.styles['colors']['surface'])
            self.rect = Rectangle(pos=card.pos, size=card.size)
        card.bind(pos=self._update_rect, size=self._update_rect)

        # Header with ID and Name
        header = BoxLayout(size_hint_y=None, height=dp(30))
        header.add_widget(Label(
            text=f"ID: {item['asset_id']}",
            bold=True,
            color=self.styles['colors']['primary'],
            size_hint_x=0.3
        ))
        header.add_widget(Label(
            text=item['item_name'],
            bold=True,
            color=self.styles['colors']['text'],
            size_hint_x=0.7,
            text_size=(None, dp(30)),
            halign='left',
            valign='middle',
            shorten=True
        ))
        card.add_widget(header)

        # Description
        desc = Label(
            text=item['description'] or "No description available",
            color=self.styles['colors']['text_secondary'],
            size_hint_y=None,
            height=dp(60),
            text_size=(card.width - dp(20), dp(60)),
            halign='left',
            valign='top'
        )
        card.add_widget(desc)

        # Location and Department
        info = Label(
            text=f"Location: {item['location'] or 'N/A'} | Department: {item['department'] or 'N/A'}",
            color=self.styles['colors']['text'],
            size_hint_y=None,
            height=dp(25)
        )
        card.add_widget(info)

        # Status, Condition, and Quantity
        status = Label(
            text=f"Status: {item['status']} | Condition: {item['condition']} | Quantity: {item.get('quantity', 1)}",
            color=self.styles['colors']['text'],
            size_hint_y=None,
            height=dp(25)
        )
        card.add_widget(status)

        # Buttons
        buttons = BoxLayout(
            size_hint_y=None,
            height=dp(30),
            spacing=dp(10)
        )

        # Edit button
        edit_btn = Button(
            text='Edit',
            size_hint_x=0.33,
            background_normal='',
            background_color=self.styles['colors']['primary'],
            color=self.styles['colors']['text']
        )
        edit_btn.bind(on_press=lambda x: self.show_edit_form(item))
        buttons.add_widget(edit_btn)

        # Image button
        image_btn = Button(
            text='View/Edit Image',
            size_hint_x=0.33,
            background_normal='',
            background_color=self.styles['colors']['primary'],
            color=self.styles['colors']['text']
        )
        image_btn.bind(on_press=lambda x: self.show_image_viewer(item))
        buttons.add_widget(image_btn)

        # Delete button
        delete_btn = Button(
            text='Delete',
            size_hint_x=0.33,
            background_normal='',
            background_color=self.styles['colors']['error'],
            color=self.styles['colors']['text']
        )
        delete_btn.bind(on_press=lambda x: self.confirm_delete(item))
        buttons.add_widget(delete_btn)

        card.add_widget(buttons)
        self.results_grid.add_widget(card)

    def update_pagination_controls(self):
        """Update pagination buttons state."""
        self.prev_button.disabled = self.current_page <= 1
        self.next_button.disabled = self.current_page >= self.total_pages
        self.page_label.text = f'Page {self.current_page} of {self.total_pages}'

    def previous_page(self, instance):
        """Go to previous page."""
        if self.current_page > 1:
            self.current_page -= 1
            self.perform_search(None)

    def next_page(self, instance):
        """Go to next page."""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.perform_search(None)

    def show_edit_form(self, item):
        """Display the edit form for an item."""
        edit_popup = EditItemForm(item)
        edit_popup.on_save_callback = self.refresh_search
        edit_popup.open()

    def show_image_viewer(self, item):
        """Display the image viewer for an item."""
        image_viewer = ImageViewer(item['asset_id'])
        image_viewer.open()

    def confirm_delete(self, item):
        """Show delete confirmation dialog."""
        content = BoxLayout(
            orientation='vertical',
            padding=dp(10),
            spacing=dp(10)
        )

        content.add_widget(Label(
            text=f'Are you sure you want to delete item {item["asset_id"]}?',
            color=self.styles['colors']['text']
        ))

        buttons = BoxLayout(
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )

        # Confirm button
        confirm_btn = Button(
            text='Delete',
            background_normal='',
            background_color=self.styles['colors']['error']
        )

        # Cancel button
        cancel_btn = Button(
            text='Cancel',
            background_normal='',
            background_color=self.styles['colors']['primary']
        )

        buttons.add_widget(confirm_btn)
        buttons.add_widget(cancel_btn)
        content.add_widget(buttons)

        popup = Popup(
            title='Confirm Delete',
            content=content,
            size_hint=(0.4, 0.3),
            background_color=self.styles['colors']['surface']
        )

        def delete_item(instance):
            try:
                self.app.get_database().delete_item(item['asset_id'])
                popup.dismiss()
                self.refresh_search()
            except Exception as e:
                popup.dismiss()
                error_popup = Popup(
                    title='Error',
                    content=Label(text=str(e)),
                    size_hint=(0.6, 0.3)
                )
                error_popup.open()

        confirm_btn.bind(on_press=delete_item)
        cancel_btn.bind(on_press=popup.dismiss)

        popup.open()

    def refresh_search(self):
        """Refresh the current search results."""
        self.perform_search(None)

    def show_message(self, message):
        """Display a message in the results area."""
        self.results_grid.clear_widgets()
        self.results_grid.add_widget(Label(
            text=message,
            color=self.styles['colors']['text'],
            size_hint_y=None,
            height=dp(40)
        ))

    def _update_rect(self, instance, value):
        """Update the background rectangle of a card."""
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*self.styles['colors']['surface'])
            Rectangle(pos=instance.pos, size=instance.size)

    def on_search_focus(self, instance, value):
        """Handle search input focus event."""
        if value:  # When focused
            self.perform_search(None)

    def on_search_text_change(self, instance, value):
        """Handle search text changes."""
        # Perform search after a short delay
        from kivy.clock import Clock
        Clock.unschedule(self._delayed_search)  # Cancel any pending search
        Clock.schedule_once(self._delayed_search, 0.5)  # Schedule new search

    def _delayed_search(self, dt):
        """Perform delayed search."""
        self.perform_search(None)