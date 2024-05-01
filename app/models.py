from sqlalchemy import Column, Integer, String, Boolean
from .database import Base

class UserPreferences(Base):
    """
    Represents user preferences stored in the database.
    """
    __tablename__ = 'user_preferences'

    user_id = Column(Integer, primary_key=True)
    email_enabled = Column(Boolean, default=False)
    sms_enabled = Column(Boolean, default=False)
    email = Column(String)
    phone_number = Column(String)


