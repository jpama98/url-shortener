from pydantic import BaseModel, EmailStr
import uuid
from datetime import datetime

class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    created_at: datetime

    model_config = {"from_attributes": True}
