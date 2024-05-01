from sqlalchemy.orm import Session
from .models import UserPreferences

def get_user_preferences(db: Session, user_id: int):
    """
    Retrieve user preferences from the database.
    """
    return db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()

def create_or_update_user_preferences(db: Session, user_id: int, email_enabled: bool, sms_enabled: bool, email: str, phone_number: str):
    """
    Create or update user preferences in the database.
    """
    user_preferences = get_user_preferences(db, user_id)
    if user_preferences is None:
        # Create new user preferences if not exist
        user_preferences = UserPreferences(user_id=user_id, email_enabled=email_enabled, sms_enabled=sms_enabled, email=email, phone_number=phone_number)
        db.add(user_preferences)
    else:
        # Update existing user preferences
        user_preferences.email_enabled = email_enabled
        user_preferences.sms_enabled = sms_enabled
        user_preferences.email = email
        user_preferences.phone_number = phone_number
    db.commit()
    return user_preferences
