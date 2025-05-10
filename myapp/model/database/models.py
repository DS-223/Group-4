from sqlalchemy import Column, Integer, String, Float, ForeignKey, Numeric, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import date
from .engine import engine  # Make sure this points to your actual engine

Base = declarative_base()
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String, nullable=False)
    phone_number = Column(String(20))
    user_type = Column(String(20))
    properties = relationship("Property", back_populates="user")

class PropertyType(Base):
    __tablename__ = 'property_types'
    type_id = Column(Integer, primary_key=True)
    type_name = Column(String)
    properties = relationship("Property", back_populates="property_type")

class Location(Base):
    __tablename__ = 'locations'
    location_id = Column(Integer, primary_key=True)
    city = Column(String(50))
    district = Column(String(50))
    properties = relationship("Property", back_populates="location")

class Property(Base):
    __tablename__ = 'properties'
    property_id = Column(Integer, primary_key=True)
    title = Column(String(100))
    type_id = Column(Integer, ForeignKey('property_types.type_id'))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    location_id = Column(Integer, ForeignKey('locations.location_id'))
    deal_type = Column(String(10))
    status = Column(String(20))
    post_date = Column(Date)
    sale_date = Column(Date)
    size_sqm = Column(Float)
    floor = Column(Integer)
    rooms = Column(Integer)
    year_built = Column(Integer)
    renovation_status = Column(String(50))
    estimated_saleprice = Column(Numeric(12, 2))
    estimated_rentprice = Column(Numeric(12, 2))
    property_type = relationship("PropertyType", back_populates="properties")
    user = relationship("User", back_populates="properties")
    location = relationship("Location", back_populates="properties")
    images = relationship("Image", back_populates="property")
    predictions = relationship("Prediction", back_populates="property")

class Image(Base):
    __tablename__ = 'images'
    image_id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('properties.property_id'))
    image_url = Column(String(255))
    property = relationship("Property", back_populates="images")

class Prediction(Base):
    __tablename__ = 'predictions'
    prediction_id = Column(Integer, Sequence('prediction_id_seq'), primary_key=True)
    property_id = Column(Integer, ForeignKey('properties.property_id'))
    predicted_sell_price = Column(Numeric(12, 2))
    predicted_rent_price = Column(Numeric(12, 2))
    prob_sold_within_5_months = Column(Float)
    property = relationship("Property", back_populates="predictions")

def initialize_database():
    try:
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        print("Database initialized successfully")

        session = Session()

        # Seed required data
        user = User(username='John Doe', email='john@example.com', phone_number='1234567890', user_type='agent')
        location = Location(city='Yerevan', district='Kentron')
        ptype = PropertyType(type_name='Apartment')

        session.add_all([user, location, ptype])
        session.commit()

        property = Property(
            title='Nice Apartment',
            user_id=user.user_id,
            location_id=location.location_id,
            type_id=ptype.type_id,
            deal_type='sell',
            status='available',
            post_date=date.today(),
            sale_date=None,
            size_sqm=85.0,
            floor=3,
            rooms=3,
            year_built=2015,
            renovation_status='new',
            estimated_saleprice=120000.00,
            estimated_rentprice=800.00
        )
        session.add(property)
        session.commit()

        prediction = Prediction(
            property_id=property.property_id,
            predicted_sell_price=123000.00,
            predicted_rent_price=850.00,
            prob_sold_within_5_months=0.85
        )
        session.add(prediction)
        session.commit()

        print("Sample data inserted successfully")

    except Exception as e:
        print(f"Database initialization failed: {str(e)}")
        raise

initialize_database()
