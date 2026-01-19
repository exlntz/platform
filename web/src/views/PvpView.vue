<script setup>
import { ref, onUnmounted, nextTick } from 'vue'
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
            <span class="btn-fire">🔥</span> Найти противника
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
.pvp-container {
  min-height: 100vh;
  background-color: #f8fafc;
  padding: 48px 24px;
  font-family: sans-serif;
}
.pvp-grid {
  max-width: 1280px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 32px;
}
@media (min-width: 1024px) {
  .pvp-grid {
    grid-template-columns: 2fr 1fr;
  }
}
.main-section {
  display: flex;
  flex-direction: column;
  gap: 32px;
}
.idle-state {
  position: relative;
  overflow: hidden;
  background-color: #0f172a;
  border-radius: 40px;
  padding: 40px;
  height: 384px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  box-shadow: 0 25px 50px -12px rgba(99, 102, 241, 0.2);
}
.idle-state::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 256px;
  height: 256px;
  background-color: rgba(79, 70, 229, 0.2);
  border-radius: 50%;
  filter: blur(48px);
  transform: translate(50%, -50%);
  transition: opacity 0.7s ease;
}
.idle-state:hover::before {
  opacity: 1;
}
.arena-badge {
  display: inline-block;
  padding: 4px 16px;
  background-color: rgba(79, 70, 229, 0.2);
  color: rgba(199, 210, 254, 0.8);
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  border-radius: 9999px;
  border: 1px solid rgba(79, 70, 229, 0.3);
  margin-bottom: 24px;
}
.arena-title {
  font-size: 48px;
  font-weight: 900;
  color: white;
  letter-spacing: -0.025em;
  margin-bottom: 16px;
}
.arena-description {
  color: #a5b4fc;
  max-width: 512px;
  font-weight: 500;
  font-size: 18px;
  line-height: 1.75;
  margin-bottom: 32px;
}
.find-opponent-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 40px;
  background-color: #22c55e;
  color: white;
  font-weight: 900;
  border-radius: 16px;
  border: none;
  cursor: pointer;
  box-shadow: 0 10px 15px -3px rgba(34, 197, 94, 0.1);
  transition: all 0.2s ease;
  font-size: 18px;
  position: relative;
  z-index: 10;
}
.find-opponent-btn:hover {
  background-color: #16a34a;
  transform: scale(1.05);
}
.find-opponent-btn:active {
  transform: scale(0.95);
}
.btn-fire {
  font-size: 20px;
}
.searching-state {
  background-color: white;
  border-radius: 40px;
  padding: 40px;
  height: 384px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 24px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  border: 1px solid #f1f5f9;
}
.searching-spinner {
  position: relative;
  width: 80px;
  height: 80px;
}
.spinner-ring {
  width: 100%;
  height: 100%;
  border: 4px solid #e0e7ff;
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
  font-size: 24px;
}
.searching-text h2 {
  font-size: 24px;
  font-weight: 900;
  color: #0f172a;
  margin-bottom: 8px;
}
.searching-text p {
  color: #64748b;
  font-weight: 500;
}
.cancel-btn {
  font-size: 14px;
  font-weight: 700;
  color: #ef4444;
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s ease;
}
.cancel-btn:hover {
  color: #dc2626;
}
.playing-state {
  background-color: white;
  border-radius: 40px;
  border: 1px solid #f1f5f9;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 600px;
}
.match-header {
  background-color: #0f172a;
  padding: 24px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
}
.match-status {
  display: flex;
  align-items: center;
  gap: 12px;
}
.live-dot {
  width: 12px;
  height: 12px;
  background-color: #ef4444;
  border-radius: 50%;
  animation: pulse 2s infinite;
}
.live-text {
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-size: 14px;
}
.match-hint {
  font-size: 12px;
  font-weight: 700;
  color: #a5b4fc;
}
.task-container {
  flex: 1;
  overflow-y: auto;
  padding: 32px;
  background-color: #f8fafc;
}
.task-content {
  max-width: 768px;
  margin: 0 auto;
}
.task-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}
.subject-tag {
  padding: 6px 12px;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
  color: #475569;
}
.difficulty-tag {
  padding: 6px 12px;
  background-color: #e0e7ff;
  border: 1px solid #c7d2fe;
  color: #4f46e5;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
}
.task-title {
  font-size: 24px;
  font-weight: 900;
  color: #0f172a;
  margin-bottom: 16px;
}
.task-description p {
  color: #334155;
  font-weight: 500;
  line-height: 1.75;
  white-space: pre-wrap;
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
  padding: 24px;
}
.game-logs {
  height: 128px;
  overflow-y: auto;
  padding-right: 8px;
  margin-bottom: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.game-logs::-webkit-scrollbar {
  width: 4px;
}
.game-logs::-webkit-scrollbar-track {
  background: transparent;
}
.game-logs::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 20px;
}
.log-message {
  font-size: 14px;
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
  gap: 12px;
}
.answer-input {
  flex: 1;
  background-color: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 12px 16px;
  font-weight: 700;
  color: #0f172a;
  outline: none;
  transition: border-color 0.2s ease;
}
.answer-input:focus {
  border-color: #4f46e5;
}
.submit-answer-btn {
  padding: 12px 24px;
  background-color: #4f46e5;
  color: white;
  font-weight: 900;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}
.submit-answer-btn:hover {
  background-color: #4338ca;
}
.submit-answer-btn:active {
  transform: scale(0.95);
}
.result-state {
  background-color: white;
  border-radius: 40px;
  padding: 40px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  border: 1px solid #f1f5f9;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 24px;
  height: 384px;
}
.result-icon {
  font-size: 72px;
  margin-bottom: 16px;
}
.result-text h1 {
  font-size: 36px;
  font-weight: 900;
  margin-bottom: 8px;
}
.text-win {
  color: #16a34a;
}
.text-loss {
  color: #dc2626;
}
.result-description {
  color: #64748b;
  font-weight: 700;
  font-size: 18px;
}
.play-again-btn {
  padding: 16px 32px;
  background-color: #0f172a;
  color: white;
  font-weight: 900;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}
.play-again-btn:hover {
  background-color: #1e293b;
}
.sidebar-section {
  display: flex;
  flex-direction: column;
  gap: 32px;
}
.stats-card {
  background-color: white;
  padding: 32px;
  border-radius: 40px;
  border: 1px solid #f1f5f9;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}
.stats-title {
  font-size: 20px;
  font-weight: 900;
  color: #0f172a;
  margin-bottom: 24px;
}
.stats-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background-color: #f8fafc;
  border-radius: 16px;
}
.stat-label {
  font-size: 12px;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
}
.stat-value {
  font-weight: 900;
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
  border-radius: 40px;
  border: 1px solid #f1f5f9;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}
.leaderboard-header {
  padding: 24px;
  background-color: #0f172a;
  color: white;
  font-weight: 900;
  text-align: center;
}
.leaderboard-list {
  padding: 8px;
}
.leaderboard-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-radius: 16px;
  transition: background-color 0.2s ease;
}
.leaderboard-item:hover {
  background-color: #f8fafc;
}
.player-rank {
  width: 24px;
  font-size: 14px;
  font-weight: 900;
  color: #cbd5e1;
}
.player-avatar {
  width: 40px;
  height: 40px;
  background-color: #f1f5f9;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}
.player-info {
  flex: 1;
}
.player-name {
  font-size: 14px;
  font-weight: 700;
  color: #1f2937;
}
.player-points {
  font-size: 10px;
  font-weight: 900;
  color: #4f46e5;
  text-transform: uppercase;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
