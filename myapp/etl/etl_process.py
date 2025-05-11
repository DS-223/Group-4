"""
ETL Script for Generating and Loading Real Estate Data into a database.

This script generates data for users, property types, locations, properties, and images,
saves the data to CSV files, and loads the CSV data into a database. It also creates a
machine-learning-ready CSV file with selected and joined fields.

Modules:
    - database.models: database models for the project.
    - database.database: database engine and base class.
    - database.data_generate: Functions to generate data for various entities.
    - pandas: For data manipulation and storage in CSV.
    - loguru: For logging.
    - random: For random number generation.
    - glob, os: For file path and system operations.
"""

import pandas as pd
from loguru import logger
import random
from database.database import engine, Base
from database.data_generate import generate_user, generate_location, generate_property, generate_image, generate_property_type
import glob
from os import path

# Create all tables from the models
Base.metadata.create_all(bind=engine)

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
users = pd.DataFrame([generate_user(user_id, USER_TYPES) for user_id in range(NUMBER_OF_USERS)])
logger.info("User Data Sample:")
logger.info(users.head(1))
users.to_csv("data/users.csv", index=False)
logger.info(f"User data saved to CSV: {users.shape}")

# Generate Property Types Data
types = pd.DataFrame([generate_property_type(type_id, PROPERTY_TYPES) for type_id in range(len(PROPERTY_TYPES))])
logger.info("Property Type Data Sample:")
logger.info(types.head(1))
types.to_csv("data/property_types.csv", index=False)
logger.info(f"Property type data saved to CSV: {types.shape}")

# Generate Locations Data
locations = pd.DataFrame([generate_location(location_id, DISTRICTS_YEREVAN) for location_id in range(NUMBER_OF_LOCATIONS)])
logger.info("Location Data Sample:")
logger.info(locations.head(1))
locations.to_csv("data/locations.csv", index=False)
logger.info(f"Location data saved to CSV: {locations.shape}")

# Generate Properties Data
properties = []

for property_id in range(1, NUMBER_OF_PROPERTIES + 1):
    user_id = random.randint(1, NUMBER_OF_USERS)
    location_id = random.randint(1, NUMBER_OF_LOCATIONS)
    post_date = pd.Timestamp.today() - pd.to_timedelta(random.randint(0, 180), unit='d')

    prop = generate_property(
        property_id=property_id,
        user_id=user_id,
        location_id=location_id,
        property_types=PROPERTY_TYPES,
        deal_types=DEAL_TYPES,
        renovation_statuses=RENOVATION_STATUSES,
        districts=DISTRICTS_YEREVAN,
        post_date=post_date.strftime('%Y-%m-%d')
    )

    # 65% chance to assign a sell_date
    if random.random() < 0.65:
        sell_date = post_date + pd.to_timedelta(random.randint(1, 180), unit='d')
        if sell_date > pd.Timestamp.today():
            sell_date = pd.Timestamp.today()
        sell_date = sell_date.strftime('%Y-%m-%d')
    else:
        sell_date = None

    prop["sell_date"] = sell_date
    properties.append(prop)

properties = pd.DataFrame(properties)
logger.info("Property Data Sample:")
logger.info(properties.head(1))
properties.to_csv("data/properties.csv", index=False)
logger.info(f"Property data saved to CSV: {properties.shape}")

# Generate Images Data
images = []
image_id = 1

for property_record in properties.to_dict(orient="records"):
    property_id = property_record["property_id"]
    img = generate_image(image_id, property_id)
    images.append(img)
    image_id += 1

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
    Load data from a CSV file into a specified database table.

    Args:
        table_name (str): The name of the table to load data into.
        csv_path (str): The file path of the CSV to load.

    Returns:
        None
    """
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, con=engine, if_exists="append", index=False)
    logger.info(f"Loading data into table: {table_name}")

# -----------------------------------------------------
# Load CSV Data into Database Tables
# -----------------------------------------------------

folder_path = "data/*.csv"
files = glob.glob(folder_path)
base_names = [path.splitext(path.basename(file))[0] for file in files]

for table in base_names:
    try:
        logger.info(f"Loading data into table: {table}")
        load_csv_to_table(table, path.join("data/", f"{table}.csv"))
    except Exception as e:
        logger.error(f"Failed to ingest table {table}. Error: {e}")
        print(f"Failed to ingest table {table}. Moving to the next!")

print("Tables are populated.")

# -----------------------------------------------------
# Create ML-Ready CSV
# -----------------------------------------------------

def create_ml_ready_property_csv():
    """
    Merge various CSVs to prepare a machine-learning-ready dataset.

    Merges properties with user, location, and property type information,
    selects relevant columns, and saves the dataset to a new CSV file:
    `data/property_ml_ready.csv`.

    Returns:
        None
    """
    users_df = pd.read_csv("data/users.csv")
    locations_df = pd.read_csv("data/locations.csv")
    types_df = pd.read_csv("data/property_types.csv")
    properties_df = pd.read_csv("data/properties.csv")

    merged = properties_df.merge(users_df[['user_id', 'user_type']], on='user_id', how='inner')
    merged = merged.merge(locations_df[['location_id', 'district']], on='location_id', how='inner')
    merged = merged.merge(types_df[['type_id', 'type_name']], on='type_id', how='inner')

    merged.drop(columns=['user_id', 'location_id', 'type_id'], inplace=True)

    cols = ['property_id', 'deal_type', 'user_type', 'district', 'type_name',
            'size_sqm', 'rooms', 'floor', 'year_built', 'post_date',
            'sell_date', 'renovation_status', 'estimated_saleprice', 'estimated_rentprice']
    merged = merged[cols]

    merged.to_csv("data/property_ml_ready.csv", index=False)
    logger.info(f"ML-ready property data saved to data/property_ml_ready.csv with shape {merged.shape}")

# Generate ML-ready CSV
create_ml_ready_property_csv()


print("Tables are populated and ML-ready CSV is created.")
