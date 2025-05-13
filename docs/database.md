
# 🗃️ Database & ETL Design

Our platform uses a PostgreSQL database to store structured data relevant to real estate transactions.

## 🏗️ Database Tables

- `users`: Information about the property owners or agents
- `locations`: Location metadata (e.g., neighborhood, zone)
- `property_types`: Categories such as "Apartment", "House", etc.
- `properties`: Each listed property with foreign keys to the above
- `images`: URLs tied to property IDs

## 🧬 Schema Diagram

![ERD](./ERD_House_Price_Final.png)

## 🛠️ ETL Pipeline

Located in `etl/etl_process.py`, the ETL performs:

- Extraction from cleaned CSV files
- Transformation: handling nulls, standardizing fields
- Loading into PostgreSQL using SQLAlchemy

The ETL supports modular growth and can easily scale to new data sources in future iterations.
