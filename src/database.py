# database.py
from datetime import datetime
import time
from datetime import timezone
from datetime import timedelta
import csv
import os
from pymongo import MongoClient


class InventoryDatabase:
    def __init__(self, connection_string):
        """Initialize the MongoDB connection."""
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client.inventory_db
            self.inventory = self.db.inventory_items

            # Test connection
            self.client.server_info()

            # Create indexes
            self.inventory.create_index('asset_id', unique=True)

        except Exception as e:
            raise Exception("Failed to connect to database. Please check your credentials.")

    def get_formatted_time(self):
        """Get current time in EST format."""
        # Get current UTC time
        utc_time = datetime.now(timezone.utc)

        # Convert to EST (UTC-5)
        est_offset = timedelta(hours=-5)
        est_time = utc_time + est_offset

        # Format time
        return est_time.strftime("%d/%m/%Y %H:%M:%S")

    def add_item(self, asset_id, item_name, description="", location="", department="",
                 purchase_price=0.0, condition="New", model_number="", serial_number="",
                 status="Available", notes=""):
        """Add a new item to the inventory."""
        try:
            self.validate_asset_id(asset_id)

            item = {
                'asset_id': asset_id,
                'item_name': item_name,
                'description': description,
                'location': location,
                'department': department,
                'purchase_price': float(purchase_price),
                'condition': condition,
                'model_number': model_number,
                'serial_number': serial_number,
                'status': status,
                'quantity': int(quantity),
                'notes': notes,
                'last_updated': self.get_formatted_time()
            }

            self.inventory.insert_one(item)
            return True

        except Exception as e:
            raise ValueError(f"Error adding item: {str(e)}")

    def update_item(self, asset_id, **kwargs):
        """Update an existing item's details."""
        if not self.get_item(asset_id):
            raise ValueError(f"Asset ID {asset_id} not found")

        # Add last_updated timestamp in EST
        kwargs['last_updated'] = self.get_formatted_time()

        try:
            self.inventory.update_one(
                {'asset_id': asset_id},
                {'$set': kwargs}
            )
            return True
        except Exception as e:
            raise ValueError(f"Error updating item: {str(e)}")

    def validate_asset_id(self, asset_id):
        """Validate the asset ID."""
        if not asset_id.strip():
            raise ValueError("Asset ID is required")

        # Check if asset ID already exists
        if self.get_item(asset_id):
            raise ValueError(f"Asset ID {asset_id} already exists")

        return True


    def get_item(self, asset_id):
        """Retrieve an item by its asset ID."""
        item = self.inventory.find_one({'asset_id': asset_id})
        if item:
            item['_id'] = str(item['_id'])  # Convert ObjectId to string
        return item

    def delete_item(self, asset_id):
        """Delete an item from the inventory."""
        result = self.inventory.delete_one({'asset_id': asset_id})
        if result.deleted_count == 0:
            raise ValueError(f"Asset ID {asset_id} not found")
        return True

    def search_items(self, search_term):
        """Search for items by ID, name, or description."""
        query = {
            '$or': [
                {'asset_id': {'$regex': search_term, '$options': 'i'}},
                {'item_name': {'$regex': search_term, '$options': 'i'}},
                {'description': {'$regex': search_term, '$options': 'i'}},
                {'location': {'$regex': search_term, '$options': 'i'}},
                {'department': {'$regex': search_term, '$options': 'i'}}
            ]
        }

        items = list(self.inventory.find(query))
        for item in items:
            item['_id'] = str(item['_id'])
        return items

    def export_to_csv(self, filename="inventory_export.csv"):
        """Export the inventory to CSV, excluding image data."""
        try:
            # Get all items
            items = list(self.inventory.find({}))
            if not items:
                raise ValueError("No items to export")

            # Fields to exclude from export
            exclude_fields = ['_id', 'image']

            # Get field names excluding the ones we don't want
            fieldnames = [k for k in items[0].keys() if k not in exclude_fields]

            with open(filename, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for item in items:
                    # Remove excluded fields from each item
                    for field in exclude_fields:
                        item.pop(field, None)
                    writer.writerow(item)

            return os.path.abspath(filename)

        except Exception as e:
            raise ValueError(f"Error exporting data: {str(e)}")

    def get_statistics(self):
        """Get basic statistics about the inventory."""
        stats = {
            'total_items': self.inventory.count_documents({}),
            'total_value': sum(item.get('purchase_price', 0) for item in self.inventory.find()),
            'items_by_department': {},
            'items_by_condition': {}
        }

        # Get department statistics
        departments = self.inventory.distinct('department')
        for dept in departments:
            if dept:  # Ignore empty departments
                stats['items_by_department'][dept] = self.inventory.count_documents({'department': dept})

        # Get condition statistics
        conditions = self.inventory.distinct('condition')
        for cond in conditions:
            if cond:  # Ignore empty conditions
                stats['items_by_condition'][cond] = self.inventory.count_documents({'condition': cond})

        return stats

    def update_asset_id(self, old_asset_id, new_asset_id):
        """Update an item's asset ID."""
        if old_asset_id == new_asset_id:
            return True

        # Check if new ID exists
        if self.get_item(new_asset_id):
            raise ValueError(f"Asset ID {new_asset_id} already exists")

        # Get the item data
        item = self.get_item(old_asset_id)
        if not item:
            raise ValueError(f"Original Asset ID {old_asset_id} not found")

        # Remove _id field if it exists
        if '_id' in item:
            del item['_id']

        # Update the asset_id
        item['asset_id'] = new_asset_id

        # Insert new document first
        self.inventory.insert_one(item)

        # Then delete the old one
        self.inventory.delete_one({'asset_id': old_asset_id})

        return True

    def add_image(self, asset_id, image_path):
        """Add or update image for an item."""
        try:
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()

            # Update the item with image data
            self.inventory.update_one(
                {'asset_id': asset_id},
                {'$set': {'image': image_data}}
            )
            return True
        except Exception as e:
            raise ValueError(f"Error adding image: {str(e)}")

    def get_image(self, asset_id):
        """Retrieve image data for an item."""
        item = self.inventory.find_one({'asset_id': asset_id})
        if item and 'image' in item:
            return item['image']
        return None

    def remove_image(self, asset_id):
        """Remove image from an item."""
        self.inventory.update_one(
            {'asset_id': asset_id},
            {'$unset': {'image': ""}}
        )
        return True