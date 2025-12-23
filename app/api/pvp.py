from fastapi import APIRouter,HTTPException,status,WebSocket
import asyncio
from app.schemas.matchmaking import QueueEntry
from app.database import SessionDep
# from app.main import UserSchema
from time import time
import bisect

from fastapi.responses import HTMLResponse


queue = [] # комната ожидания, отсортирована по рейтингу
index = dict() # словарь user_id-QueueEntry
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
    print('removing',QueueEntry)
    async with _queue_lock:
        if not index[entry.user_id]:
            return
        queue.remove(entry)
        index[entry.user_id]=None
    print('removed')


@router.websocket('/join') # начать поиск оппонента
async def join_match(session: SessionDep, websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(f"Connected")
    user = {
        'id': 1,
        'name': 'John',
        'mail': 'aomosm@mail.ru',
        'bio': None,
        'elo': 1000
    }
    entry = QueueEntry(
        rating=user['elo'],
        joined_at=time(),
        user_id=user['id']
    )
    await add_player(entry)
    print(queue)
    await websocket.send_text(f"Search started")
    while True:
        try:
            data = await websocket.receive_text()
            if data == "cancel":
                await remove_player(entry)
                print(queue)
        except Exception as e:
            await remove_player(entry)
            break




# всё снизу для тестирования
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/pvp/join");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@router.get("/")
async def get():
    return HTMLResponse(html)