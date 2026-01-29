<script setup>
import { ref, onUnmounted, nextTick, computed } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()

// --- СОСТОЯНИЕ ---
const socket = ref(null)
const gameState = ref('idle') // 'idle' | 'searching' | 'playing' | 'result'
const gameResult = ref(null) // 'win' | 'loss' | 'disconnect'
const activeTask = ref(null)
const userAnswer = ref('')
const logs = ref([])
const logContainer = ref(null)

// Моковые данные для статистики (можно потом подтянуть с бэка)
const stats = ref({ rank: "Gold IV", points: 1250, winStreak: 3 })
const leaderboard = ref([
  { id: 1, name: "Alex_Pro", points: 2840, avatar: "⚔️" },
  { id: 2, name: "Olimpiad_Master", points: 2710, avatar: "🔥" },
  { id: 3, name: "PythonLover", points: 2590, avatar: "🐍" }
])

// Вычисляемые свойства для результатов
const resultTitle = computed(() => {
  switch (gameResult.value) {
    case 'win': return 'Победа! 🎉'
    case 'loss': return 'Поражение 😔'
    case 'disconnect': return 'Соперник вышел'
    default: return ''
  }
})

const resultDescription = computed(() => {
  switch (gameResult.value) {
    case 'win': return 'Ты решил задачу быстрее соперника! +15 рейтинга'
    case 'loss': return 'Соперник был быстрее. Не сдавайся!'
    case 'disconnect': return 'Противник покинул игру. Тебе засчитана победа!'
    default: return ''
  }
})

const resultTitleClass = computed(() => {
  return {
    'text-win': gameResult.value === 'win',
    'text-loss': gameResult.value === 'loss',
    'text-disconnect': gameResult.value === 'disconnect'
  }
})

// --- ЛОГИКА WEBSOCKET ---
const connectPvp = () => {
  const token = localStorage.getItem('user-token')
  if (!token) {
    alert('Сначала войдите в аккаунт!')
    router.push('/auth')
    return
  }

  // Сбрасываем состояние перед новой игрой
  gameState.value = 'searching'
  gameResult.value = null
  activeTask.value = null
  logs.value = []
  userAnswer.value = ''

  // Подключение (используем localhost, как в backend main.py)
  socket.value = new WebSocket('ws://127.0.0.1:8000/pvp/join')

  socket.value.onopen = () => {
    addLog('system', 'Соединение установлено...')
  }

  socket.value.onmessage = async (event) => {
    const msg = event.data
    console.log('WS Message:', msg)

    // 1. Рукопожатие и авторизация
    if (msg === 'Connected') {
      socket.value.send(token) // Отправляем токен сразу после подключения
    }
    else if (msg === 'token accepted') {
      addLog('system', 'Авторизация успешна. Ищем противника...')
    }
    else if (msg === 'invalid token') {
      alert('Ошибка авторизации. Попробуйте перезайти.')
      socket.value.close()
      router.push('/auth')
    }
    else if (msg === 'Search started') {
      // Уже обработано визуально статусом 'searching'
    }

    // 2. Старт матча
    else if (msg === 'match started') {
      gameState.value = 'playing'
      addLog('system', 'Матч начался! Ждем задачу...')
    }
    else if (msg === 'нет задач') {
      alert('В базе нет задач для игры!')
      disconnect()
    }

    // 3. Получение ID задачи (проверяем, является ли сообщение числом)
    else if (!isNaN(parseInt(msg)) && msg.length < 10) {
      await loadTask(msg)
    }

    // 4. Игровой процесс
    else if (msg.includes('неправильный')) {
      addLog('error', 'Неверно! Попробуй еще раз.')
    }

    // 5. Результаты
    else if (msg === 'win') {
      finishGame('win')
    }
    else if (msg === 'loss') {
      finishGame('loss')
    }
    else if (msg === 'opponent disconnected') {
      finishGame('disconnect')
    }
  }

  socket.value.onclose = () => {
    if (gameState.value === 'searching' || gameState.value === 'playing') {
      gameState.value = 'idle'
    }
  }

  socket.value.onerror = (e) => {
    console.error('WebSocket error:', e)
    addLog('error', 'Ошибка соединения')
    gameState.value = 'idle'
  }
}

