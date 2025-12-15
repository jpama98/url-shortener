from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
import uuid

class CreateShortURL(BaseModel):
    target_url: HttpUrl

class ShortURLOut(BaseModel):
    id: uuid.UUID
    code: str
    target_url: str
    short_url: str
    created_at: datetime

    model_config = {"from_attributes": True}

class ClickStatsOut(BaseModel):
    code: str
    total_clicks: int
