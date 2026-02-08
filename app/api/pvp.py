from fastapi import APIRouter, WebSocket, Query
import asyncio
import jwt
from sqlalchemy import select, func, or_
from sqlalchemy.orm import aliased
from app.core.dependencies import UserDep
from app.schemas.matchmaking import QueueEntry, MessageEvent, MatchHistoryItem
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
from app.utils.elo import ELO_RANKS

ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY

pending_reconnects = {}  # user_id -> asyncio.Future
is_connected = defaultdict(
    bool)  # для отслеживания подключенных пользователей т.к. в fastapi'ной имплементации вебсокетов нельзя проверить отключился ли пользователь
is_in_match = defaultdict(bool)  # user_id
queue = []  # комната ожидания, отсортирована по рейтингу
index = dict()  # словарь user_id-QueueEntry
_queue_lock = asyncio.Lock()

router = APIRouter(prefix='/pvp', tags=['PVP'])


async def add_player(entry: QueueEntry):
    async with _queue_lock:
        old = index.get(entry.user_id)
        if old is not None:  # если уже в очереди
            # закрываем старый вебсокет
            try:
                await old._ws.send_text("opponent disconnected")
                await old._ws.close()
            except Exception:
                pass
            queue.remove(old)
            del index[old.user_id]
        idx = bisect.bisect_left(queue, entry)  # ищем куда вставить чтобы не поломать сортировку
        queue.insert(idx, entry)
        index[entry.user_id] = entry


async def remove_player(entry: QueueEntry):
    print('removing', entry)
    async with _queue_lock:
        if entry.user_id not in index:
            return
        queue.remove(entry)
        del index[entry.user_id]
    print('removed')


