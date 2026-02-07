from fastapi import APIRouter, WebSocket
import asyncio
import jwt
from sqlalchemy import select, func
from app.schemas.matchmaking import QueueEntry, MessageEvent
from app.core.database import SessionDep
from app.core.config import settings
from app.core.models import UserModel, TaskModel, PvPMatchModel, EloHistoryModel
from app.utils.elo import calculate_elo_change, change_elo, WIN, LOSS, DRAW
from app.utils.formatters import format_answer
import time
import bisect
from app.core.database import new_session
from fastapi.responses import HTMLResponse
from collections import defaultdict, deque

ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY

pending_reconnects = {}  # user_id -> asyncio.Future
is_connected = defaultdict(bool) # для отслеживания подключенных пользователей т.к. в fastapi'ной имплементации вебсокетов нельзя проверить отключился ли пользователь
is_in_match  = defaultdict(bool) # user_id
queue = [] # комната ожидания, отсортирована по рейтингу
index = dict() # словарь user_id-QueueEntry
_queue_lock = asyncio.Lock()

router=APIRouter(prefix='/pvp',tags=['PVP'])

async def add_player(entry: QueueEntry):
    async with _queue_lock:
        old = index.get(entry.user_id)
        if old is not None: # если уже в очереди
            #закрываем старый вебсокет
            try:
                await old._ws.send_text("opponent disconnected")
                await old._ws.close()
            except Exception:
                pass
            queue.remove(old)
            del index[old.user_id]
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
            tokenData = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
            await websocket.send_text("token accepted")
        except Exception as e:
            print(e)
            await websocket.send_text("invalid token")
            await websocket.close()
            return

        query=select(UserModel).where(UserModel.id == int(tokenData['sub']))
        result=await session.execute(query)
        user=result.scalar_one_or_none()

        entry = QueueEntry(
            rating=user.rating,
            joined_at=time.time(),
            user_id=user.id
        )
        entry._ws = websocket


        # если пользователь переподключается
        if user.id in pending_reconnects:
            try:
                # добавляем новый websocket
                pending_reconnects[user.id].set_result(websocket)
            except Exception:
                pass
            is_connected[user.id] = True
            # пока пользователь подключен не завершаем функцию, чтобы не отключится
            while is_connected[user.id]:
                await asyncio.sleep(10)
            del is_connected[user.id]
            return # возвращаем после отключения чтобы игрок не добавился в очередь


        async with _queue_lock:
            if is_in_match[entry.user_id]:
                try:
                    await websocket.send_text(f"already in a match")
                    await websocket.close()
                    return
                except Exception as e:
                    print('pvp join is_in_match  ',e)
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
            is_connected[user.id] = False
            await websocket.close()
        except Exception as e:
            print('/pvp/join',e)
            pass


async def listen_messages(player: QueueEntry, out: asyncio.Queue,):
    ws = player._ws
    try:
        while True:
            msg = await ws.receive_text()
            await out.put(
                MessageEvent(
                    user_id=player.user_id,
                    text=msg,
                    ts=time.time(),
                )
            )
    except Exception:
        await out.put(
            MessageEvent(
                user_id=player.user_id,
                text="__DISCONNECTED__",
                ts=0,
            )
        )
        # вебсокет закрылся
        

async def wait_for_reconnect(user_id: int, timeout: float):
    fut = asyncio.get_event_loop().create_future()
    pending_reconnects[user_id] = fut
    try:
        # ждём пока пользователь переподключится
        new_ws = await asyncio.wait_for(fut, timeout=timeout)
        return new_ws
    except asyncio.TimeoutError:
        return None
    finally:
        pending_reconnects.pop(user_id, None)


