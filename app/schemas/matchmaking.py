from pydantic import BaseModel, PrivateAttr
from fastapi import WebSocket

class QueueEntry(BaseModel):
    rating: int
    joined_at: float
    user_id: int

    _ws: WebSocket | None = PrivateAttr(default=None)

    def __lt__(self, other: "QueueEntry"):
        return (self.rating, self.joined_at) < (other.rating, other.joined_at)