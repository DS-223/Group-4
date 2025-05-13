from sqlalchemy import Column, Integer, String, Float, ForeignKey, Numeric, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from database import engine

Base = declarative_base()


class User(Base):
    """
        Represents a user in the real estate platform.

        Attributes:
            user_id (int): Primary key identifying the user.
            username (str): Name or alias of the user.
            email (str): Email address of the user (required).
            phone_number (str): Contact phone number of the user.
            user_type (float): Type of user (Agent, Owner, Buyer).
    """
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String, nullable=False)
    phone_number = Column(String)
    user_type = Column(String)


class Location(Base):
    """
        Represents a physical location relevant to property listings.

        Attributes:
            location_id (int): Primary key identifying the location.
            region (str): Name of the region.
            city (str): Name of the city (required).
            district (str): District within the city.
    """
    __tablename__ = "locations"

    location_id = Column(Integer, primary_key=True)
    region = Column(String)
    city = Column(String, nullable=False)
    district = Column(String)


class PropertyType(Base):
    """
        Represents the type or category of a property.

        Attributes:
            type_id (int): Primary key identifying the property type.
            type_name (str): Descriptive name of the property type (Apartment, House).
    """
    __tablename__ = "property_types"

    type_id = Column(Integer, primary_key=True)
    type_name = Column(String)


class Property(Base):
    """
        Represents a real estate property listing.

        Attributes:
            property_id (int): Primary key for the property.
            title (str): Title of the listing.
            description (str): Description of the property.
            type_id (int): Foreign key referencing the property type.
            deal_type (str): Type of deal (Sale, Rent).
            status (str): Current status of the listing (Available, Sold).
            user_id (int): Foreign key referencing the user who posted the property.
            location_id (int): Foreign key referencing the property's location.
            post_date (date): Date the property was posted (required).
            sell_date (date): Date the property was sold (nullable).
            size_sqm (float): Size of the property in square meters.
            floor (int): Floor number (if applicable).
            rooms (int): Number of rooms in the property.
            year_built (int): Year the property was constructed.
            renovation_status (str): Current renovation status (Newly Renovated, Partially Renovated, Not Renovated).
            estimated_saleprice (Decimal): Estimated sale price in currency.
            esimated_rentprice (Decimal): Estimated rental price in currency.

        Relationships:
            type (PropertyType): Relationship to the PropertyType model.
            user (User): Relationship to the User who posted the property.
            location (Location): Relationship to the property's Location.
    """
    __tablename__ = "properties"

    property_id = Column(Integer, primary_key=True)
    title = Column(String)
    type_id = Column(Integer, ForeignKey('property_types.type_id'))
    deal_type = Column(String)
    status = Column(String)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    location_id = Column(Integer, ForeignKey('locations.location_id'))
    post_date = Column(Date, nullable=False)
    sell_date = Column(Date, nullable=True)
    size_sqm = Column(Float)
    floor = Column(Integer)
    rooms = Column(Integer)
    year_built = Column(Integer)
    renovation_status = Column(String)
    estimated_saleprice = Column(Integer)
    estimated_rentprice = Column(Integer)

    type = relationship("PropertyType")
    user = relationship("User")
    location = relationship("Location")


class Image(Base):
    """
        Represents an image associated with a property listing.

        Attributes:
            image_id (int): Primary key for the image.
            property_id (int): Foreign key referencing the related property.
            image_url (str): URL or path to the image file.

        Relationships:
            property (Property): Relationship to the related Property.
    """
    __tablename__ = "images"

    image_id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('properties.property_id'))
    image_url = Column(String)

    property = relationship("Property")

class Prediction(Base):
    __tablename__ = 'predictions'
    prediction_id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('properties.property_id', ondelete="CASCADE"))
    predicted_sell_price = Column(Integer)
    predicted_rent_price = Column(Integer)
    prob_sold_within_5_months = Column(Float)

    property = relationship("Property")


# Base.metadata.drop_all(engine)
