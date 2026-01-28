from fastapi import APIRouter, WebSocket
import asyncio
import jwt
from sqlalchemy import select, func
from app.schemas.matchmaking import QueueEntry, AnswerEvent
from app.core.database import SessionDep
from app.core.security import SECRET_KEY
from app.core.models import UserModel, TaskModel
from app.utils.elo import calculate_elo_change, change_elo, WIN, LOSS
import time
import bisect
from app.core.database import new_session
from fastapi.responses import HTMLResponse
from collections import defaultdict


is_connected = defaultdict(bool) # для отслеживания подключенных пользователей т.к. в fastapi'ной имплементации вебсокетов нельзя проверить отключился ли пользователь
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
        is_connected[entry.user_id] = True
        await websocket.send_text(f"Search started")

        # если функция завершится, то она закроет соединение, поэтому ждём пока пользователь отключится
        while is_connected[entry.user_id]:
            await asyncio.sleep(10)
        
        # убираем чтобы не тратить память зря
        del is_connected[entry.user_id]

    except Exception as e:
        print('/pvp/join',e)
        if entry is not None:
            await remove_player(entry)
        try:
            is_connected[user_id] = False
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
    numtasks = 3
    ws1 = player1._ws
    ws2 = player2._ws
    await ws1.send_text(f"match started")
    await ws2.send_text(f"match started")
    try:
        # выбираем рандомные задачи
        async with new_session() as session:
            query = select(TaskModel).order_by(func.random()).limit(numtasks)
            res = await session.execute(query)
            tasks = res.all()
            print('TASKS:',tasks)

        if len(tasks)!=numtasks:
            await ws1.send_text(f"нет задач")
            await ws2.send_text(f"нет задач")
            return
        
        task_ids = [task[0].id for task in tasks]
        correct_answers = {task[0].id:task[0].correct_answer for task in tasks}
        is_answered = {task[0].id:False for task in tasks}

        # отправляем id задач пользователям
        await ws1.send_text(f"{task[0].id} " for task in tasks)
        await ws2.send_text(f"{task[0].id} " for task in tasks)
        
        # ответы обоих игроков добавляются в очередь и обрабатываются по порядку
        answers = asyncio.Queue()

        # ждём ответы
        t1 = asyncio.create_task(listen_answers(player1, answers))
        t2 = asyncio.create_task(listen_answers(player2, answers))

        # счётчики правильных ответов
        anscnt1 = 0
        anscnt2 = 0

        try:
            while True:
                # ответ в формате id ans. Например, "1 aboba"
                rawans = await answers.get()
            
                if rawans is None: # нет ответов
                    await asyncio.sleep(1)
                    continue
                
                # TODO проверка формата ответа

                user_id = rawans.user_id
                task_id,ans = rawans.answer.split()
                task_id = int(task_id)
                
                message = ''
                if task_id in task_ids:
                    if correct_answers[task_id] == ans and not is_answered[task_id]:
                        is_answered[task_id] = True
                        message = "correct"
                        if user_id == player1.user_id: anscnt1+=1
                        else: anscnt2+=1
                    elif is_answered[task_id]:
                        message = "answered"
                    else:
                        message = "incorrect"
                else:
                    message = "invalid id"

                if message:
                    if user_id == player1.user_id: await ws1.send_text(message)
                    else: await ws2.send_text(message)

                if anscnt1 > numtasks//2 or anscnt2 > numtasks//2:
                    if anscnt1 > numtasks//2:
                        elochange = calculate_elo_change(player1.rating, player2.rating, WIN)
                        r1 = await change_elo(player1.user_id,elochange)
                        r2 = await change_elo(player2.user_id,-elochange)
                        winner=1
                    else:
                        elochange = calculate_elo_change(player1.rating, player2.rating, LOSS)
                        r1 = await change_elo(player1.user_id,elochange)
                        r2 = await change_elo(player2.user_id,-elochange)
                        winner=2
                    await ws1.send_text(str("win" if winner==1 else "loss")+f" {r1}")
                    await ws2.send_text(str("win" if winner==2 else "loss")+f" {r2}")
                    await ws1.close()
                    await ws2.close()
                    is_connected[player1.user_id] = False
                    is_connected[player2.user_id] = False
                    return
        finally: # завершаем слушатели ответов
            t1.cancel()
            t2.cancel()
        

    except Exception as e: # если кто-то отключился
        print('pvp start_match,',e)
        is_connected[player1.user_id] = False
        is_connected[player2.user_id] = False
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
    now = time.time()
    async with _queue_lock:
        if not queue: return
        pairs = [] # найденные пары оппонентов
        newqueue = []
        newindex = dict()
        l = len(queue)
        i = 0
        while i < l-1:
            p1 = queue[i]
            p2 = queue[i + 1]

            wait_time = max( # наибольшее время поиска
                now - p1.joined_at,
                now - p2.joined_at
            )
            allowed_elo_diff = 100+wait_time*5 # каждую секунду увеличиваем допустимую разницу в эло на 5

            if p2.rating - p1.rating < allowed_elo_diff: # если подходить, то начинаем матч
                pairs.append((p1,p2))
                i+=2
            else: # иначе оставляем игрока в очереди
                newqueue.append(p1)
                newindex[p1.user_id] = p1
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