from fastapi import APIRouter, WebSocket
import asyncio
import jwt
from sqlalchemy import select, func
from app.schemas.matchmaking import QueueEntry, AnswerEvent
from app.core.database import SessionDep
from app.core.security import SECRET_KEY
from app.models import UserModel, TaskModel
from app.utils.elo import calculate_elo_change, WIN, DRAW, LOSS
import time
import bisect
from app.core.database import new_session
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
    entry = None

    try:
        token = await websocket.receive_text()
        try:
            tokenData = jwt.decode(token,SECRET_KEY,algorithms=['HS256'])
            await websocket.send_text("token accepted")
        except Exception as e:
            print(e)
            await websocket.send_text("invalid token")
            await websocket.close()
            return

        query=select(UserModel).where(UserModel.username == str(tokenData['sub']))
        result=await session.execute(query)
        user=result.scalar_one_or_none()

        entry = QueueEntry(
            rating=user.rating,
            joined_at=time.time(),
            user_id=user.id
        )
        entry._ws = websocket

        await add_player(entry)
        await websocket.send_text(f"Search started")

        while True:
            data = await websocket.receive_text()
            if data == "cancel":
                break
            elif data == "ping":
                await websocket.send_text("pong")

    except Exception as e:
        print('/pvp/join',e)
        pass
    
    finally:
        if entry is not None:
            await remove_player(entry)
        try:
            await websocket.close()
        except Exception as e:
            print('/pvp/join',e)
            pass


async def listen_answers(player: QueueEntry, out: asyncio.Queue,):
    ws = player._ws
    try:
        while True:
            msg = await ws.receive_text()
            print(msg)
            await out.put(
                AnswerEvent(
                    user_id=player.user_id,
                    answer=msg,
                    ts=time.time(),
                )
            )
    except Exception:
        pass  # вебсокет закрылся
        

async def start_match(player1: QueueEntry, player2: QueueEntry):
    ws1 = player1._ws
    ws2 = player2._ws
    try:
        # выбираем рандомную задачу
        async with new_session() as session:
            query = select(TaskModel).order_by(func.random()).limit(1)
            res = await session.execute(query)
            task = res.scalar_one_or_none()

        if task is None:
            await ws1.send_text(f"нет задач")
            await ws2.send_text(f"нет задач")
            return

        # отправляем id задачи пользователям
        await ws1.send_text(f"{task.id}")
        await ws2.send_text(f"{task.id}")
        
        # ответы обоих игроков добавляются в очередь и обрабатываются по порядку
        answers = asyncio.Queue()

        # ждём ответы
        t1 = asyncio.create_task(listen_answers(player1, answers))
        t2 = asyncio.create_task(listen_answers(player2, answers))

        try:
            while True:
                ans = await answers.get()
            
                if ans is None: # нет ответов
                    asyncio.sleep(1)
                    continue
                print('ANS',ans)
                if ans.answer == task.correct_answer:
                    if ans.user_id == player1.user_id:
                        elochange = calculate_elo_change(player1.rating, player2.rating, WIN)
                        #TODO сделать функцию change_elo
                        #await change_elo(player1.user_id,elochange)
                        #await change_elo(player2.user_id,-elochange)
                    else:
                        elochange = calculate_elo_change(player1.rating, player2.rating, LOSS)
                        #TODO сделать функцию change_elo
                        #await change_elo(player1.user_id,elochange)
                        #await change_elo(player2.user_id,-elochange)
                    await ws1.send_text("win" if player1.user_id == ans.user_id else "loss")
                    await ws2.send_text("win" if player2.user_id == ans.user_id else "loss")
                    await ws1.close()
                    await ws2.close()
                    return

                else:
                    if ans.user_id == player1.user_id:
                        await ws1.send_text(f"ответ {ans.answer} неправильный")
                    else:
                        await ws2.send_text(f"ответ {ans.answer} неправильный")
        finally: # завершаем слушатели ответов
            print('END_T')
            t1.cancel()
            t2.cancel()
        

    except Exception as e: # если кто-то отключился
        print('pvp start_match,',e)
        # мы не знаем, кто отключился, поэтому пытаемся отправить сообщение обоим.
        try:
            await ws1.send_text("opponent disconnected")
            await ws1.close()
        except Exception:
            pass

        try:
            await ws2.send_text("opponent disconnected")
            await ws2.close()
        except Exception:
            pass


    return


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