// Отправка ответа
const sendAnswer = () => {
  if (!userAnswer.value.trim() || !socket.value) return

  socket.value.send(userAnswer.value)
  addLog('user', userAnswer.value) // Показываем свой ответ в чате
  userAnswer.value = ''
}

// Загрузка деталей задачи по ID
const loadTask = async (taskId) => {
  try {
    const token = localStorage.getItem('user-token')
    const response = await axios.get(`http://127.0.0.1:8000/tasks/${taskId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    activeTask.value = response.data
    addLog('system', 'Задача получена! Решайте быстрее!')
  } catch (e) {
    console.error('Ошибка загрузки задачи:', e)
    addLog('error', 'Не удалось загрузить условие задачи')
  }
}

// Завершение игры
const finishGame = (result) => {
  gameResult.value = result
  gameState.value = 'result'
  if (socket.value) socket.value.close()
}

// Принудительный разрыв
const disconnect = () => {
  if (socket.value) socket.value.close()
  gameState.value = 'idle'
}

// Логирование в чат
const addLog = (type, text) => {
  logs.value.push({ type, text, id: Date.now() })
  nextTick(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = logContainer.value.scrollHeight
    }
  })
}

// Чистим за собой
onUnmounted(() => {
  if (socket.value) socket.value.close()
})
</script>

<template>
  <div class="pvp-container">
    <div class="pvp-grid">
      <div class="main-section">
        <div v-if="gameState === 'idle'" class="idle-state">
          <div class="arena-badge">PvP Arena</div>
          <h1 class="arena-title">Готов к битве?</h1>
          <p class="arena-description">Сразись с реальным противником. Кто первый решит задачу — забирает рейтинг.</p>

          <button
            @click="connectPvp"
            class="find-opponent-btn"
          >
            Найти противника
          </button>
        </div>

        <div v-else-if="gameState === 'searching'" class="searching-state">
          <div class="searching-spinner">
            <div class="spinner-ring"></div>
            <div class="spinner-icon">⚔️</div>
          </div>
          <div class="searching-text">
            <h2>Поиск оппонента...</h2>
            <p>Подбираем равного по силе соперника</p>
          </div>
          <button @click="disconnect" class="cancel-btn">Отмена</button>
        </div>

        <div v-else-if="gameState === 'playing'" class="playing-state">
          <div class="match-header">
            <div class="match-status">
              <span class="live-dot"></span>
              <span class="live-text">Live Match</span>
            </div>
            <div class="match-hint">Решай быстрее!</div>
          </div>

          <div class="task-container">
            <div v-if="activeTask" class="task-content">
              <div class="task-tags">
                <span class="subject-tag">{{ activeTask.subject }}</span>
                <span class="difficulty-tag">{{ activeTask.difficulty }}</span>
              </div>
              <h2 class="task-title">{{ activeTask.title }}</h2>
              <div class="task-description">
                <p>{{ activeTask.description }}</p>
              </div>
            </div>
            <div v-else class="loading-task">
              Загрузка задачи...
            </div>
          </div>

          <div class="game-controls">
            <div ref="logContainer" class="game-logs">
              <div v-for="log in logs" :key="log.id" class="log-message">
                <span v-if="log.type === 'system'" class="log-system">🤖 {{ log.text }}</span>
                <span v-else-if="log.type === 'error'" class="log-error">❌ {{ log.text }}</span>
                <span v-else class="log-user">👤 Вы: {{ log.text }}</span>
              </div>
            </div>

            <form @submit.prevent="sendAnswer" class="answer-form">
              <input
                v-model="userAnswer"
                placeholder="Введите ответ..."
                class="answer-input"
                autoFocus
              >
              <button type="submit" class="submit-answer-btn">
                Отправить
              </button>
            </form>
          </div>
        </div>

        <div v-else-if="gameState === 'result'" class="result-state">
          <div class="result-icon">
            <span v-if="gameResult === 'win'">🏆</span>
            <span v-else-if="gameResult === 'loss'">💀</span>
            <span v-else>🔌</span>
          </div>
          <div class="result-text">
            <h1 :class="resultTitleClass">
              {{ resultTitle }}
            </h1>
            <p class="result-description">
              {{ resultDescription }}
            </p>
          </div>
          <button @click="connectPvp" class="play-again-btn">
            Играть снова
          </button>
        </div>
      </div>

      <div class="sidebar-section">
        <div class="stats-card">
          <h3 class="stats-title">Твои успехи</h3>
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-label">Ранг</span>
              <span class="stat-value rank-value">{{ stats.rank }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Очки</span>
              <span class="stat-value points-value">{{ stats.points }}</span>
            </div>
          </div>
        </div>

        <div class="leaderboard-card">
          <div class="leaderboard-header">🏆 ТОП МАСТЕРОВ</div>
          <div class="leaderboard-list">
            <div v-for="(player, index) in leaderboard" :key="player.id" class="leaderboard-item">
              <span class="player-rank">#{{ index + 1 }}</span>
              <div class="player-avatar">
                {{ player.avatar }}
              </div>
              <div class="player-info">
                <p class="player-name">{{ player.name }}</p>
                <p class="player-points">{{ player.points }} PTS</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ==================== БАЗОВЫЕ СТИЛИ ==================== */

.pvp-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #f0f9ff 100%);
  padding: 16px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  line-height: 1.5;
}

.pvp-grid {
  max-width: 1000px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

/* Основная секция */
.main-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Состояние ожидания */
.idle-state {
  position: relative;
  overflow: hidden;
  background-color: #0f172a;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  min-height: 280px;
}

.arena-badge {
  display: inline-block;
  padding: 4px 12px;
  background-color: rgba(79, 70, 229, 0.2);
  color: rgba(199, 210, 254, 0.8);
  font-size: 9px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  border-radius: 20px;
  border: 1px solid rgba(79, 70, 229, 0.3);
  margin-bottom: 16px;
}

.arena-title {
  font-size: 28px;
  font-weight: 800;
  color: white;
  letter-spacing: -0.025em;
  margin-bottom: 12px;
  line-height: 1.2;
}

.arena-description {
  color: #a5b4fc;
  max-width: 100%;
  font-weight: 500;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 24px;
}

.find-opponent-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 24px;
  background-color: #22c55e;
  color: white;
  font-weight: 800;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  box-shadow: 0 6px 12px -3px rgba(34, 197, 94, 0.2);
  transition: all 0.2s ease;
  font-size: 14px;
  position: relative;
  z-index: 10;
}

.find-opponent-btn:hover {
  background-color: #16a34a;
  transform: translateY(-2px);
}

.find-opponent-btn:active {
  transform: translateY(0);
}

/* Состояние поиска */
.searching-state {
  background-color: white;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #f1f5f9;
  min-height: 280px;
}

.searching-spinner {
  position: relative;
  width: 60px;
  height: 60px;
}

.spinner-ring {
  width: 100%;
  height: 100%;
  border: 3px solid #e0e7ff;
  border-top-color: #4f46e5;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.spinner-icon {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.searching-text h2 {
  font-size: 20px;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 6px;
}

.searching-text p {
  color: #64748b;
  font-weight: 500;
  font-size: 14px;
}

.cancel-btn {
  font-size: 13px;
  font-weight: 700;
  color: #ef4444;
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s ease;
  padding: 8px 16px;
  border-radius: 8px;
}

.cancel-btn:hover {
  color: #dc2626;
  background-color: #fef2f2;
}

/* Состояние игры */
.playing-state {
  background-color: white;
  border-radius: 16px;
  border: 1px solid #f1f5f9;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 500px;
  max-height: 600px;
}

.match-header {
  background-color: #0f172a;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
  flex-shrink: 0;
}

.match-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.live-dot {
  width: 8px;
  height: 8px;
  background-color: #ef4444;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.live-text {
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-size: 12px;
}

.match-hint {
  font-size: 11px;
  font-weight: 700;
  color: #a5b4fc;
}

.task-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #f8fafc;
}

.task-content {
  width: 100%;
}

.task-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.subject-tag {
  padding: 4px 10px;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 9px;
  font-weight: 800;
  text-transform: uppercase;
  color: #475569;
}

.difficulty-tag {
  padding: 4px 10px;
  background-color: #e0e7ff;
  border: 1px solid #c7d2fe;
  color: #4f46e5;
  border-radius: 8px;
  font-size: 9px;
  font-weight: 800;
  text-transform: uppercase;
}

.task-title {
  font-size: 20px;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 12px;
  line-height: 1.3;
}

.task-description p {
  color: #334155;
  font-weight: 500;
  line-height: 1.6;
  white-space: pre-wrap;
  font-size: 14px;
}

.loading-task {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  font-weight: 700;
  animation: pulse 2s infinite;
}

.game-controls {
  border-top: 1px solid #e2e8f0;
  background-color: white;
  padding: 16px;
  flex-shrink: 0;
}

.game-logs {
  height: 100px;
  overflow-y: auto;
  padding-right: 8px;
  margin-bottom: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.game-logs::-webkit-scrollbar {
  width: 3px;
}

.game-logs::-webkit-scrollbar-track {
  background: transparent;
}

.game-logs::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 10px;
}

.log-message {
  font-size: 12px;
  font-weight: 500;
}

.log-system {
  color: #4f46e5;
}

.log-error {
  color: #ef4444;
}

.log-user {
  color: #334155;
}

.answer-form {
  display: flex;
  gap: 8px;
}

.answer-input {
  flex: 1;
  background-color: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  padding: 10px 14px;
  font-weight: 700;
  color: #0f172a;
  outline: none;
  transition: border-color 0.2s ease;
  font-size: 14px;
}

.answer-input:focus {
  border-color: #4f46e5;
}

.submit-answer-btn {
  padding: 10px 20px;
  background-color: #4f46e5;
  color: white;
  font-weight: 800;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
  font-size: 14px;
  white-space: nowrap;
}

.submit-answer-btn:hover {
  background-color: #4338ca;
  transform: translateY(-1px);
}

.submit-answer-btn:active {
  transform: translateY(0);
}

/* Состояние результата */
.result-state {
  background-color: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #f1f5f9;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 20px;
  min-height: 280px;
}

.result-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.result-text h1 {
  font-size: 24px;
  font-weight: 800;
  margin-bottom: 8px;
  line-height: 1.2;
}

.text-win {
  color: #16a34a;
}

.text-loss {
  color: #dc2626;
}

.text-disconnect {
  color: #f59e0b;
}

.result-description {
  color: #64748b;
  font-weight: 700;
  font-size: 14px;
  line-height: 1.4;
}

.play-again-btn {
  padding: 12px 24px;
  background-color: #0f172a;
  color: white;
  font-weight: 800;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
  font-size: 14px;
}

.play-again-btn:hover {
  background-color: #1e293b;
  transform: translateY(-2px);
}

.play-again-btn:active {
  transform: translateY(0);
}

/* Сайдбар */
.sidebar-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stats-card {
  background-color: white;
  padding: 20px;
  border-radius: 16px;
  border: 1px solid #f1f5f9;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.stats-title {
  font-size: 18px;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 16px;
}

.stats-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px;
  background-color: #f8fafc;
  border-radius: 12px;
}

.stat-label {
  font-size: 11px;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
}

.stat-value {
  font-weight: 800;
  font-size: 14px;
}

.rank-value {
  color: #4f46e5;
}

.points-value {
  color: #0f172a;
}

.leaderboard-card {
  background-color: white;
  overflow: hidden;
  border-radius: 16px;
  border: 1px solid #f1f5f9;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.leaderboard-header {
  padding: 16px;
  background-color: #0f172a;
  color: white;
  font-weight: 800;
  text-align: center;
  font-size: 14px;
}

.leaderboard-list {
  padding: 8px;
}

.leaderboard-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 12px;
  transition: background-color 0.2s ease;
}

.leaderboard-item:hover {
  background-color: #f8fafc;
}

.player-rank {
  width: 20px;
  font-size: 12px;
  font-weight: 800;
  color: #cbd5e1;
}

.player-avatar {
  width: 36px;
  height: 36px;
  background-color: #f1f5f9;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.player-info {
  flex: 1;
}

.player-name {
  font-size: 13px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 2px;
}

.player-points {
  font-size: 9px;
  font-weight: 800;
  color: #4f46e5;
  text-transform: uppercase;
}

/* Анимации */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* ==================== АДАПТИВНЫЕ СТИЛИ ==================== */


@media (min-width: 321px) and (max-width: 375px) {
  .arena-title {
    font-size: 30px;
  }
  
  .result-icon {
    font-size: 56px;
  }
  
  .result-text h1 {
    font-size: 26px;
  }
}


@media (min-width: 376px) and (max-width: 480px) {
  .pvp-container {
    padding: 20px;
  }
  
  .arena-title {
    font-size: 32px;
  }
  
  .task-title {
    font-size: 22px;
  }
  
  .stats-card,
  .leaderboard-card {
    padding: 24px;
  }
}


@media (min-width: 481px) {
  .pvp-container {
    padding: 24px;
  }
  
  .pvp-grid {
    gap: 24px;
  }
  
  .idle-state,
  .searching-state,
  .result-state {
    border-radius: 20px;
    padding: 32px;
    min-height: 320px;
  }
  
  .arena-title {
    font-size: 36px;
  }
  
  .arena-description {
    font-size: 16px;
  }
  
  .find-opponent-btn {
    padding: 16px 32px;
    font-size: 16px;
  }
  
  .playing-state {
    border-radius: 20px;
    min-height: 550px;
  }
  
  .match-header {
    padding: 20px 24px;
  }
  
  .task-container {
    padding: 24px;
  }
  
  .task-title {
    font-size: 24px;
  }
  
  .task-description p {
    font-size: 15px;
  }
  
  .game-controls {
    padding: 20px;
  }
  
  .game-logs {
    height: 120px;
  }
  
  .answer-form {
    gap: 12px;
  }
  
  .answer-input {
    padding: 12px 16px;
  }
  
  .submit-answer-btn {
    padding: 12px 24px;
  }
  
  .result-icon {
    font-size: 64px;
  }
  
  .result-text h1 {
    font-size: 32px;
  }
  
  .result-description {
    font-size: 16px;
  }
  
  .play-again-btn {
    padding: 14px 28px;
    font-size: 16px;
  }
  
  .sidebar-section {
    gap: 24px;
  }
  
  .stats-card,
  .leaderboard-card {
    border-radius: 20px;
    padding: 24px;
  }
  
  .stats-title {
    font-size: 20px;
  }
  
  .stat-item {
    padding: 16px;
  }
  
  .stat-label {
    font-size: 12px;
  }
  
  .stat-value {
    font-size: 16px;
  }
  
  .leaderboard-header {
    padding: 20px;
    font-size: 16px;
  }
  
  .leaderboard-item {
    padding: 16px;
  }
  
  .player-avatar {
    width: 40px;
    height: 40px;
    font-size: 18px;
  }
  
  .player-name {
    font-size: 14px;
  }
}


@media (min-width: 641px) {
  .pvp-grid {
    grid-template-columns: 2fr 1fr;
  }
  
  .idle-state {
    min-height: 360px;
  }
  
  .arena-title {
    font-size: 40px;
  }
  
  .arena-description {
    font-size: 17px;
  }
  
  .playing-state {
    min-height: 600px;
  }
  
  .task-title {
    font-size: 26px;
  }
  
  .result-icon {
    font-size: 72px;
  }
  
  .result-text h1 {
    font-size: 36px;
  }
}


@media (min-width: 769px) {
  .pvp-container {
    padding: 32px;
  }
  
  .pvp-grid {
    max-width: 1200px;
    gap: 32px;
  }
  
  .idle-state,
  .searching-state,
  .result-state {
    border-radius: 24px;
    padding: 40px;
    min-height: 400px;
  }
  
  .arena-title {
    font-size: 44px;
  }
  
  .arena-badge {
    font-size: 10px;
    padding: 6px 16px;
  }
  
  .playing-state {
    border-radius: 24px;
  }
  
  .match-header {
    padding: 24px 32px;
  }
  
  .live-text {
    font-size: 14px;
  }
  
  .match-hint {
    font-size: 12px;
  }
  
  .task-container {
    padding: 32px;
  }
  
  .task-tags {
    gap: 8px;
  }
  
  .subject-tag,
  .difficulty-tag {
    padding: 6px 12px;
    font-size: 10px;
  }
  
  .task-title {
    font-size: 28px;
  }
  
  .task-description p {
    font-size: 16px;
  }
  
  .game-controls {
    padding: 24px;
  }
  
  .game-logs {
    height: 140px;
  }
  
  .log-message {
    font-size: 14px;
  }
  
  .stats-card,
  .leaderboard-card {
    border-radius: 24px;
    padding: 28px;
  }
  
  .stats-title {
    font-size: 22px;
  }
}


@media (min-width: 1025px) {
  .pvp-container {
    padding: 40px;
  }
  
  .pvp-grid {
    max-width: 1280px;
  }
  
  .idle-state {
    min-height: 420px;
  }
  
  .arena-title {
    font-size: 48px;
  }
  
  .arena-description {
    font-size: 18px;
    max-width: 600px;
  }
  
  .find-opponent-btn {
    padding: 20px 40px;
    font-size: 18px;
  }
  
  .btn-fire {
    font-size: 20px;
  }
  
  .playing-state {
    min-height: 650px;
  }
  
  .task-title {
    font-size: 32px;
  }
  
  .result-icon {
    font-size: 80px;
  }
  
  .result-text h1 {
    font-size: 40px;
  }
  
  .result-description {
    font-size: 18px;
  }
}


@media (min-width: 1281px) {
  .pvp-container {
    padding: 48px;
  }
  
  .pvp-grid {
    max-width: 1400px;
  }
  
  .idle-state {
    min-height: 450px;
  }
  
  .arena-title {
    font-size: 52px;
  }
  
  .stats-card,
  .leaderboard-card {
    padding: 32px;
  }
  
  .stats-title {
    font-size: 24px;
  }
  
  .stat-item {
    padding: 20px;
  }
  
  .stat-value {
    font-size: 18px;
  }
}


@media (min-width: 1537px) {
  .pvp-container {
    padding: 64px;
  }
  
  .pvp-grid {
    max-width: 1600px;
  }
  
  .idle-state {
    min-height: 500px;
  }
  
  .arena-title {
    font-size: 56px;
  }
  
  .arena-description {
    font-size: 20px;
    max-width: 700px;
  }
  
  .playing-state {
    min-height: 700px;
  }
  
  .task-title {
    font-size: 36px;
  }
  
  .task-description p {
    font-size: 18px;
  }
  
  .stats-card,
  .leaderboard-card {
    padding: 36px;
    border-radius: 28px;
  }
  
  .leaderboard-header {
    padding: 24px;
    font-size: 18px;
  }
}
</style>