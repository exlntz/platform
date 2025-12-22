from fastapi import APIRouter,HTTPException,status,WebSocket
from time import time
import bisect


queue: List[QueueEntry] = [] # отсортирован по рейтингу
index: Dict[int, QueueEntry] = {} # словарь по user_id
_queue_lock = asyncio.Lock()

router=APIRouter(prefix='/pvp',tags=['PVP'])

async def add_player(entry: QueueEntry):
    async with _queue_lock:
        if entry.user_id in index: # если уже в очереди, то не добавляем
            return
        idx = bisect.bisect_left(queue, entry) # ищем куда вставить чтобы не поломать сортировку
        queue.insert(idx, entry)
        index[entry.user_id] = entry


async def remove_player(entry: QueueEntry):
    async with _queue_lock:
        if not index[entry.user_id]:
            return
        queue.pop(entry)
        index.pop(entry.user_id)


@router.websocket('/join') # начать поиск оппонента
async def join_match(user: UserSchema, session: SessionDep, websocket: WebSocket):
    await websocket.accept()
    entry = QueueEntry(
        rating=user.elo,
        joined_at=time.time(),
        user_id=user.id,
        ws=websocket
    )
    add_player(entry)
    websocket.send_text(f"Search started")
    while True:
        data = await websocket.receive_text()
        if msg == "cancel":
            remove_player(entry)
    except WebSocketDisconnect:
        remove_player(entry)
