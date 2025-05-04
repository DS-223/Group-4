"""
Data Generation Utilities for Real Estate ETL.

This script uses Faker and random logic to generate realistic fake data for users,
property types, locations, properties, and images for use in seeding or testing
a real estate platform's database.

Functions:
    - generate_user
    - generate_property_type
    - generate_location
    - estimate_prices
    - generate_random_date
    - generate_property
    - generate_image
"""

from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

# Data Models

def generate_user(user_id, user_types):
    """
        Generate a dictionary representing a user.

        Args:
            user_id (int): Unique identifier for the user.
            user_types (list): List of user type strings (e.g., ["Agent", "Owner"]).

        Returns:
            dict: A dictionary representing the user record.
    """
    return {
        "user_id": user_id,
        "username": fake.user_name(),
        "email": fake.email(),
        "phone_number": fake.phone_number(),
        "user_type": random.choice(user_types)
    }

def generate_property_type(type_id, property_types):
    """
        Generate a dictionary representing a property type.

        Args:
            type_id (int): Unique identifier for the property type.
            property_types (list): List of property type strings (e.g., ["Apartment", "House"]).

        Returns:
            dict: A dictionary representing the property type record.
    """
    return {
        "type_id": type_id,
        "type_name": random.choice(property_types)
    }

def generate_location(location_id, districts):
    """
        Generate a dictionary representing a location in Yerevan.

        Args:
            location_id (int): Unique identifier for the location.
            districts (list): List of districts within Yerevan.

        Returns:
            dict: A dictionary representing the location record.
    """
    return {
        "location_id": location_id,
        "region": "Yerevan",
        "city": "Yerevan",
        "district": random.choice(districts)
    }

def estimate_prices(size, rooms, year, renovation, district, deal_type):
    """
        Estimate sale and rent prices based on property characteristics.

        Args:
            size (float): Size of the property in square meters.
            rooms (int): Number of rooms.
            year (int): Year the property was built.
            renovation (str): Renovation status.
            district (str): District of the property.
            deal_type (str): Type of deal ("Sale" or "Rent").

        Returns:
            tuple: Estimated sale price and rent price.
        """
    base_price = size * random.uniform(1200, 2500)
    multiplier = 1.0

    if renovation == "Newly Renovated":
        multiplier += 0.15
    elif renovation == "Not Renovated":
        multiplier -= 0.1

    if district == "Kentron":
        multiplier += 0.25
    elif district in ["Ajapnyak", "Nubarashen"]:
        multiplier -= 0.15

    if rooms >= 4:
        multiplier += 0.10
    elif rooms == 1:
        multiplier -= 0.05

    current_year = datetime.now().year
    age = current_year - year
    if age < 10:
        multiplier += 0.05
    elif age > 40:
        multiplier -= 0.05

    sale_price = round(base_price * multiplier, 2)
    rent_price = round((sale_price * 0.004), 2)

    return sale_price, rent_price

def generate_random_date(start_year=2021, end_year=2025):
    """
        Generate a random date between the given years years.

        Args:
            start_year (int): Start year for the range.
            end_year (int): End year for the range.

        Returns:
            date: A randomly generated date.
    """
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return (start_date + timedelta(days=random_days)).date()


def generate_property(property_id, user_id, location_id, property_types, post_date, deal_types, renovation_statuses, districts):
    """
        Generate a synthetic property record with price estimation and optional sell_date.

        Args:
            property_id (int): Unique identifier for the property.
            user_id (int): ID of the user posting the property.
            location_id (int): ID of the property's location.
            property_types (List[str]): Available property types.
            post_date (str): Date the property is posted.
            deal_types (List[str]): List of deal types.
            renovation_statuses (List[str]): Renovation options.
            districts (List[str]): List of available districts.

        Returns:
            dict: A dictionary representing a property listing.
    """
    size = round(random.uniform(25, 200), 1)
    deal_type = random.choice(deal_types)
    renovation = random.choice(renovation_statuses)
    rooms = random.randint(1, 6)
    post_date = generate_random_date()
    year = random.randint(1965, 2024)
    district = random.choice(districts)
    sale_price, rent_price = estimate_prices(size, rooms, year, renovation, district, deal_type)

    sell_date = None
    if deal_type == "Sale" and random.random() < 0.7:  # 70% chance it was sold
        sell_date = post_date + timedelta(days=random.randint(15, 400))
        if sell_date > datetime.now().date():
            sell_date = None

    return {
        "property_id": property_id,
        "title": fake.sentence(nb_words=4),
        "type_id": random.randint(1, len(property_types)),
        "deal_type": deal_type,
        "user_id": user_id,
        "post_date": post_date,
        "sell_date": sell_date,
        "location_id": location_id,
        "size_sqm": size,
        "floor": random.randint(1, 12),
        "rooms": rooms,
        "year_built": year,
        "renovation_status": renovation,
        "estimated_saleprice": sale_price,
        "estimated_rentprice": rent_price
    }


def generate_image(image_id, property_id):
    """
        Generate a synthetic image record for a property.

        Args:
            image_id (int): Unique identifier for the image.
            property_id (int): ID of the property the image belongs to.

        Returns:
            dict: A dictionary representing an image.
    """
    return {
        "image_id": image_id,
        "property_id": property_id,
        "image_url": f"https://picsum.photos/seed/{fake.uuid4()}/400/300"
    }
