from .database import Base
from sqlalchemy import String, Integer, Column

# DELIVERY TABLE
class Delivery(Base):
    __tablename__='delivery'
    id=Column(Integer,primary_key=True)
    delivery_date=Column(String(10),nullable=False,unique=True)
    delivery_slot=Column(String(10),nullable=False)

# def __repr__(self):
#     return f"<delivery delivery_date={self.delivery_date} delivery_slot={self.delivery_slot}>"

# LOYALTY POINTS
class Points(Base):
    __tablename__='points'
    id=Column(Integer,primary_key=True)
    created_at=Column(String(20),nullable=False)
    customer_id=Column(Integer,nullable=False)
    mode=Column(String(20),nullable=False)
    new_point=Column(String(20),nullable=False)
    old_point=Column(Integer,nullable=False)
    order_id=Column(Integer,nullable=False)
    status=Column(String(20),nullable=False)
    type=Column(String(20),nullable=False)
    updated_at=Column(String(20),nullable=False)

# STOCKISTS
class stockists(Base):
    __tablename__='stockists'
    id=Column(Integer,primary_key=True)
    title=Column(String(100),nullable=False)
    add=Column(String(300),nullable=False)
    city=Column(String(100),nullable=False)
    zip=Column(String(100),nullable=False)
    country=Column(String(100),nullable=False)
    email=Column(String(100),nullable=False)
    url=Column(String(100),nullable=False)
    iso=Column(String(20),nullable=False)
    lat=Column(String(20),nullable=False)
    lng=Column(String(20),nullable=False)

class catbday(Base):
    __tablename__='catbday'
    id=Column(Integer,primary_key=True)
    dob=Column(String(100),nullable=False)
    name=Column(String(300),nullable=False)
    cid=Column(Integer,nullable=False)
 
