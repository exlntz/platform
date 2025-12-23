from pydantic import BaseModel

class QueueEntry(BaseModel):
    rating: int
    joined_at: float
    user_id: int