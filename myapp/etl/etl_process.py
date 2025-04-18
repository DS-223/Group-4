"""
ETL Script for Generating and Loading Real Estate Data into a Database.

This script generates data for users, property types, locations, properties, and images,
saves the data to CSV files, and loads the CSV data into a database.

Modules:
    - Database.models: Database models for the project.
    - Database.database: Database engine and base class.
    - Database.data_generate: Functions to generate data for various entities.
    - pandas: For data manipulation and storage in CSV.
    - loguru: For logging.
    - random: For random number generation.
    - glob, os: For file path and system operations.
"""

import pandas as pd
from loguru import logger
import random
from Database.models import *
from Database.database import engine, Base
from Database.data_generate import (
    generate_users,
    generate_property_types,
    generate_locations,
    generate_properties,
    generate_images
)
import glob
from os import path

# -----------------------------------------------------
# Constants
# -----------------------------------------------------
NUMBER_OF_USERS = 50
NUMBER_OF_LOCATIONS = 50
NUMBER_OF_PROPERTIES = 3000
PROPERTY_TYPES = ["Apartment", "House"]
DEAL_TYPES = ["Rent", "Sale"]
USER_TYPES = ["Agent", "Owner", "Buyer"]
DISTRICTS_YEREVAN = [
    "Kentron", "Arabkir", "Avan", "Davtashen", "Erebuni", "Malatia-Sebastia",
    "Nor Nork", "Nork-Marash", "Shengavit", "Kanaker-Zeytun", "Ajapnyak", "Nubarashen"
]
RENOVATION_STATUSES = ["Newly Renovated", "Partially Renovated", "Not Renovated"]

# -----------------------------------------------------
# Generate and Save Data to CSV
# -----------------------------------------------------

# Generate Users Data
users = pd.DataFrame([generate_users(1, USER_TYPES)[0] for user_id in range(NUMBER_OF_USERS)])
logger.info("User Data Sample:")
logger.info(users.head(1))
users.to_csv("data/users.csv", index=False)
logger.info(f"User data saved to CSV: {users.shape}")

# Generate Property Types Data
types = pd.DataFrame([generate_property_types(PROPERTY_TYPES)[0] for _ in range(len(PROPERTY_TYPES))])
logger.info("Property Type Data Sample:")
logger.info(types.head(1))
types.to_csv("data/property_types.csv", index=False)
logger.info(f"Property type data saved to CSV: {types.shape}")

# Generate Locations Data
locations = pd.DataFrame([generate_locations(1, DISTRICTS_YEREVAN)[0] for location_id in range(NUMBER_OF_LOCATIONS)])
logger.info("Location Data Sample:")
logger.info(locations.head(1))
locations.to_csv("data/locations.csv", index=False)
logger.info(f"Location data saved to CSV: {locations.shape}")

# Generate Properties Data
properties = []
for property_id in range(1, NUMBER_OF_PROPERTIES + 1):
    user_id = random.randint(1, NUMBER_OF_USERS)
    location_id = random.randint(1, NUMBER_OF_LOCATIONS)
    property_type = random.choice(PROPERTY_TYPES)
    deal_type = random.choice(DEAL_TYPES)
    renovation_status = random.choice(RENOVATION_STATUSES)
    district = random.choice(DISTRICTS_YEREVAN)
    
    prop = generate_properties(
        n=1,
        user_count=1,
        location_count=1,
        property_types=[property_type],
        deal_types=[deal_type],
        renovation_statuses=[renovation_status],
        districts=[district]
    )[0]
    properties.append(prop)

properties = pd.DataFrame(properties)
logger.info("Property Data Sample:")
logger.info(properties.head(1))
properties.to_csv("data/properties.csv", index=False)
logger.info(f"Property data saved to CSV: {properties.shape}")

# Generate Images Data
images = []
for property_record in properties.to_dict(orient="records"):
    img = generate_images([property_record])[0]
    images.append(img)

images = pd.DataFrame(images)
logger.info("Image Data Sample:")
logger.info(images.head(1))
images.to_csv("data/images.csv", index=False)
logger.info(f"Image data saved to CSV: {images.shape}")

# -----------------------------------------------------
# Utility Function to Load Data into Database
# -----------------------------------------------------

def load_csv_to_table(table_name: str, csv_path: str) -> None:
    """
    Load data from a CSV file into a database table.

    **Parameters:**
    
    - `table_name (str):` The name of the database table.
    - `csv_path (str):` The path to the CSV file containing data.

    **Returns:**
        - `None`
    """
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, con=engine, if_exists="append", index=False)
    logger.info(f"Loading data into table: {table_name}")

# -----------------------------------------------------
# Load CSV Data into Database Tables
# -----------------------------------------------------

# Get all CSV file paths
folder_path = "data/*.csv"
files = glob.glob(folder_path)
base_names = [path.splitext(path.basename(file))[0] for file in files]

# Load data from CSV files into respective tables
for table in base_names:
    try:
        logger.info(f"Loading data into table: {table}")
        load_csv_to_table(table, path.join("data/", f"{table}.csv"))
    except Exception as e:
        logger.error(f"Failed to ingest table {table}. Error: {e}")
        print(f"Failed to ingest table {table}. Moving to the next!")

print("Tables are populated.")