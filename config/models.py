from .database import Base
from sqlalchemy import String,Integer,Column

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
    loyalty_cid=Column(Integer,nullable=False)
    loyalty_type=Column(String(10),nullable=False,unique=True)
    loyalty_date=Column(String(10),nullable=False)
    loyalty_points=Column(Integer,nullable=False)
    loyalty_status=Column(String(10),nullable=False)
