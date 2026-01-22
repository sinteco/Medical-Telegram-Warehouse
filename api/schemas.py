from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TopProduct(BaseModel):
    term: str
    frequency: int

class ChannelActivity(BaseModel):
    date: str
    post_count: int
    total_views: int

class MessageSearch(BaseModel):
    message_id: int
    channel_name: str
    date: datetime
    text: str
    views: int

class VisualStats(BaseModel):
    image_category: str
    count: int
    percentage: float

