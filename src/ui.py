from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.app import App

# Import components
from components.add_item import AddItemForm
from components.search import SearchInterface
from components.export import ExportInterface

class InventoryUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(20)
        self.spacing = dp(15)
        
        # Get app instance and styles
        self.app = App.get_running_app()
        self.styles = self.app.get_common_styles()
        
        # Initialize the UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main UI components."""
        # Add title
        self.add_widget(Label(
            text='Inventory Management System',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(24),
            color=self.styles['colors']['text']
        ))
        
        # Create menu bar
        self.create_menu()
        
        # Create content area
        self.content_area = BoxLayout(orientation='vertical', spacing=dp(10))
        self.add_widget(self.content_area)
        
        # Show add item form by default
        self.show_add_item()
    
    def create_menu(self):
        """Create the main menu buttons."""
        menu = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )
        
        # Create menu buttons with common style
        button_style = self.styles['button_style']
        
        buttons = [
            ('Add Item', self.show_add_item),
            ('Search', self.show_search),
            ('Export', self.show_export)
        ]
        
        for text, callback in buttons:
            btn = Button(
                text=text,
                on_press=callback,
                **button_style
            )
            menu.add_widget(btn)
        
        self.add_widget(menu)
    
    def clear_content(self):
        """Clear the content area."""
        self.content_area.clear_widgets()
    
    def show_message(self, message, message_type='info'):
        """Show a message to the user."""
        color = {
            'success': self.styles['colors']['success'],
            'error': self.styles['colors']['error'],
            'info': self.styles['colors']['text']
        }.get(message_type, self.styles['colors']['text'])
        
        self.content_area.add_widget(Label(
            text=message,
            color=color,
            font_size=dp(16),
            size_hint_y=None,
            height=dp(40)
        ))
    
    def show_add_item(self, *args):
        """Display the add item form."""
        self.clear_content()
        add_item_form = AddItemForm()
        self.content_area.add_widget(add_item_form)
    
    def show_search(self, *args):
        """Display the search interface."""
        self.clear_content()
        search_interface = SearchInterface()
        self.content_area.add_widget(search_interface)
    
    def show_export(self, *args):
        """Display the export interface."""
        self.clear_content()
        export_interface = ExportInterface()
        self.content_area.add_widget(export_interface)
    
    def handle_error(self, error_message):
        """Handle and display errors."""
        self.show_message(f"Error: {error_message}", 'error')
    
    def handle_success(self, success_message):
        """Handle and display success messages."""
        self.show_message(success_message, 'success') 
