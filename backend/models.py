from sqlalchemy import Column, Integer, String, Boolean
from database import Base # Import the Base class from the database setup

# Define the table structure (SQLAlchemy Model)
class User(Base):
    __tablename__ = "users"

    # Columns:
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    # Optional: A representation for printing/debugging
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"