async def start_match(player1: QueueEntry, player2: QueueEntry):
    tasktime = 120 # время в секундах на выполнение задачи
    numtasks = 3 # количество задач
    max_cons_ans = 3 # максимальное количество ответов подряд
    ans_window = 10 
    reconnect_timeout = 5 # время в секундах за которое можно переподключиться
    ws1 = player1._ws
    ws2 = player2._ws
    try:
        await ws1.send_text("ping")
    except Exception: # игрок1 отключился, добавляем второго обратно в очередь
        print('pvp start_match player1 disconnected') # DEBUG
        is_connected[player1.user_id] = False
        async with _queue_lock:
            is_in_match[player1.user_id] = False
            is_in_match[player2.user_id] = False
        await add_player(player2)
        return
    try:
        await ws2.send_text("ping")
    except Exception: # игрок2 отключился, добавляем первого обратно в очередь
        print('pvp start_match player2 disconnected') # DEBUG
        is_connected[player2.user_id] = False
        async with _queue_lock:
            is_in_match[player1.user_id] = False
            is_in_match[player2.user_id] = False
        await add_player(player1)
        return
    try:
        await ws1.send_text(f"match started")
        await ws2.send_text(f"match started")
        # выбираем рандомные задачи
        async with new_session() as session:
            query = select(TaskModel).order_by(func.random()).limit(numtasks)
            res = await session.execute(query)
            tasks = res.all()

        if len(tasks)!=numtasks:
            await ws1.send_text(f"нет задач")
            await ws2.send_text(f"нет задач")
            return
        
        task_ids = [task[0].id for task in tasks]
        correct_answers = {task[0].id:format_answer(task[0].correct_answer) for task in tasks}
        is_answered = {task[0].id:False for task in tasks}
        answer_times = {player1.user_id:deque(),player2.user_id:deque()}
        
        # ответы обоих игроков добавляются в очередь и обрабатываются по порядку
        messages = asyncio.Queue()

        # ждём ответы
        t1 = asyncio.create_task(listen_messages(player1, messages))
        t2 = asyncio.create_task(listen_messages(player2, messages))

        # счётчики правильных ответов
        anscnt1 = 0
        anscnt2 = 0
        for task_id in task_ids:
            # заканчиваем если игрок решил больше половины задач
            if max(anscnt1,anscnt2) > numtasks//2: break
            # отправляем id задачи пользователям
            await ws1.send_text(f"{task_id}")
            await ws2.send_text(f"{task_id}")
            timestart = time.time()
            while True:
                now = time.time()
                
                if now-timestart > tasktime:
                    await ws1.send_text("time is up. next task")
                    await ws2.send_text("time is up. next task")
                    break # ломаем цикл чтобы перейти к следующей задаче

                try:
                    msg = await asyncio.wait_for(messages.get(), timeout=1)
                except asyncio.TimeoutError:
                    continue
                
                if msg.text=='__DISCONNECTED__' and msg.ts == 0:
                    discplayer = None # отключившийся игрок
                    if msg.user_id == player1.user_id:
                        discplayer = player1
                    else:
                        discplayer = player2
                    # ждём пока игрок переподключится
                    new_ws = await wait_for_reconnect(discplayer.user_id, timeout=reconnect_timeout)
                    if new_ws:
                        # заменяем ws на новый
                        discplayer._ws = new_ws
                        if msg.user_id == player1.user_id:
                            ws1 = new_ws
                            t1 = asyncio.create_task(listen_messages(player1, messages))
                        else:
                            ws2 = new_ws
                            t2 = asyncio.create_task(listen_messages(player2, messages))
                        await discplayer._ws.send_text("match started")
                        await discplayer._ws.send_text(f"{task_id}")
                        #print("player reconnected") # DEBUG
                        continue # чтобы не обрабатывать дисконнект как ответ

                    else: # игрок не переподключился
                        #print("player did not reconnect") # DEBUG
                        raise Exception # завершаем матч
                
                if msg.text[:14] == 'MessageToChat ':
                    if msg.user_id == player1.user_id: await ws2.send_text(f"chat message {msg.text[14:]}")
                    else: await ws1.send_text(f"chat message {msg.text[14:]}")
                    continue
                
                ans = msg

                times = answer_times[ans.user_id]

                # убираем старые ответы
                while times and now - times[0] > ans_window:
                    times.popleft()
                
                if len(times) >= max_cons_ans:
                    if ans.user_id == player1.user_id:
                        await ws1.send_text(f"please wait {ans_window} seconds between answers")
                    else:
                        await ws2.send_text(f"please wait {ans_window} seconds between answers")
                    continue

                times.append(now)

                if correct_answers[task_id] == format_answer(ans.text):
                    if ans.user_id == player1.user_id:
                        anscnt1+=1
                        await ws1.send_text("correct")
                        await ws2.send_text("other player answered. next task")
                    else:
                        anscnt2+=1
                        await ws1.send_text("other player answered. next task")
                        await ws2.send_text("correct")
                    break # ломаем цикл чтобы перейти к следующей задаче
                else:
                    if ans.user_id == player1.user_id: await ws1.send_text("incorrect")
                    else: await ws2.send_text("incorrect")
        

        if anscnt1 == anscnt2:
            elochange = calculate_elo_change(player1.rating, player2.rating, DRAW)
            winner = 0
        elif anscnt1 > anscnt2:
            elochange = calculate_elo_change(player1.rating, player2.rating, WIN)
            winner = 1
        else:
            elochange = calculate_elo_change(player1.rating, player2.rating, LOSS)
            winner = 2
        
        r1 = await change_elo(player1.user_id,elochange)
        r2 = await change_elo(player2.user_id,-elochange)

        async with new_session() as db_session:

            result = 'draw'
            if winner == 1:
                result = 'win_p1'
            elif winner == 2:
                result = 'win_p2'


            new_match = PvPMatchModel(
                player1_id=player1.user_id,
                player2_id=player2.user_id,
                result=result,
                p1_elo_change=float(elochange),
                p2_elo_change=float(-elochange)
            )
            db_session.add(new_match)

            db_session.add(EloHistoryModel(
                user_id=player1.user_id,
                rating=round(float(r1),1),
                change=float(elochange)
            ))
            db_session.add(EloHistoryModel(
                user_id=player2.user_id,
                rating=round(float(r2),1),
                change=float(-elochange)
            ))

            await db_session.commit()

        await ws1.send_text(str("win" if winner==1 else "loss" if winner==2 else "draw")+f" {r1}")
        await ws2.send_text(str("win" if winner==2 else "loss" if winner==1 else "draw")+f" {r2}")
        await ws1.close()
        await ws2.close()
        is_connected[player1.user_id] = False
        is_connected[player2.user_id] = False
        return

    except Exception as e: # если кто-то отключился
        #print('pvp start_match,',e) #DEBUG
        is_connected[player1.user_id] = False
        is_connected[player2.user_id] = False
        # мы не знаем, кто отключился, поэтому пытаемся отправить сообщение обоим.
        # в кейсе написано, что при разрыве соединения эло не меняется
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
        
        async with new_session() as db_session:

            result = 'cancelled'


            new_match = PvPMatchModel(
                player1_id=player1.user_id,
                player2_id=player2.user_id,
                result=result,
                p1_elo_change=0,
                p2_elo_change=0
            )
            db_session.add(new_match)

            db_session.add(EloHistoryModel(
                user_id=player1.user_id,
                rating=round(player1.rating,1),
                change=0
            ))
            db_session.add(EloHistoryModel(
                user_id=player2.user_id,
                rating=round(player2.rating,1),
                change=0
            ))

            await db_session.commit()

    finally:
        async with _queue_lock:
            is_in_match[player1.user_id] = False
            is_in_match[player2.user_id] = False
        try:
            t1.cancel()
        except Exception:
            pass
        try:
            t2.cancel()
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

            allowed_elo_diff = 50*wait_time # с каждой секундой увеличиваем допустимую разницу в эло

            if p2.rating - p1.rating < allowed_elo_diff: # если подходить, то начинаем матч

                is_in_match[p1.user_id] = True
                is_in_match[p2.user_id] = True
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
    global _matchmaking_task
    _matchmaking_task = asyncio.create_task(matchmaking_loop())

# при остановке перестаём подбирать задачи
@router.on_event("shutdown")
async def stop_matchmaking():
    global _matchmaking_task
    if _matchmaking_task:
        _matchmaking_task.cancel()
        try:
            await _matchmaking_task
        except asyncio.CancelledError:
            pass

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
