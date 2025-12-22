from pydantic import BaseModel
from fastapi import WebSocket

class QueueEntry(BaseModel):
    rating: int
    joined_at: float
    user: int
    ws: WebSocket