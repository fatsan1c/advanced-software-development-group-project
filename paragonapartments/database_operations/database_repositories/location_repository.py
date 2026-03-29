"""
Location Repository - All location-related database operations.
Handles location CRUD operations and location information retrieval.
"""
from __future__ import annotations

from database_operations.database_repositories.base_repository import BaseRepository


class LocationsRepository(BaseRepository):
    """Object-oriented data access for the locations table."""

    TABLE = "locations"
    ID_FIELD = "location_ID"
    ALLOWED_UPDATE_FIELDS = {"city", "address"}

    def get_location_by_id(self, location_id):
        """
        Get location details by location ID.

        Args:
            location_id (int): The location ID to look up

        Returns:
            dict: Location data if found, None otherwise
                  Example: {'location_ID': 1, 'city': 'Bristol', 'address': '...'}
        """
        return self._get_by_id(
            location_id,
            columns=["location_ID", "city", "address"],
        )

    def get_location_by_city(self, city):
        """
        Get location details by city name.

        Args:
            city (str): The city name to look up

        Returns:
            dict: Location data if found, None otherwise
        """
        rows = self._get_all_by_field(
            "city",
            city,
            columns=["location_ID", "city", "address"],
        )
        return rows[0] if rows else None

    def get_all_locations(self):
        """
        Get all locations from the database.

        Returns:
            list: List of location dictionaries, empty list if error
        """
        return self._get_all(
            columns=["location_ID", "city", "address"],
            order_by="city",
        )

    def get_all_cities(self):
        """
        Get all city names from the database.

        Returns:
            list: List of city name strings (e.g., ['Bristol', 'Cardiff', 'London'])
        """
        result = self._get_all(columns=["city"], order_by="city")
        return [row["city"] for row in result] if result else []

    def get_location_id_by_city(self, city):
        """
        Get location ID by city name.

        Args:
            city (str): The city name to look up

        Returns:
            int: Location ID if found, None otherwise
        """
        location = self.get_location_by_city(city)
        return location["location_ID"] if location else None

    def create_location(self, city, address=None):
        """
        Create a new location in the database.

        Args:
            city (str): City name for the new location
            address (str, optional): Physical address

        Returns:
            int: ID of newly created location, None if failed
        """
        return self._insert({"city": city, "address": address})

    def update_location(self, location_id, **kwargs):
        """
        Update location information.

        Args:
            location_id (int): ID of location to update
            **kwargs: Fields to update (city, address)

        Returns:
            bool: True if successful, False otherwise
        """
        return self._update_by_id(
            location_id,
            kwargs,
            allowed_fields=self.ALLOWED_UPDATE_FIELDS,
        )

    def delete_location(self, location_id):
        """
        Delete a location from the database.

        Args:
            location_id (int): ID of location to delete

        Returns:
            bool: True if successful, False otherwise
        """
        return self._delete_by_id(location_id)

    def get_location_stats(self, location_id):
        """
        Get statistics for a specific location.

        Args:
            location_id (int): The location ID

        Returns:
            dict: Statistics including user count, apartment count, etc.
        """
        query = """
            SELECT
                l.location_ID,
                l.city,
                COUNT(DISTINCT u.user_ID) as user_count,
                COUNT(DISTINCT a.apartment_ID) as apartment_count
            FROM locations l
            LEFT JOIN users u ON l.location_ID = u.location_ID
            LEFT JOIN apartments a ON l.location_ID = a.location_ID
            WHERE l.location_ID = ?
            GROUP BY l.location_ID, l.city
        """
        return self._execute(query, (location_id,), fetch_one=True)


def get_location_id_by_city(city):
    """
    Helper function to get location ID by city name.

    Args:
        city (str): The city name to look up

    Returns:
        int: Location ID if found, None otherwise
    """
    return LocationsRepository().get_location_id_by_city(city)

def get_all_cities():
    """
    Helper function to get all city names.

    Returns:
        list: List of city name strings (e.g., ['Bristol', 'Cardiff', 'London'])
    """
    return LocationsRepository().get_all_cities()
