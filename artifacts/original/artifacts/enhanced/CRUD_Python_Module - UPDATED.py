# Enhanced CRUD_Python_Module.py
# Author: Emily Murphy
# Project: CS 340 – Project One (Grazioso Salvare)
#
# Purpose:
#   Improved CRUD class for the AAC MongoDB database.
#   Enhancements include:
#       - Input validation
#       - Structured logging
#       - Exception handling
#       - Clearer delete behavior
#       - More robust CRUD operations

import logging
from typing import Any, Dict, List, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError

# ---------------------------
# LOGGING CONFIGURATION
# ---------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

class AnimalShelter:
    """
    Enhanced AnimalShelter class providing CRUD access to the 'aac.animals' collection.
    """

    def __init__(
        self,
        username: str,
        password: str,
        host: str = "localhost",
        port: int = 27017,
        auth_db: str = "admin",
        db: str = "aac",
        collection: str = "animals",
    ) -> None:
        """
        Initialize the MongoDB client and select the database/collection.
        """
        if not username or not password:
            logging.error("Missing username or password for MongoDB authentication.")
            raise ValueError("Username and password are required for MongoDB authentication.")

        uri = f"mongodb://{username}:{password}@{host}:{port}/?authSource={auth_db}"

        try:
            self.client = MongoClient(uri)
            self.client.admin.command("ping")
            self.database = self.client[db]
            self.collection = self.database[collection]
            logging.info("Successfully connected to MongoDB.")
        except ConnectionFailure as e:
            logging.error(f"Failed to connect to MongoDB: {e}")
            raise ConnectionFailure(f"Failed to connect to MongoDB: {e}") from e

    # ---------------------------
    # VALIDATION HELPER
    # ---------------------------
    def _validate_dict(self, data: Optional[Dict[str, Any]], operation: str) -> bool:
        """Validate that input is a non-empty dictionary."""
        if not isinstance(data, dict) or not data:
            logging.warning(f"{operation} failed: Input must be a non-empty dictionary.")
            return False
        return True

    # ---------------------------
    # CREATE
    # ---------------------------
    def create(self, data: Optional[Dict[str, Any]]) -> bool:
        """Insert a single document into the collection."""
        if not self._validate_dict(data, "Create"):
            return False

        try:
            result = self.collection.insert_one(data)
            logging.info(f"Create successful: Inserted document with _id={result.inserted_id}")
            return bool(result.acknowledged)
        except PyMongoError as e:
            logging.error(f"Create failed: {e}")
            return False

    # ---------------------------
    # READ
    # ---------------------------
    def read(self, query: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Query for documents using find()."""
        mongo_query = query if self._validate_dict(query, "Read") else {}

        try:
            cursor = self.collection.find(mongo_query)
            results = list(cursor)
            logging.info(f"Read successful: Retrieved {len(results)} document(s).")
            return results
        except PyMongoError as e:
            logging.error(f"Read failed: {e}")
            return []

    # ---------------------------
    # UPDATE
    # ---------------------------
    def update(self, query: Dict[str, Any], new_values: Dict[str, Any], many: bool = True) -> int:
        """Update one or many documents."""
        if not self._validate_dict(query, "Update") or not self._validate_dict(new_values, "Update"):
            return 0

        try:
            if many:
                result = self.collection.update_many(query, {"$set": new_values})
            else:
                result = self.collection.update_one(query, {"$set": new_values})

            logging.info(f"Update successful: Modified {result.modified_count} document(s).")
            return int(result.modified_count)
        except PyMongoError as e:
            logging.error(f"Update failed: {e}")
            return 0

    # ---------------------------
    # DELETE
    # ---------------------------
    def delete(self, query: Dict[str, Any], many: bool = True) -> int:
        """Delete one or many documents."""
        if not self._validate_dict(query, "Delete"):
            return 0

        try:
            if many:
                result = self.collection.delete_many(query)
            else:
                result = self.collection.delete_one(query)

            logging.info(f"Delete successful: Removed {result.deleted_count} document(s).")
            return int(result.deleted_count)
        except PyMongoError as e:
            logging.error(f"Delete failed: {e}")
            return 0

    # ---------------------------
    # CLOSE
    # ---------------------------
    def close(self) -> None:
        """Close the MongoDB client."""
        try:
            self.client.close()
            logging.info("MongoDB connection closed.")
        except Exception as e:
            logging.error(f"Error closing MongoDB connection: {e}")
