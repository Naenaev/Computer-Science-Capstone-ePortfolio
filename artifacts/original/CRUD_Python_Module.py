# CRUD_Python_Module.py
# Author: Emily Murphy
# Project: CS 340 – Project One (Grazioso Salvare)
#
# Purpose:
#   Reusable CRUD class for the AAC MongoDB database.
#   - Authenticates with Mongo using provided username/password
#   - Exposes Create, Read, Update, Delete methods with simple return values
#

from typing import Any, Dict, List, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError


class AnimalShelter:
    """
    AnimalShelter provides CRUD access to the 'aac.animals' collection.

    Constructor:
        AnimalShelter(username, password, host='localhost', port=27017,
                      auth_db='admin', db='aac', collection='animals')

    Methods:
        create(data: dict) -> bool
        read(query: dict) -> List[dict]
        update(query: dict, new_values: dict, many: bool = True) -> int
        delete(query: dict, many: bool = True) -> int
        close() -> None
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
        Raises ConnectionFailure if the connection/auth fails.
        """
        if not username or not password:
            raise ValueError("Username and password are required for MongoDB authentication.")

        # Build MongoDB URI with authSource=admin (per course setup instructions)
        uri = f"mongodb://{username}:{password}@{host}:{port}/?authSource={auth_db}"

        try:
            self.client = MongoClient(uri)
            # Quick ping to verify connectivity and credentials
            self.client.admin.command("ping")

            self.database = self.client[db]
            self.collection = self.database[collection]
        except ConnectionFailure as e:
            # Bubble up a clear error so calling code (Dash/notebooks) can display it
            raise ConnectionFailure(f"Failed to connect to MongoDB: {e}") from e

    # ---------------------------
    # CREATE
    # ---------------------------
    def create(self, data: Optional[Dict[str, Any]]) -> bool:
        """
        Insert a single document.
        Input:  data -> dictionary representing the document to insert
        Return: True if insert acknowledged, else False
        """
        if not isinstance(data, dict) or not data:
            # Per rubric, return False instead of raising for bad input
            return False

        try:
            result = self.collection.insert_one(data)
            return bool(result.acknowledged)
        except PyMongoError as e:
            # Log-friendly print; return False per rubric
            print(f"Create failed: {e}")
            return False

    # ---------------------------
    # READ
    # ---------------------------
    def read(self, query: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Query for document(s) using find() (not find_one()).
        Input:  query -> dictionary used with MongoDB find()
        Return: list of matching documents (possibly empty)
        """
        # Allow None/empty query to mean "match all"
        mongo_query = query if isinstance(query, dict) else {}

        try:
            cursor = self.collection.find(mongo_query)
            return list(cursor)
        except PyMongoError as e:
            print(f"Read failed: {e}")
            return []

    # ---------------------------
    # UPDATE
    # ---------------------------
    def update(self, query: Dict[str, Any], new_values: Dict[str, Any], many: bool = True) -> int:
        """
        Update one or many documents by setting provided fields.
        Inputs:
            query       -> dict filter for documents to update
            new_values  -> dict of fields to set (e.g., {'age_upon_outcome': '3 years'})
            many        -> True to update_many, False to update_one
        Return:
            Number of modified documents (int)
        """
        if not isinstance(query, dict) or not query:
            print("Update failed: query must be a non-empty dict.")
            return 0
        if not isinstance(new_values, dict) or not new_values:
            print("Update failed: new_values must be a non-empty dict.")
            return 0

        try:
            if many:
                result = self.collection.update_many(query, {"$set": new_values})
            else:
                result = self.collection.update_one(query, {"$set": new_values})
            return int(result.modified_count)
        except PyMongoError as e:
            print(f"Update failed: {e}")
            return 0

    # ---------------------------
    # DELETE
    # ---------------------------
    def delete(self, query: Dict[str, Any], many: bool = True) -> int:
        """
        Delete one or many documents matching the query.
        Inputs:
            query  -> dict filter for documents to delete
            many   -> True to delete_many, False to delete_one
        Return:
            Number of deleted documents (int)
        """
        if not isinstance(query, dict) or not query:
            print("Delete failed: query must be a non-empty dict.")
            return 0

        try:
            if many:
                result = self.collection.delete_many(query)
            else:
                result = self.collection.delete_one(query)
            return int(result.deleted_count)
        except PyMongoError as e:
            print(f"Delete failed: {e}")
            return 0

    # ---------------------------
    # OPTIONAL: explicit close
    # ---------------------------
    def close(self) -> None:
        """Close the underlying MongoDB client."""
        try:
            self.client.close()
        except Exception:
            pass
