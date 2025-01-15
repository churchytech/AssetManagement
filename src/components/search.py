# components/search.py
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

class SearchInterface(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = dp(10)
        
        self.app = App.get_running_app()
        self.styles = self.app.get_common_styles()
        
        self.setup_interface()
    
    def setup_interface(self):
        self.add_widget(Label(
            text='Search Inventory',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(20),
            color=self.styles['colors']['text']
        ))
        
        search_layout = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10),
            padding=[0, dp(5)]
        )
        
        self.search_input = TextInput(
            multiline=False,
            hint_text='Enter search term...',
            size_hint=(0.7, None),
            height=dp(40),
            background_color=self.styles['colors']['surface'],
            foreground_color=self.styles['colors']['text'],
            padding=(dp(10), dp(10))
        )
        self.search_input.bind(on_text_validate=self.perform_search)
        search_layout.add_widget(self.search_input)
        
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

    def perform_search(self, instance):
        self.results_grid.clear_widgets()
        results = self.app.get_database().search_items(self.search_input.text)
        
        if not results:
            self.results_grid.add_widget(Label(
                text='No items found',
                color=self.styles['colors']['text'],
                size_hint_y=None,
                height=dp(40)
            ))
            return
            
        self.results_grid.add_widget(Label(
            text=f'Found {len(results)} item(s)',
            color=self.styles['colors']['text'],
            size_hint_y=None,
            height=dp(30)
        ))
        
        for item in results:
            self.add_result_card(item)

    def add_result_card(self, item):
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(180),
            padding=dp(10),
            spacing=dp(5)
        )
        
        with card.canvas.before:
            Color(*self.styles['colors']['surface'])
            self.rect = Rectangle(pos=card.pos, size=card.size)
        card.bind(pos=self._update_rect, size=self._update_rect)

        # Header with ID and Name
        header = BoxLayout(
            size_hint_y=None,
            height=dp(30)
        )
        
        id_label = Label(
            text=f"ID: {item['asset_id']}",
            bold=True,
            color=self.styles['colors']['primary'],
            size_hint_x=0.3
        )
        header.add_widget(id_label)
        
        name_label = Label(
            text=item['item_name'],
            bold=True,
            color=self.styles['colors']['text'],
            size_hint_x=0.7,
            text_size=(None, dp(30)),
            halign='left',
            valign='middle',
            shorten=True,
            shorten_from='right'
        )
        header.add_widget(name_label)
        card.add_widget(header)
        
        # Description with wrapping
        desc_label = Label(
            text=item['description'] or "No description available",
            color=self.styles['colors']['text_secondary'],
            size_hint_y=None,
            height=dp(60),
            text_size=(card.width - dp(20), dp(60)),
            halign='left',
            valign='top'
        )
        card.bind(width=lambda instance, value: setattr(
            desc_label, 'text_size', (value - dp(20), dp(60))
        ))
        card.add_widget(desc_label)
        
        # Location and Department
        loc_dept = Label(
            text=f"Location: {item['location'] or 'N/A'} | Department: {item['department'] or 'N/A'}",
            color=self.styles['colors']['text'],
            size_hint_y=None,
            height=dp(25),
            text_size=(card.width - dp(20), dp(25)),
            halign='left',
            valign='middle'
        )
        card.bind(width=lambda instance, value: setattr(
            loc_dept, 'text_size', (value - dp(20), dp(25))
        ))
        card.add_widget(loc_dept)
        
        # Status and Condition
        status_cond = Label(
            text=f"Status: {item['status'] or 'N/A'} | Condition: {item['condition'] or 'N/A'} | Quantity: {item.get('quantity', 1)}",
            color=self.styles['colors']['text'],
            size_hint_y=None,
            height=dp(25),
            text_size=(card.width - dp(20), dp(25)),
            halign='left',
            valign='middle'
        )

        card.bind(width=lambda instance, value: setattr(
            status_cond, 'text_size', (value - dp(20), dp(25))
        ))
        card.add_widget(status_cond)
        
        # Buttons container
        buttons_box = BoxLayout(
            size_hint_y=None,
            height=dp(30),
            spacing=dp(10)
        )

        # Edit button
        edit_button = Button(
            text='Edit Item',
            size_hint_x=0.33,  # Changed from 0.5 to 0.33
            background_normal='',
            background_color=self.styles['colors']['primary'],
            color=self.styles['colors']['text']
        )
        edit_button.bind(on_press=lambda x: self.show_edit_form(item))
        buttons_box.add_widget(edit_button)

        # Image button
        image_button = Button(
            text='View/Add Image',
            size_hint_x=0.33,  # Changed from 0.5 to 0.33
            background_normal='',
            background_color=self.styles['colors']['primary'],
            color=self.styles['colors']['text']
        )
        image_button.bind(on_press=lambda x: self.show_image_viewer(item))
        buttons_box.add_widget(image_button)

        # Delete button
        delete_button = Button(
            text='Delete Item',
            size_hint_x=0.33,  # Changed from 0.5 to 0.33
            background_normal='',
            background_color=self.styles['colors']['error'],
            color=self.styles['colors']['text']
        )
        delete_button.bind(on_press=lambda x: self.confirm_delete(item))
        buttons_box.add_widget(delete_button)
        
        card.add_widget(buttons_box)
        
        self.results_grid.add_widget(card)
        
        # Add separator
        separator = BoxLayout(
            size_hint_y=None,
            height=dp(2),
            padding=[dp(20), 0]
        )
        with separator.canvas:
            Color(*self.styles['colors']['surface'])
            Rectangle(pos=separator.pos, size=separator.size)
        self.results_grid.add_widget(separator)

    def show_edit_form(self, item):
        from .edit_item import EditItemForm
        edit_popup = EditItemForm(item)
        edit_popup.on_save_callback = self.refresh_search
        edit_popup.open()
    
    def confirm_delete(self, item):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        content.add_widget(Label(
            text=f'Are you sure you want to delete item {item["asset_id"]}?',
            color=self.styles['colors']['text']
        ))
        
        buttons = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        
        # Confirm button
        confirm_btn = Button(
            text='Delete',
            background_normal='',
            background_color=self.styles['colors']['error'],
            color=self.styles['colors']['text']
        )
        
        # Cancel button
        cancel_btn = Button(
            text='Cancel',
            background_normal='',
            background_color=self.styles['colors']['primary'],
            color=self.styles['colors']['text']
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
        self.perform_search(None)
    
    def _update_rect(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*self.styles['colors']['surface'])
            Rectangle(pos=instance.pos, size=instance.size)

    def show_image_viewer(self, item):
        """Show image viewer popup."""
        image_viewer = ImageViewer(item['asset_id'])
        image_viewer.open()