@router.websocket('/join')  # начать поиск оппонента
async def join_match(session: SessionDep, websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Connected")
    entry = None
    user = None  # Инициализируем user, чтобы в блоке except можно было проверить user.id

    try:
        token = await websocket.receive_text()
        try:
            tokenData = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            await websocket.send_text("token accepted")
        except Exception as e:
            print(e)
            await websocket.send_text("invalid token")
            await websocket.close()
            return

        query = select(UserModel).where(UserModel.id == int(tokenData['sub']))
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            await websocket.close()
            return

        entry = QueueEntry(
            rating=user.rating,
            joined_at=time.time(),
            user_id=user.id
        )
        entry._ws = websocket

        # === ЛОГИКА РЕКОННЕКТА (ИЗМЕНЕНО) ===

        # 1. Если пользователь числится в матче, но слот для реконнекта еще не готов (Race Condition при F5)
        if is_in_match[user.id] and user.id not in pending_reconnects:
            # Ждем немного (до 3 сек), пока цикл матча поймет, что старый сокет отвалился
            for _ in range(30):
                if user.id in pending_reconnects:
                    break
                await asyncio.sleep(0.1)

        # 2. Если слот для реконнекта существует -> подключаем к текущему матчу
        if user.id in pending_reconnects:
            try:
                # Передаем новый вебсокет в ожидающую Future
                pending_reconnects[user.id].set_result(websocket)
            except Exception:
                pass

            is_connected[user.id] = True

            # Держим соединение открытым, пока цикл матча не завершится или юзер не выйдет
            while is_connected[user.id]:
                await asyncio.sleep(5)

            # Удаляем флаг подключения только при выходе
            if user.id in is_connected:
                del is_connected[user.id]
            return

        async with _queue_lock:
            if is_in_match[entry.user_id]:
                try:
                    await websocket.send_text(f"already in a match")
                    await websocket.close()
                    return
                except Exception as e:
                    print('pvp join is_in_match  ', e)

        await add_player(entry)
        is_connected[entry.user_id] = True
        await websocket.send_text(f"Search started")

        # если функция завершится, то она закроет соединение, поэтому ждём пока пользователь отключится
        while is_connected[entry.user_id]:
            await asyncio.sleep(10)

        # убираем чтобы не тратить память зря
        if user.id in is_connected:
            del is_connected[entry.user_id]

    except Exception as e:
        print('/pvp/join error:', e)
        if entry is not None:
            await remove_player(entry)
        try:
            if user:
                is_connected[user.id] = False
            await websocket.close()
        except Exception as e:
            pass


async def listen_messages(player: QueueEntry, out: asyncio.Queue, ):
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
    # Создаем Future для ожидания нового вебсокета
    loop = asyncio.get_running_loop()
    fut = loop.create_future()
    pending_reconnects[user_id] = fut
    try:
        # ждём пока пользователь переподключится
        new_ws = await asyncio.wait_for(fut, timeout=timeout)
        return new_ws
    except asyncio.TimeoutError:
        return None
    finally:
        # Очищаем слот реконнекта
        pending_reconnects.pop(user_id, None)


async def start_match(player1: QueueEntry, player2: QueueEntry):
    tasktime = 120  # время в секундах на выполнение задачи
    numtasks = 3  # количество задач
    max_cons_ans = 3  # максимальное количество ответов подряд
    ans_window = 10
    reconnect_timeout = 15  # УВЕЛИЧИЛИ ВРЕМЯ НА РЕКОННЕКТ

    ws1 = player1._ws
    ws2 = player2._ws

    # Helper для проверки пинга перед стартом
    async def safe_ping(ws):
        try:
            await ws.send_text("ping")
            return True
        except:
            return False

    if not await safe_ping(ws1):
        is_connected[player1.user_id] = False
        async with _queue_lock:
            is_in_match[player1.user_id] = False
            is_in_match[player2.user_id] = False
        await add_player(player2)
        return

    if not await safe_ping(ws2):
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

        if len(tasks) != numtasks:
            await ws1.send_text(f"нет задач")
            await ws2.send_text(f"нет задач")
            return

        task_ids = [task[0].id for task in tasks]
        correct_answers = {task[0].id: format_answer(task[0].correct_answer) for task in tasks}
        is_answered = {task[0].id: False for task in tasks}
        answer_times = {player1.user_id: deque(), player2.user_id: deque()}

        # ответы обоих игроков добавляются в очередь и обрабатываются по порядку
        messages = asyncio.Queue()

        # ждём ответы
        t1 = asyncio.create_task(listen_messages(player1, messages))
        t2 = asyncio.create_task(listen_messages(player2, messages))

        # счётчики правильных ответов
        anscnt1 = 0
        anscnt2 = 0

        # === ЦИКЛ ЗАДАЧ ===
        for i, task_id in enumerate(task_ids):
            # заканчиваем если игрок решил больше половины задач
            if max(anscnt1, anscnt2) > numtasks // 2: break

            # === ЗАДЕРЖКА ПЕРЕД СЛЕДУЮЩЕЙ ЗАДАЧЕЙ (для таймера на фронте) ===
            if i > 0:
                await asyncio.sleep(3)

            # отправляем id задачи пользователям
            # Оборачиваем в try-except, так как при sleep соединение могло упасть
            try:
                await ws1.send_text(f"{task_id}")
            except:
                pass
            try:
                await ws2.send_text(f"{task_id}")
            except:
                pass

            timestart = time.time()

            while True:
                now = time.time()

                if now - timestart > tasktime:
                    try:
                        await ws1.send_text("time is up. next task")
                    except:
                        pass
                    try:
                        await ws2.send_text("time is up. next task")
                    except:
                        pass
                    break  # ломаем цикл чтобы перейти к следующей задаче

                try:
                    msg = await asyncio.wait_for(messages.get(), timeout=1)
                except asyncio.TimeoutError:
                    continue

                # === ОБРАБОТКА ДИСКОННЕКТА И РЕКОННЕКТА ===
                if msg.text == '__DISCONNECTED__' and msg.ts == 0:
                    discplayer = None  # отключившийся игрок
                    if msg.user_id == player1.user_id:
                        discplayer = player1
                    else:
                        discplayer = player2

                    print(f"Player {discplayer.user_id} disconnected. Waiting for reconnect...")

                    # ждём пока игрок переподключится
                    new_ws = await wait_for_reconnect(discplayer.user_id, timeout=reconnect_timeout)

                    if new_ws:
                        # заменяем ws на новый
                        discplayer._ws = new_ws
                        # Перезапускаем слушатель для этого игрока
                        if msg.user_id == player1.user_id:
                            ws1 = new_ws
                            t1.cancel()
                            t1 = asyncio.create_task(listen_messages(player1, messages))
                        else:
                            ws2 = new_ws
                            t2.cancel()
                            t2 = asyncio.create_task(listen_messages(player2, messages))

                        # Отправляем состояние матча вернувшемуся игроку
                        await discplayer._ws.send_text("match started")
                        await discplayer._ws.send_text("already in a match")  # Маркер для фронта
                        await discplayer._ws.send_text(f"{task_id}")

                        print(f"Player {discplayer.user_id} reconnected!")
                        continue  # чтобы не обрабатывать дисконнект как ответ

                    else:  # игрок не переподключился
                        print(f"Player {discplayer.user_id} failed to reconnect.")
                        raise Exception  # завершаем матч

                if msg.text.startswith('SendEmoji '):
                    emoji_content = msg.text[10:]  # Отрезаем "SendEmoji "

                    # Пересылаем сопернику
                    target_ws = ws2 if msg.user_id == player1.user_id else ws1
                    try:
                        await target_ws.send_text(f"emoji {emoji_content}")
                    except:
                        pass
                    continue
                # ==========================
                if msg.text[:14] == 'MessageToChat ':
                    target_ws = ws2 if msg.user_id == player1.user_id else ws1
                    try:
                        await target_ws.send_text(f"chat message {msg.text[14:]}")
                    except:
                        pass
                    continue

                ans = msg

                times = answer_times[ans.user_id]

                # убираем старые ответы
                while times and now - times[0] > ans_window:
                    times.popleft()

                # Определяем кому слать ответ
                current_ws = ws1 if ans.user_id == player1.user_id else ws2

                if len(times) >= max_cons_ans:
                    try:
                        await current_ws.send_text(f"please wait {ans_window} seconds between answers")
                    except:
                        pass
                    continue

                times.append(now)

                if correct_answers[task_id] == format_answer(ans.text):
                    if ans.user_id == player1.user_id:
                        anscnt1 += 1
                        try:
                            await ws1.send_text("correct")
                        except:
                            pass
                        try:
                            await ws2.send_text("other player answered. next task")
                        except:
                            pass
                    else:
                        anscnt2 += 1
                        try:
                            await ws1.send_text("other player answered. next task")
                        except:
                            pass
                        try:
                            await ws2.send_text("correct")
                        except:
                            pass
                    break  # ломаем цикл чтобы перейти к следующей задаче
                else:
                    try:
                        await current_ws.send_text("incorrect")
                    except:
                        pass

        if anscnt1 == anscnt2:
            elochange = calculate_elo_change(player1.rating, player2.rating, DRAW)
            winner = 0
        elif anscnt1 > anscnt2:
            elochange = calculate_elo_change(player1.rating, player2.rating, WIN)
            winner = 1
        else:
            elochange = calculate_elo_change(player1.rating, player2.rating, LOSS)
            winner = 2

        r1 = await change_elo(player1.user_id, elochange)
        r2 = await change_elo(player2.user_id, -elochange)

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
                rating=round(float(r1), 1),
                change=float(elochange)
            ))
            db_session.add(EloHistoryModel(
                user_id=player2.user_id,
                rating=round(float(r2), 1),
                change=float(-elochange)
            ))

            await db_session.commit()

        try:
            await ws1.send_text(str("win" if winner == 1 else "loss" if winner == 2 else "draw") + f" {r1}")
        except:
            pass
        try:
            await ws2.send_text(str("win" if winner == 2 else "loss" if winner == 1 else "draw") + f" {r2}")
        except:
            pass

        try:
            await ws1.close()
        except:
            pass
        try:
            await ws2.close()
        except:
            pass

        is_connected[player1.user_id] = False
        is_connected[player2.user_id] = False
        return

    except Exception as e:  # если кто-то отключился окончательно
        print('pvp start_match exception:', e)
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
                rating=round(player1.rating, 1),
                change=0
            ))
            db_session.add(EloHistoryModel(
                user_id=player2.user_id,
                rating=round(player2.rating, 1),
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
        pairs = []  # найденные пары оппонентов
        newqueue = []
        newindex = dict()
        l = len(queue)
        i = 0
        while i < l - 1:
            p1 = queue[i]
            p2 = queue[i + 1]

            wait_time = max(  # наибольшее время поиска
                now - p1.joined_at,
                now - p2.joined_at
            )

            allowed_elo_diff = 50 * wait_time  # с каждой секундой увеличиваем допустимую разницу в эло

            if abs(p2.rating - p1.rating) < allowed_elo_diff:  # если подходить, то начинаем матч

                is_in_match[p1.user_id] = True
                is_in_match[p2.user_id] = True
                pairs.append((p1, p2))
                i += 2
            else:  # иначе оставляем игрока в очереди
                newqueue.append(p1)
                newindex[p1.user_id] = p1
                i += 1
        if i == l - 1:
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


@router.get('/matches_history', summary='История игр для пвп')
async def get_matches_history(
        session: SessionDep,
        user: UserDep,
        limit: int = Query(default=10, le=50),
        offset: int = 0
):
    Player1 = aliased(UserModel)
    Player2 = aliased(UserModel)

    query = (
        select(
            PvPMatchModel.id,
            PvPMatchModel.player1_id,
            PvPMatchModel.player2_id,
            Player1.username.label("p1_name"),
            Player2.username.label("p2_name"),
            PvPMatchModel.p1_elo_change,
            PvPMatchModel.p2_elo_change,
            PvPMatchModel.result,
            PvPMatchModel.created_at
        )
        .join(Player1, PvPMatchModel.player1_id == Player1.id)
        .join(Player2, PvPMatchModel.player2_id == Player2.id)
        .where(or_(PvPMatchModel.player1_id == user.id, PvPMatchModel.player2_id == user.id))
        .order_by(PvPMatchModel.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    result = await session.execute(query)
    matches: list[PvPMatchModel] = result.all()

    response_list = []

    for row in matches:
        is_p1 = row.player1_id == user.id

        if is_p1:
            current_player_name = row.p1_name
            opponent_name = row.p2_name
            my_elo_change = row.p1_elo_change
            opponent_elo_change = row.p2_elo_change
        else:
            current_player_name = row.p2_name
            opponent_name = row.p1_name
            my_elo_change = row.p2_elo_change
            opponent_elo_change = row.p1_elo_change

        if row.result == 'draw':
            match_outcome = 'Ничья'
        elif row.result == "cancelled":
            match_outcome = 'Матч отменен'
        elif my_elo_change > 0:
            match_outcome = 'Победа'
        else:
            match_outcome = 'Проигрыш'

        response_list.append(MatchHistoryItem(
            current_player=current_player_name,
            opponent=opponent_name,
            current_player_elo_change=my_elo_change,
            opponent_elo_change=opponent_elo_change,
            result=match_outcome,
            created_at=row.created_at
        ))

    return response_list


@router.get('/ranks_info', summary='Возвращает инфу про ранги')
async def get_ranks_info():
    return ELO_RANKS