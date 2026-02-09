from datetime import datetime

from pydantic import BaseModel, PrivateAttr
from fastapi import WebSocket

class QueueEntry(BaseModel):
    rating: float
    joined_at: float
    user_id: int

    _ws: WebSocket | None = PrivateAttr(default=None)

    def __lt__(self, other: "QueueEntry"):
        return (self.rating, self.joined_at) < (other.rating, other.joined_at)


class MessageEvent(BaseModel):
    user_id: int
    text: str
    ts: float # timestamp


class MatchHistoryItem(BaseModel):
    current_player: str
    opponent: str
    current_player_elo_change: float
    opponent_elo_change: float
    result: str
    created_at: datetime

    class Config:
        from_attributes = True