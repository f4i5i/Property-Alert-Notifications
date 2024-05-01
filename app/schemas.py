from pydantic import BaseModel
from typing import Optional

class UserPreferenceRequest(BaseModel):
    """
    Represents a user preference update request.
    """
    email_enabled: bool
    sms_enabled: bool
    email: Optional[str]
    phone_number: Optional[str]

class UserPreferenceResponse(BaseModel):
    """
    Represents a user preference response.
    """
    user_id: int
    email_enabled: bool
    sms_enabled: bool
    email: str
    phone_number: str

    class ConfigDict:
        orm_mode = True