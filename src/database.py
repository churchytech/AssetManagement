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
from pymongo import MongoClient, ASCENDING, TEXT, DESCENDING
from pymongo.errors import PyMongoError, DuplicateKeyError, ConnectionFailure
from datetime import datetime, timezone, timedelta
import logging
from typing import List, Dict, Any, Optional
import csv
import os
from functools import wraps
import time

def retry_operation(max_attempts: int = 3, delay: float = 1.0):
    """Decorator for implementing retry logic on database operations."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except (ConnectionFailure, PyMongoError) as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay * (attempt + 1))
                    continue
            raise last_error
        return wrapper
    return decorator

class InventoryDatabase:
    def __init__(self, connection_string: str):
        """Initialize MongoDB connection with optimized settings."""
        self._setup_logging()

        try:
            # Optimized connection settings
            self.client = MongoClient(
                connection_string,
                maxPoolSize=50,  # Increased connection pool
                retryWrites=True,
                w='majority',  # Ensure write consistency
                connectTimeoutMS=5000,
                serverSelectionTimeoutMS=5000
            )

            self.db = self.client.inventory_db
            self.inventory = self.db.inventory_items

            # Initialize indexes
            self._setup_indexes()

            # Test connection
            self.client.server_info()

            self.logger.info("Successfully connected to database")

        except Exception as e:
            self.logger.error(f"Database initialization error: {e}")
            raise

    def _setup_logging(self):
        """Configure logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _setup_indexes(self):
        """Setup optimized database indexes."""
        try:
            # Unique index for asset_id
            self.inventory.create_index([('asset_id', ASCENDING)], unique=True)

            # Additional indexes for common queries and sorting
            self.inventory.create_index([('last_updated', DESCENDING)])
            self.inventory.create_index([('item_name', ASCENDING)])
            self.inventory.create_index([('department', ASCENDING)])
            self.inventory.create_index([('location', ASCENDING)])
            self.inventory.create_index([('status', ASCENDING)])

            self.logger.info("Database indexes created successfully")

        except Exception as e:
            self.logger.error(f"Failed to create indexes: {e}")
            raise

    def get_formatted_time(self):
        """Get current time in EST format."""
        # Get current UTC time
        utc_time = datetime.now(timezone.utc)

        # Convert to EST (UTC-5)
        est_offset = timedelta(hours=-5)
        est_time = utc_time + est_offset

        # Format time
        return est_time.strftime("%d/%m/%Y %H:%M:%S")

    def validate_asset_id(self, asset_id: str) -> bool:
        """Validate the asset ID."""
        if not asset_id.strip():
            raise ValueError("Asset ID is required")

        # Check if asset ID already exists
        existing = self.inventory.find_one({'asset_id': asset_id})
        if existing:
            raise ValueError(f"Asset ID {asset_id} already exists")

        return True

    @retry_operation()
    def add_item(self, asset_id: str, item_name: str, **kwargs) -> bool:
        """Add a new item with improved validation and error handling."""
        try:
            self.validate_asset_id(asset_id)

            # Prepare item document
            item = {
                'asset_id': asset_id,
                'item_name': item_name,
                'description': kwargs.get('description', ''),
                'location': kwargs.get('location', ''),
                'department': kwargs.get('department', ''),
                'purchase_price': float(kwargs.get('purchase_price', 0.0)),
                'condition': kwargs.get('condition', 'New'),
                'model_number': kwargs.get('model_number', ''),
                'serial_number': kwargs.get('serial_number', ''),
                'status': kwargs.get('status', 'Available'),
                'quantity': int(kwargs.get('quantity', 1)),
                'notes': kwargs.get('notes', ''),
                'last_updated': self.get_formatted_time()
            }

            # Validate required fields
            if not item_name.strip():
                raise ValueError("Item name is required")

            result = self.inventory.insert_one(item)
            self.logger.info(f"Added item with ID: {asset_id}")
            return bool(result.inserted_id)

        except DuplicateKeyError:
            self.logger.error(f"Duplicate asset ID: {asset_id}")
            raise ValueError(f"Asset ID {asset_id} already exists")
        except Exception as e:
            self.logger.error(f"Error adding item: {e}")
            raise

    def update_item(self, asset_id: str, **kwargs) -> bool:
        """Update an existing item's details."""
        try:
            if not self.get_item(asset_id):
                raise ValueError(f"Asset ID {asset_id} not found")

            # Add last_updated timestamp
            kwargs['last_updated'] = self.get_formatted_time()

            result = self.inventory.update_one(
                {'asset_id': asset_id},
                {'$set': kwargs}
            )
            return result.modified_count > 0
        except Exception as e:
            self.logger.error(f"Error updating item: {e}")
            raise

    def get_item(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an item by its asset ID."""
        try:
            item = self.inventory.find_one({'asset_id': asset_id})
            if item:
                item['_id'] = str(item['_id'])
            return item
        except Exception as e:
            self.logger.error(f"Error retrieving item: {e}")
            raise

    def delete_item(self, asset_id: str) -> bool:
        """Delete an item from the inventory."""
        try:
            result = self.inventory.delete_one({'asset_id': asset_id})
            if result.deleted_count == 0:
                raise ValueError(f"Asset ID {asset_id} not found")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting item: {e}")
            raise

    def search_items(self, search_term: str, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Perform paginated search with fragment matching."""
        try:
            # Build query based on search term
            if search_term.strip():
                # Make the search term more strict to avoid partial word matches
                pattern = search_term.strip()
                query = {
                    '$or': [
                        {'asset_id': {'$regex': f".*{pattern}.*", '$options': 'i'}},
                        {'item_name': {'$regex': f".*{pattern}.*", '$options': 'i'}},
                        {'description': {'$regex': f".*{pattern}.*", '$options': 'i'}},
                        {'location': {'$regex': f".*{pattern}.*", '$options': 'i'}},
                        {'department': {'$regex': f".*{pattern}.*", '$options': 'i'}},
                        {'model_number': {'$regex': f".*{pattern}.*", '$options': 'i'}},
                        {'serial_number': {'$regex': f".*{pattern}.*", '$options': 'i'}},
                        {'status': {'$regex': f"^{pattern}.*", '$options': 'i'}},  # Start of word only for status
                        {'condition': {'$regex': f"^{pattern}.*", '$options': 'i'}}  # Start of word only for condition
                    ]
                }
            else:
                # Return all items if no search term
                query = {}

            # Calculate pagination
            skip = (page - 1) * per_page

            # Get total count
            total_items = self.inventory.count_documents(query)

            # Execute search with sorting
            cursor = self.inventory.find(
                query,
                {'_id': 1, 'asset_id': 1, 'item_name': 1, 'description': 1,
                 'location': 1, 'department': 1, 'status': 1, 'condition': 1,
                 'model_number': 1, 'serial_number': 1, 'quantity': 1,
                 'purchase_price': 1, 'last_updated': 1}
            ).sort(
                [('last_updated', DESCENDING)]
            ).skip(skip).limit(per_page)

            # Process results
            items = list(cursor)
            for item in items:
                item['_id'] = str(item['_id'])

            return {
                'items': items,
                'total_items': total_items,
                'page': page,
                'total_pages': (total_items + per_page - 1) // per_page,
                'per_page': per_page
            }

        except Exception as e:
            self.logger.error(f"Search error: {e}")
            raise

            # Calculate pagination
            skip = (page - 1) * per_page

            # Get total count
            total_items = self.inventory.count_documents(query)

            # Execute search with sorting - sort by last_updated by default
            cursor = self.inventory.find(
                query,
                {'image': 0}  # Exclude image data
            ).sort(
                'last_updated', DESCENDING
            ).skip(skip).limit(per_page)

            # Process results
            items = list(cursor)
            for item in items:
                item['_id'] = str(item['_id'])

            return {
                'items': items,
                'total_items': total_items,
                'page': page,
                'total_pages': (total_items + per_page - 1) // per_page,
                'per_page': per_page
            }

        except Exception as e:
            self.logger.error(f"Search error: {e}")
            raise
            skip = (page - 1) * per_page

            # Get total count
            total_items = self.inventory.count_documents(query)

            # Execute search with sorting
            cursor = self.inventory.find(
                query,
                {'score': {'$meta': 'textScore'}, 'image': 0}
            ).sort([
                ('score', {'$meta': 'textScore'}),
                ('last_updated', DESCENDING)
            ]).skip(skip).limit(per_page)

            # Process results
            items = list(cursor)
            for item in items:
                item['_id'] = str(item['_id'])

            return {
                'items': items,
                'total_items': total_items,
                'page': page,
                'total_pages': (total_items + per_page - 1) // per_page,
                'per_page': per_page
            }
        except Exception as e:
            self.logger.error(f"Search error: {e}")
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """Get basic statistics about the inventory."""
        try:
            stats = {
                'total_items': self.inventory.count_documents({}),
                'total_value': sum(item.get('purchase_price', 0)
                                 for item in self.inventory.find({}, {'purchase_price': 1})),
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
        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            raise

    def export_to_csv(self, filename: str = "inventory_export.csv", batch_size: int = 1000) -> str:
        """Export inventory to CSV with batched processing."""
        try:
            # Define consistent field order
            fieldnames = [
                'asset_id',
                'item_name',
                'description',
                'location',
                'department',
                'purchase_price',
                'quantity',
                'condition',
                'model_number',
                'serial_number',
                'status',
                'notes',
                'last_updated'
            ]

            cursor = self.inventory.find(
                {},
                {'_id': 0, 'image': 0}  # Exclude unnecessary fields
            ).batch_size(batch_size)

            if not cursor.alive:
                raise ValueError("No items to export")

            with open(filename, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for item in cursor:
                    # Ensure all fields exist in the item
                    row = {field: item.get(field, '') for field in fieldnames}
                    writer.writerow(row)

            return os.path.abspath(filename)

        except Exception as e:
            self.logger.error(f"Export error: {e}")
            raise

    def add_image(self, asset_id: str, image_path: str) -> bool:
        """Add or update image for an item."""
        try:
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()

            # Update the item with image data
            result = self.inventory.update_one(
                {'asset_id': asset_id},
                {'$set': {'image': image_data}}
            )
            return result.modified_count > 0
        except Exception as e:
            self.logger.error(f"Error adding image: {e}")
            raise

    def get_image(self, asset_id: str) -> Optional[bytes]:
        """Retrieve image data for an item."""
        try:
            item = self.inventory.find_one(
                {'asset_id': asset_id},
                {'image': 1}
            )
            return item.get('image') if item else None
        except Exception as e:
            self.logger.error(f"Error retrieving image: {e}")
            raise

    def remove_image(self, asset_id: str) -> bool:
        """Remove image from an item."""
        try:
            result = self.inventory.update_one(
                {'asset_id': asset_id},
                {'$unset': {'image': ""}}
            )
            return result.modified_count > 0
        except Exception as e:
            self.logger.error(f"Error removing image: {e}")
            raise

    def __del__(self):
        """Cleanup database connections."""
        try:
            if hasattr(self, 'client'):
                self.client.close()
                self.logger.info("Database connection closed")
        except Exception as e:
            self.logger.error(f"Error closing database connection: {e}")