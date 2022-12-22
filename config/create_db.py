from .database import Base,engine
from .models import Delivery

print("Creating database .....")

Base.metadata.create_all(engine)