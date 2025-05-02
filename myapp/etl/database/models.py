from sqlalchemy import Column, Integer, String, Float, ForeignKey, Numeric, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from database import engine

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String, nullable=False)
    phone_number = Column(String)
    user_type = Column(Float)


class Location(Base):
    __tablename__ = "locations"

    location_id = Column(Integer, primary_key=True)
    region = Column(String)
    city = Column(String, nullable=False)
    district = Column(String)


class PropertyType(Base):
    __tablename__ = "property_types"

    type_id = Column(Integer, primary_key=True)
    type_name = Column(String)


class Property(Base):
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
    estimated_saleprice = Column(Numeric(12, 2))
    esimated_rentprice = Column(Numeric(12, 2))

    type = relationship("PropertyType")
    user = relationship("User")
    location = relationship("Location")


class Image(Base):
    __tablename__ = "images"

    image_id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('properties.property_id'))
    image_url = Column(String)

    property = relationship("Property")

class Prediction(Base):
    __tablename__ = "predictions"

    property_id = Column(Integer, primary_key=True, index=True)
    predicted_sell_price = Column(Float)
    predicted_rent_price = Column(Float)
    prob_sold_within_5_months = Column(Float)


Base.metadata.create_all(engine)
