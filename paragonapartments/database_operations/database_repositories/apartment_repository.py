"""
Apartment Repository - All apartment-related database operations.
Handles apartment queries, occupancy tracking, and apartment management.
"""
from __future__ import annotations

from database_operations.database_repositories.base_repository import BaseRepository
from database_operations.database_repositories.location_repository import get_location_id_by_city
from database_operations.db_utils import normalize_location


class ApartmentsRepository(BaseRepository):
    """Object-oriented API for apartments table and apartment-centric analytics."""

    TABLE = "apartments"
    ID_FIELD = "apartment_ID"
    ALLOWED_UPDATE_FIELDS = {
        "apartment_address",
        "number_of_beds",
        "monthly_rent",
        "occupied",
        "location_ID",
    }

    def get_all_occupancy(self, location=None):
        """
        Retrieve count of occupied apartments from the database.

        Args:
            location (str, optional): City name to filter by. If None, returns all occupied apartments.

        Returns:
            int: Number of occupied apartments (where occupied = 1)
        """
        if location and location.lower() != "all":
            query = """
                SELECT a.apartment_ID
                FROM apartments a
                JOIN locations l ON a.location_ID = l.location_ID
                WHERE a.occupied = 1 AND l.city = ?
            """
            results = self._execute(query, (location,), fetch_all=True)
        else:
            query = """
                SELECT apartment_ID FROM apartments WHERE occupied = 1
            """
            results = self._execute(query, fetch_all=True)

        return len(results) if results else 0

    def get_total_apartments(self, location=None):
        """
        Retrieve total count of all apartments from the database.

        Args:
            location (str, optional): City name to filter by. If None, returns all apartments.

        Returns:
            int: Total number of apartments
        """
        city = normalize_location(location)

        if city:
            location_id = get_location_id_by_city(city)
            if location_id is None:
                return 0

            results = self._get_all_by_field(
                "location_ID",
                location_id,
                columns=["apartment_ID"],
            )
        else:
            results = self._get_all(columns=["apartment_ID"])

        return len(results) if results else 0

    def get_monthly_revenue(self, location=None):
        """
        Calculate total monthly revenue from active leases (actual rent collected).
        Uses lease_agreements for consistency with revenue trend graph.

        Args:
            location (str, optional): City name to filter by. None/'all'/'All Locations' = all.

        Returns:
            float: Total monthly revenue from active leases
        """
        city = normalize_location(location)
        loc_filter = " AND l.city = ?" if city else ""
        query = f"""
            SELECT COALESCE(SUM(la.monthly_rent), 0) AS total_revenue
            FROM lease_agreements la
            JOIN apartments a ON la.apartment_ID = a.apartment_ID
            JOIN locations l ON a.location_ID = l.location_ID
            WHERE la.active = 1
            {loc_filter}
        """
        params = (city,) if city else None
        result = self._execute(query, params, fetch_one=True)
        return float(result.get("total_revenue") or 0)

    def get_potential_revenue(self, location=None):
        """
        Calculate potential monthly revenue if all apartments were occupied.

        Args:
            location (str, optional): City name to filter by. None/'all'/'All Locations' = all.

        Returns:
            float: Potential monthly revenue from all apartments
        """
        city = normalize_location(location)
        loc_filter = " AND l.city = ?" if city else ""
        query = f"""
            SELECT COALESCE(SUM(a.monthly_rent), 0) AS potential_revenue
            FROM apartments a
            JOIN locations l ON a.location_ID = l.location_ID
            WHERE 1=1
            {loc_filter}
        """
        params = (city,) if city else None
        result = self._execute(query, params, fetch_one=True)
        return float(result.get("potential_revenue") or 0)

    def get_all_apartments(self, location="all"):
        """
        Get all apartments from the database.

        Args:
            location (str, optional): City name to filter by. If "All Locations" or None, returns all apartments.

        Returns:
            list: List of apartment dictionaries, empty list if error
        """
        if location and location.lower() not in ["all locations", "all"]:
            query = """
                SELECT a.apartment_ID, l.city, a.apartment_address, a.number_of_beds, a.monthly_rent, a.occupied
                FROM apartments a
                JOIN locations l ON a.location_ID = l.location_ID
                WHERE l.city = ?
                ORDER BY l.city, a.apartment_address
            """
            return self._execute(query, (location,), fetch_all=True)

        query = """
            SELECT a.apartment_ID, l.city, a.apartment_address, a.number_of_beds, a.monthly_rent, a.occupied
            FROM apartments a
            JOIN locations l ON a.location_ID = l.location_ID
            ORDER BY l.city, a.apartment_address
        """
        return self._execute(query, fetch_all=True)

    def create_apartment(self, location_ID, apartment_address, number_of_beds, monthly_rent, occupied):
        """
        Create a new apartment in the database.

        Args:
            apartment_address (str): Address of the apartment
            number_of_beds (int): Number of beds in the apartment
            monthly_rent (float): Monthly rent amount
            occupied (int): 1 if occupied, 0 if vacant
            location_ID (int): Location ID for the apartment

        Returns:
            bool: True if creation was successful, False otherwise
        """
        result = self._insert(
            {
                "apartment_address": apartment_address,
                "number_of_beds": number_of_beds,
                "monthly_rent": monthly_rent,
                "occupied": occupied,
                "location_ID": location_ID,
            },
        )
        return result is not None

    def update_apartment(self, apartment_id, **kwargs):
        """
        Update apartment information.

        Args:
            apartment_id (int): ID of apartment to update
            **kwargs: Fields to update (apartment_address, number_of_beds, monthly_rent, occupied, location_ID)

        Returns:
            bool: True if successful, False otherwise
        """
        return self._update_by_id(
            apartment_id,
            kwargs,
            allowed_fields=self.ALLOWED_UPDATE_FIELDS,
        )

    def delete_apartment(self, apartment_id):
        """
        Delete an apartment from the database.

        Args:
            apartment_id (int): ID of apartment to delete
        """
        return self._delete_by_id(apartment_id)

def get_all_apartments(location="all"):
    """
    Get all apartments from the database.

    Args:
        location (str, optional): City name to filter by. If "All Locations" or None, returns all apartments.

    Returns:
        list: List of apartment dictionaries, empty list if error
    """
    return ApartmentsRepository().get_all_apartments(location)

def set_apartment_as_occupied(apartment_id):
    """
    Update the occupied status of an apartment.

    Args:
        apartment_id (int): ID of the apartment to update
        occupied (bool): True to set as occupied, False for vacant

    Returns:
        bool: True if update was successful, False otherwise
    """
    return ApartmentsRepository().update_apartment(apartment_id, occupied=1)