from fastapi import APIRouter,HTTPException,status,WebSocket
import asyncio
import jwt
from sqlalchemy import select
from app.schemas.matchmaking import QueueEntry
from app.database import SessionDep
from app.security import SECRET_KEY
from app.models import UserModel
from app.schemas.user import Token
import time
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
    print('removing',entry)
    async with _queue_lock:
        if entry.user_id not in index:
            return
        queue.remove(entry)
        del index[entry.user_id]
    print('removed')


@router.websocket('/join') # начать поиск оппонента
async def join_match(session: SessionDep, websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Connected")

    token = await websocket.receive_text()
    try:
        tokenData = jwt.decode(token,SECRET_KEY,algorithms=['HS256'])
        await websocket.send_text("token accepted")
    except Exception as e:
        print(e)
        await websocket.send_text("invalid token")
        await websocket.close()

    query=select(UserModel).where(UserModel.email == str(tokenData['sub']))
    result=await session.execute(query)
    user=result.scalar_one_or_none()

    entry = QueueEntry(
        rating=user.rating,
        joined_at=time.time(),
        user_id=user.id
    )
    entry._ws = websocket

    await add_player(entry)
    print(queue)
    await websocket.send_text(f"Search started")
    while True:
        try:
            data = await websocket.receive_text()
            if data == "cancel":
                await remove_player(entry)
                print(queue)
                await websocket.close()
            elif data == "ping":
                await websocket.send_text("pong")
        except Exception as e:
            await remove_player(entry)
            await websocket.close()
            break
    await websocket.close()


async def start_match(player1: QueueEntry, player2: QueueEntry):
    ws1 = player1._ws
    ws2 = player2._ws
    await ws1.send_text(f"Match started {player1.user_id}")
    await ws2.send_text(f"Match started {player2.user_id}")
    return

#ЗАКОМЕНТИЛ ЧТОБЫ КОД НЕ ВЫДАВАЛ ОШИБОК
async def match_players():
    global queue
    global index
    async with _queue_lock:
        if not queue: return
        pairs = [] # найденные пары оппонентов
        newqueue = []
        newindex = dict()
        l = len(queue)
        i = 0
        while i < l-1:
            if queue[i+1].rating - queue[i].rating < 100:
                pairs.append((queue[i],queue[i+1]))
                i+=2
            else:
                newqueue.append(queue[i])
                newindex[queue[i].user_id] = queue[i]
                i+=1
        if i == l-1:
            newqueue.append(queue[i])
            newindex[queue[i].user_id] = queue[i]
        queue = newqueue
        index = newindex

    for p in pairs:
        asyncio.create_task(start_match(p[0], p[1]))


async def matchmaking_loop():
    while True:
        try:
            await match_players()
        except Exception as e:
            print(e)
        await asyncio.sleep(3)

# при запуске начинаем постоянно подбирать всем матчи
@router.on_event("startup")
async def start_matchmaking():
    asyncio.create_task(matchmaking_loop())


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