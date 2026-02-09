<script setup>
import { ref, onUnmounted, nextTick, computed, onMounted, watch } from 'vue'
import api from '@/api/axios'
import { useRouter } from 'vue-router'
import { useNotificationStore } from '@/pinia/NotificationStore'
const notify = useNotificationStore()
const router = useRouter()

// --- КОНСТАНТЫ ВИЗУАЛА ---
const RANK_VISUALS = {
  LEGEND: { emoji: '🐲', color: 'from-purple-500 to-pink-500' },
  SENSEI: { emoji: '🥋', color: 'from-red-500 to-orange-500' },
  ELITE: { emoji: '⚔️', color: 'from-blue-500 to-cyan-500' },
  GOLD: { emoji: '🥇', color: 'from-yellow-400 to-yellow-600' },
  SILVER: { emoji: '🥈', color: 'from-slate-300 to-slate-400' },
  BRONZE: { emoji: '🥉', color: 'from-amber-700 to-amber-900' },
}

// --- СОСТОЯНИЕ ---
const ELO_RANKS = ref([])
const socket = ref(null)
const gameState = ref('idle')
const gameResult = ref(null)
const activeTask = ref(null)
const userAnswer = ref('')
const logs = ref([])
const logContainer = ref(null)

// --- СЧЕТ МАТЧА ---
const myScore = ref(0)
const opponentScore = ref(0)

const availableEmojis = ['😎', '🔥', '😱', '🤔', '😭', '😂']
const showEmojiPicker = ref(false)
const floatingEmojis = ref([])

// --- ТАЙМЕР МЕЖДУ ЗАДАЧАМИ ---
const isNextTaskTimerActive = ref(false)
const nextTaskTimer = ref(3)
let taskTimerInterval = null

// --- ТАЙМЕР РЕКОННЕКТА ---
let reconnectButtonTimer = null
const RECONNECT_WINDOW_MS = 5000

// --- СТАТИСТИКА И ИСТОРИЯ ---
const stats = ref({ rank: 'Loading...', points: 0, username: '' })
const matchHistory = ref([])
const isHistoryLoading = ref(true)

// --- MODAL STATE ---
const showRankModal = ref(false)
const openRankModal = () => (showRankModal.value = true)
const closeRankModal = () => (showRankModal.value = false)

// --- ЛОГИКА СОХРАНЕНИЯ СЧЕТА (LOCAL STORAGE) ---
const saveScoreState = () => {
  const scoreData = {
    me: myScore.value,
    opp: opponentScore.value,
  }
  localStorage.setItem('pvp_score_state', JSON.stringify(scoreData))
}

const restoreScoreState = () => {
  const saved = localStorage.getItem('pvp_score_state')
  if (saved) {
    try {
      const parsed = JSON.parse(saved)
      myScore.value = parsed.me || 0
      opponentScore.value = parsed.opp || 0
    } catch (e) {
      console.error('Ошибка восстановления счета', e)
    }
  }
}

const clearScoreState = () => {
  localStorage.removeItem('pvp_score_state')
  myScore.value = 0
  opponentScore.value = 0
}

// Следим за изменениями счета и сохраняем
watch([myScore, opponentScore], () => {
  if (gameState.value === 'playing') {
    saveScoreState()
  }
})

// --- ВЫЧИСЛЕНИЯ ДЛЯ РАНГОВ ---
const currentRankObj = computed(() => {
  if (ELO_RANKS.value.length === 0) {
    return { name: '...', min_elo: 0, emoji: '⏳', label: 'Loading...', color: 'from-gray-500' }
  }
  const points = stats.value.points || 0
  const sortedRanks = [...ELO_RANKS.value].sort((a, b) => a.min_elo - b.min_elo)
  return (
    sortedRanks.reverse().find((r) => r.min_elo <= points) || sortedRanks[sortedRanks.length - 1]
  )
})

const nextRankObj = computed(() => {
  if (ELO_RANKS.value.length === 0) return null
  const points = stats.value.points || 0
  const sorted = [...ELO_RANKS.value].sort((a, b) => a.min_elo - b.min_elo)
  return sorted.find((r) => r.min_elo > points) || null
})

const progressToNextRank = computed(() => {
  if (ELO_RANKS.value.length === 0) return 0
  if (!nextRankObj.value) return 100
  const current = stats.value.points || 0
  const prevLimit = currentRankObj.value.min_elo
  const nextLimit = nextRankObj.value.min_elo
  const totalDiff = nextLimit - prevLimit
  const currentDiff = current - prevLimit
  let percent = (currentDiff / totalDiff) * 100
  return Math.min(Math.max(percent, 0), 100).toFixed(1)
})

const sendEmoji = (emojiChar) => {
  if (!socket.value) return
  socket.value.send(`SendEmoji ${emojiChar}`)
  triggerFloatingEmoji(emojiChar, 'me')
  showEmojiPicker.value = false
}

const triggerFloatingEmoji = (char, source) => {
  const id = Date.now() + Math.random()
  floatingEmojis.value.push({ id, char, source })
  setTimeout(() => {
    floatingEmojis.value = floatingEmojis.value.filter((e) => e.id !== id)
  }, 2000)
}

const resultTitle = computed(() => {
  switch (gameResult.value) {
    case 'win':
      return 'Победа! 🎉'
    case 'loss':
      return 'Поражение 😔'
    case 'disconnect':
      return 'Обрыв соединения 😔'
    case 'draw':
      return 'Ничья'
    case 'already_in_match':
      return 'Матч уже идёт'
    default:
      return ''
  }
})

const resultDescription = computed(() => {
  switch (gameResult.value) {
    case 'win':
      return 'Ты решил задачу быстрее соперника!'
    case 'loss':
      return 'Соперник был быстрее. Не сдавайся!'
    case 'disconnect':
      return 'Игра не будет засчитана'
    case 'draw':
      return 'Силы оказались равны'
    case 'already_in_match':
      return 'Матч уже идёт'
    default:
      return ''
  }
})

const resultTitleClass = computed(() => {
  return {
    'text-win': gameResult.value === 'win',
    'text-loss': gameResult.value === 'loss',
    'text-disconnect': gameResult.value === 'disconnect',
    'text-draw': gameResult.value === 'draw',
    'text-already_in_match': gameResult.value === 'already_in_match',
  }
})

// --- ЗАГРУЗКА ДАННЫХ ---
const loadUserData = async () => {
  try {
    if (ELO_RANKS.value.length === 0) {
      const ranksRes = await api.get('/pvp/ranks_info')
      ELO_RANKS.value = ranksRes.data.map((rank) => ({
        ...rank,
        label: rank.name,
        emoji: RANK_VISUALS[rank.name]?.emoji || '🏆',
        color: RANK_VISUALS[rank.name]?.color || 'from-gray-500 to-gray-700',
      }))
    }
    const profileRes = await api.get('/profile/')
    stats.value = {
      rank: profileRes.data.rank,
      points: profileRes.data.rating,
      username: profileRes.data.username,
    }
    await loadHistory()
  } catch (e) {
    console.error('Ошибка загрузки данных:', e)
  }
}

const loadHistory = async () => {
  isHistoryLoading.value = true
  try {
    const historyRes = await api.get('/pvp/matches_history', { params: { limit: 10 } })
    matchHistory.value = historyRes.data
  } catch (e) {
    console.error('Ошибка истории:', e)
  } finally {
    isHistoryLoading.value = false
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('ru-RU', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const formatEloRaw = (change) => {
  const val = parseFloat(change)
  if (val > 0) return `+${val}`
  return `${val}`
}

const getResultIcon = (resultStr) => {
  if (resultStr === 'Победа') return '🏆'
  if (resultStr === 'Проигрыш') return '💀'
  if (resultStr === 'Ничья') return '🤝'
  if (resultStr === 'Матч отменен') return '🚫'
  return '❓'
}

const getResultClass = (resultStr) => {
  if (resultStr === 'Победа') return 'res-text-win'
  if (resultStr === 'Проигрыш') return 'res-text-loss'
  if (resultStr === 'Ничья') return 'res-text-draw'
  return 'res-text-neutral'
}

// --- ТАЙМЕР МЕЖДУ РАУНДАМИ ---
const startNextTaskTimer = () => {
  isNextTaskTimerActive.value = true
  nextTaskTimer.value = 3

  if (taskTimerInterval) clearInterval(taskTimerInterval)

  taskTimerInterval = setInterval(() => {
    nextTaskTimer.value--
    if (nextTaskTimer.value <= 0) {
      clearInterval(taskTimerInterval)
      isNextTaskTimerActive.value = false
    }
  }, 1000)
}

// --- НАВИГАЦИЯ ПОСЛЕ МАТЧА ---
const goToTasks = () => {
  router.push('/tasks')
}

const goBackToLobby = () => {
  disconnect()
  isReconnecting.value = false
  gameState.value = 'idle'
}

// --- WEBSOCKET ---
const isReconnecting = ref(false)

const connectPvp = () => {
  const token = localStorage.getItem('user-token')
  if (!token) {
    notify.show('Сначала войдите!')
    router.push('/auth')
    return
  }

  if (reconnectButtonTimer) clearTimeout(reconnectButtonTimer)

  if (!isReconnecting.value) {
    // НОВАЯ ИГРА - СБРОС ВСЕГО
    gameState.value = 'searching'
    gameResult.value = null
    activeTask.value = null
    logs.value = []
    userAnswer.value = ''
    isNextTaskTimerActive.value = false
    clearScoreState() // Очищаем старый счет
  } else {
    // РЕКОННЕКТ
    gameState.value = 'playing'
    addLog('system', 'Восстановление соединения...')
    restoreScoreState() // Восстанавливаем счет из памяти
  }

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  socket.value = new WebSocket(`${protocol}//${window.location.host}/api/pvp/join`)

  socket.value.onopen = () => {
    if (!isReconnecting.value) addLog('system', 'Соединение установлено...')
  }

  socket.value.onmessage = async (event) => {
    const msg = event.data
    console.log('WS Message:', msg)

    if (msg === 'Connected') {
      const currentToken = localStorage.getItem('user-token')
      socket.value.send(currentToken)
    } else if (msg === 'token accepted') {
      if (!isReconnecting.value) {
        addLog('system', 'Авторизация успешна. Ищем противника...')
      } else {
        addLog('system', 'Вы переподключились к матчу!')
      }
    } else if (msg === 'invalid token') {
      socket.value.close()
      if (isReconnecting.value) {
        router.push('/auth')
        return
      }
      isReconnecting.value = true
      try {
        await api.get('/profile/')
        connectPvp()
      } catch (e) {
        router.push('/auth')
      }
    } else if (msg === 'Search started') {
    } else if (msg === 'match started') {
      gameState.value = 'playing'
      if (!isReconnecting.value) {
        addLog('system', 'Матч начался! Ждем задачу...')
      }
    } else if (msg === 'нет задач') {
      notify.show('Нет задач!')
      disconnect()
    } else if (!isNaN(parseInt(msg)) && msg.length < 10) {
      await loadTask(msg)
    } else if (msg.includes('time is up')) {
      addLog('error', 'Время вышло. Следующая задача...')
      startNextTaskTimer()
    } else if (msg.includes('other player answered')) {
      addLog('error', 'Оппонент ответил верно. Следующая задача...')
      opponentScore.value++
      startNextTaskTimer()
    } else if (msg.includes('incorrect')) {
      addLog('error', 'Неверно! Попробуй еще раз.')
    } else if (msg.includes('chat message')) {
      addLog('chat', msg.substr(12))
    } else if (msg.includes('please wait')) {
      addLog('error', 'Ожидание следующего раунда...')
    } else if (msg.includes('correct')) {
      addLog('system', 'Верно!')
      myScore.value++
      startNextTaskTimer()
    } else if (msg.includes('win')) {
      finishGame('win')
      loadUserData()
      isReconnecting.value = false
    } else if (msg.includes('loss')) {
      finishGame('loss')
      loadUserData()
      isReconnecting.value = false
    } else if (msg === 'opponent disconnected') {
      finishGame('disconnect')
      loadUserData()
      isReconnecting.value = false
    } else if (msg.includes('draw')) {
      finishGame('draw')
      loadUserData()
      isReconnecting.value = false
    } else if (msg.includes('already in a match')) {
      gameState.value = 'playing'
      isReconnecting.value = true
      addLog('system', 'Вы вернулись в игру!')
      restoreScoreState() // Попытка восстановить счет
    } else if (msg.includes('emoji ')) {
      const emojiChar = msg.split(' ')[1]
      triggerFloatingEmoji(emojiChar, 'opponent')
    }
  }

  socket.value.onclose = () => {
    if (gameState.value === 'searching' || gameState.value === 'playing') {
      isReconnecting.value = true
      gameState.value = 'idle'
      startReconnectExpirationTimer(RECONNECT_WINDOW_MS)
    }
  }

  socket.value.onerror = (e) => {
    console.error('WebSocket error:', e)
    addLog('error', 'Ошибка соединения')
    isReconnecting.value = true
    gameState.value = 'idle'
    startReconnectExpirationTimer(RECONNECT_WINDOW_MS)
  }
}

const startReconnectExpirationTimer = (duration) => {
  if (reconnectButtonTimer) clearTimeout(reconnectButtonTimer)

  reconnectButtonTimer = setTimeout(() => {
    if (gameState.value === 'idle' && isReconnecting.value) {
      isReconnecting.value = false
      clearScoreState() // Время вышло, сбрасываем счет
      localStorage.removeItem('pvp_reconnect')
      localStorage.removeItem('pvp_disconnect_time')
    }
  }, duration)
}

const sendAnswer = () => {
  if (!userAnswer.value.trim() || !socket.value) return
  socket.value.send(userAnswer.value)
  addLog('user', userAnswer.value)
  userAnswer.value = ''
}

const loadTask = async (taskId) => {
  try {
    const token = localStorage.getItem('user-token')
    const response = await api.get(`/tasks/${taskId}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    activeTask.value = response.data
    addLog('system', 'Задача получена!')
  } catch (e) {
    console.error(e)
    addLog('error', 'Ошибка загрузки задачи')
  }
}

const finishGame = (result) => {
  gameResult.value = result
  gameState.value = 'result'
  if (taskTimerInterval) clearInterval(taskTimerInterval)
  isNextTaskTimerActive.value = false
  if (socket.value) socket.value.close()

  localStorage.removeItem('pvp_reconnect')
  localStorage.removeItem('pvp_disconnect_time')
  clearScoreState() // Очищаем счет при завершении
}

const disconnect = () => {
  if (socket.value) socket.value.close()
  gameState.value = 'idle'
  isReconnecting.value = false
  clearScoreState()
  localStorage.removeItem('pvp_reconnect')
  localStorage.removeItem('pvp_disconnect_time')
}

const addLog = (type, text) => {
  logs.value.push({ type, text, id: Date.now() })
  nextTick(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = logContainer.value.scrollHeight
    }
  })
}

onMounted(() => {
  loadUserData()

  const wasInMatch = localStorage.getItem('pvp_reconnect') === 'true'
  const disconnectTime = parseInt(localStorage.getItem('pvp_disconnect_time') || '0')
  const now = Date.now()

  if (wasInMatch && now - disconnectTime < RECONNECT_WINDOW_MS) {
    isReconnecting.value = true
    restoreScoreState() // Восстанавливаем счет при рефреше

    const remainingTime = RECONNECT_WINDOW_MS - (now - disconnectTime)
    startReconnectExpirationTimer(remainingTime)
  } else {
    localStorage.removeItem('pvp_reconnect')
    localStorage.removeItem('pvp_disconnect_time')
    clearScoreState()
    isReconnecting.value = false
  }
})

window.addEventListener('beforeunload', () => {
  if (gameState.value === 'playing' || gameState.value === 'searching') {
    localStorage.setItem('pvp_reconnect', 'true')
    localStorage.setItem('pvp_disconnect_time', Date.now().toString())
    saveScoreState() // Сохраняем счет перед уходом
  } else {
    localStorage.removeItem('pvp_reconnect')
    localStorage.removeItem('pvp_disconnect_time')
    clearScoreState()
  }
})

onUnmounted(() => {
  if (socket.value) socket.value.close()
  if (taskTimerInterval) clearInterval(taskTimerInterval)
  if (reconnectButtonTimer) clearTimeout(reconnectButtonTimer)
  window.removeEventListener('beforeunload', () => {})
})
</script>

<template>
  <div class="pvp-container">
    <div class="pvp-grid">
      <div class="main-section">
        <div v-if="gameState === 'idle'" class="idle-state">
          <div class="idle-content">
            <div class="arena-badge">PvP Arena</div>
            <h1 class="arena-title">Готов к битве?</h1>
            <p class="arena-description">
              Сразись с реальным противником. Кто первый решит задачу — забирает рейтинг.
            </p>

            <button
              @click="connectPvp"
              class="find-opponent-btn"
              :class="{ 'reconnect-btn': isReconnecting }"
            >
              {{ isReconnecting ? 'Переподключиться к матчу' : 'Найти противника' }}
            </button>
          </div>
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

            <div class="match-score">
              <span class="score-me">{{ myScore }}</span>
              <span class="score-divider">:</span>
              <span class="score-opp">{{ opponentScore }}</span>
            </div>

            <div class="match-hint">Решай быстрее!</div>
          </div>

          <div class="task-container">
            <div v-if="isNextTaskTimerActive" class="next-task-overlay">
              <div class="timer-count">{{ nextTaskTimer }}</div>
              <div class="timer-text">Следующий раунд...</div>
            </div>

            <div v-else-if="activeTask" class="task-content">
              <div class="task-tags">
                <span class="subject-tag">{{ activeTask.subject }}</span>
                <span class="difficulty-tag">{{ activeTask.difficulty }}</span>
              </div>
              <h2 class="task-title">{{ activeTask.title }}</h2>
              <div class="task-description">
                <p>{{ activeTask.description }}</p>
              </div>
            </div>
            <div v-else class="loading-task">Ожидание задачи...</div>
          </div>

          <div class="game-controls">
            <div class="emoji-layer">
              <div
                v-for="e in floatingEmojis"
                :key="e.id"
                class="floating-emoji"
                :class="{ 'from-me': e.source === 'me', 'from-opponent': e.source === 'opponent' }"
              >
                {{ e.char }}
              </div>
            </div>

            <div class="input-area">
              <button
                @click="showEmojiPicker = !showEmojiPicker"
                class="emoji-btn"
                :disabled="isNextTaskTimerActive"
              >
                😀
              </button>

              <div v-if="showEmojiPicker" class="emoji-picker">
                <button
                  v-for="emoji in ['😎', '🔥', '😱', '🤔', '😭', '😂']"
                  :key="emoji"
                  @click="sendEmoji(emoji)"
                  class="emoji-option"
                >
                  {{ emoji }}
                </button>
              </div>
            </div>
            <div ref="logContainer" class="game-logs">
              <div v-for="log in logs" :key="log.id" class="log-message">
                <span v-if="log.type === 'system'" class="log-system">🤖 {{ log.text }}</span>
                <span v-else-if="log.type === 'error'" class="log-error">❌ {{ log.text }}</span>
                <span v-else-if="log.type === 'chat'" class="log-user"
                  >👤 Оппонент: {{ log.text }}</span
                >
                <span v-else class="log-user">👤 Вы: {{ log.text }}</span>
              </div>
            </div>
            <form @submit.prevent="sendAnswer" class="answer-form">
              <input
                v-model="userAnswer"
                placeholder="Введите ответ..."
                class="answer-input"
                autoFocus
                :disabled="isNextTaskTimerActive"
              />
              <button type="submit" class="submit-answer-btn" :disabled="isNextTaskTimerActive">
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
            <h1 :class="resultTitleClass">{{ resultTitle }}</h1>
            <p class="result-description">{{ resultDescription }}</p>
          </div>

          <div class="result-actions">
            <button @click="connectPvp" class="play-again-btn">Играть снова</button>
            <div class="result-secondary-actions">
              <button @click="goToTasks" class="secondary-btn">Решать задачи</button>
              <button @click="goBackToLobby" class="secondary-btn">Вернуться назад</button>
            </div>
          </div>
        </div>
      </div>

      <div class="sidebar-section">
        <div class="rank-card-vertical" @click="openRankModal">
          <div class="rank-card-header">
            <span class="rank-label">ТЕКУЩИЙ РАНГ</span>
            <span class="rank-info-icon">ℹ️</span>
          </div>

          <div class="rank-icon-large floating-anim">{{ currentRankObj.emoji }}</div>
          <div class="rank-name-large">{{ currentRankObj.label }}</div>
          <div class="rank-elo-large">{{ Math.round(stats.points) }} ELO</div>

          <div class="rank-progress-container">
            <div class="rank-progress-bar">
              <div class="rank-progress-fill" :style="{ width: progressToNextRank + '%' }"></div>
            </div>
            <div class="rank-progress-text" v-if="nextRankObj">
              До {{ nextRankObj.label }}: {{ Math.round(nextRankObj.min_elo - stats.points) }} очков
            </div>
            <div class="rank-progress-text" v-else>Максимальный ранг!</div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="gameState === 'idle'" class="history-full-container">
      <h3 class="history-full-title">История матчей</h3>
      <div v-if="isHistoryLoading" class="loading-history">Загрузка истории...</div>
      <div v-else-if="matchHistory.length === 0" class="loading-history">
        Матчей пока не найдено
      </div>
      <div v-else class="history-full-list">
        <div v-for="match in matchHistory" :key="match.id" class="history-full-item">
          <div class="history-players">
            <span class="player-me">{{ match.current_player }}</span>
            <span class="vs-badge">vs</span>
            <span class="player-opp">{{ match.opponent }}</span>
          </div>

          <div class="history-result-text" :class="getResultClass(match.result)">
            {{ match.result }}
            <span class="result-icon-small">{{ getResultIcon(match.result) }}</span>
          </div>

          <div class="history-meta">
            <span
              class="history-elo-raw"
              :class="match.current_player_elo_change > 0 ? 'elo-plus' : 'elo-minus'"
            >
              {{ formatEloRaw(match.current_player_elo_change) }} ELO
            </span>
            <span class="history-date-full">{{ formatDate(match.created_at) }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showRankModal" class="rank-modal-overlay" @click.self="closeRankModal">
      <div class="rank-modal-content">
        <button class="rank-modal-close" @click="closeRankModal">✕</button>
        <div class="rank-modal-header">
          <h2>🏆 Путь к Славе</h2>
          <p>Побеждай в дуэлях, поднимай рейтинг и получай новые звания!</p>
        </div>

        <div class="rank-road">
          <div
            v-for="(rank, index) in [...ELO_RANKS].sort((a, b) => b.min_elo - a.min_elo)"
            :key="rank.name"
            class="rank-road-item"
            :class="{ 'current-user-rank': rank.name === currentRankObj.name }"
          >
            <div class="rank-road-left">
              <div class="rank-road-icon">{{ rank.emoji }}</div>
            </div>
            <div class="rank-road-center">
              <div class="rank-road-line" v-if="index !== ELO_RANKS.length - 1"></div>
              <div
                class="rank-road-dot"
                :class="stats.points >= rank.min_elo ? 'dot-active' : ''"
              ></div>
            </div>
            <div class="rank-road-right">
              <div class="rank-road-card">
                <div class="rank-road-title">{{ rank.label }}</div>
                <div class="rank-road-elo">{{ rank.min_elo }}+ ELO</div>
                <div v-if="rank.name === currentRankObj.name" class="current-badge">ТЫ ЗДЕСЬ</div>
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

/* СТИЛИ КНОПКИ РЕКОННЕКТА */
.reconnect-btn {
  background-color: #ef4444 !important;
  box-shadow: 0 6px 12px -3px rgba(239, 68, 68, 0.3) !important;
  animation: pulse-red 2s infinite;
}

@keyframes pulse-red {
  0% {
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(239, 68, 68, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
  }
}

/* СТИЛИ СЧЕТА */
.match-score {
  font-size: 20px;
  font-weight: 800;
  color: #4f46e5;
  background-color: white;
  padding: 4px 12px;
  border-radius: 8px;
  display: flex;
  gap: 8px;
  align-items: center;
}

.score-divider {
  color: #94a3b8;
}

.score-me {
  color: #22c55e;
}

.score-opp {
  color: #ef4444;
}

:root.dark .match-score {
  background-color: #1e293b;
  color: #818cf8;
}

/* СТИЛИ КНОПОК ПОСЛЕ МАТЧА */
.result-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
  max-width: 400px;
}

.result-secondary-actions {
  display: flex;
  gap: 12px;
  width: 100%;
}

.secondary-btn {
  flex: 1;
  padding: 12px;
  background-color: white;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  color: #475569;
  font-weight: 700;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s ease;
}

.secondary-btn:hover {
  border-color: #cbd5e1;
  background-color: #f8fafc;
  color: #0f172a;
}

:root.dark .secondary-btn {
  background-color: #1e293b;
  border-color: #334155;
  color: #94a3b8;
}

:root.dark .secondary-btn:hover {
  background-color: #334155;
  color: #f1f5f9;
}

/* СТИЛИ ДЛЯ ТАЙМЕРА СЛЕДУЮЩЕГО РАУНДА */
.next-task-overlay {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.3s ease;
}

.timer-count {
  font-size: 80px;
  font-weight: 900;
  color: #4f46e5;
  line-height: 1;
  animation: pulse 1s infinite;
}

.timer-text {
  font-size: 18px;
  color: #64748b;
  font-weight: 700;
  margin-top: 12px;
}

:root.dark .timer-count {
  color: #818cf8;
}

:root.dark .timer-text {
  color: #94a3b8;
}

/* ОТКЛЮЧЕННЫЕ КНОПКИ */
.answer-input:disabled,
.submit-answer-btn:disabled,
.emoji-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  filter: grayscale(1);
}

.input-area {
  display: flex;
  gap: 8px;
  position: relative;
  align-items: center;
}

.emoji-btn {
  margin-bottom: 12px;
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  transition: transform 0.2s;
  padding: 0 8px;
}

.emoji-btn:hover {
  transform: scale(1.1);
}

.emoji-picker {
  position: absolute;
  bottom: 100%;
  left: 0;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 8px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 8px;
  z-index: 20;
}

.emoji-option {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
}

.emoji-option:hover {
  background-color: #f1f5f9;
}

/* === АНИМАЦИЯ ЛЕТАЮЩИХ ЭМОДЗИ === */
.emoji-layer {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 50;
}

.floating-emoji {
  position: absolute;
  font-size: 48px;
  bottom: 80px;
  animation: floatUp 2s ease-out forwards;
}

.from-me {
  right: 20px;
}

.from-opponent {
  left: 20px;
}

@keyframes floatUp {
  0% {
    transform: translateY(0) scale(0.5);
    opacity: 0;
  }
  10% {
    transform: translateY(-20px) scale(1.2);
    opacity: 1;
  }
  100% {
    transform: translateY(-200px) scale(1);
    opacity: 0;
  }
}

/* Dark mode fixes for emoji */
:root.dark .emoji-picker {
  background-color: #1e293b;
  border-color: #334155;
}
:root.dark .emoji-option:hover {
  background-color: #334155;
}

/* === MAIN LAYOUT === */
.pvp-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #f0f9ff 100%);
  padding: 16px;
  font-family:
    -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
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

/* Состояние ожидания (IDLE) */
.idle-state {
  position: relative;
  overflow: hidden;
  background-color: #0f172a;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  min-height: 280px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

/* Idle content inside */
.idle-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
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

/* RANK CARD (Now in Sidebar) */
.rank-card-vertical {
  width: 100%;
  background: white; /* Light theme bg */
  border: 1px solid #f1f5f9;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

:root.dark .rank-card-vertical {
  background: #1e293b;
  border-color: #334155;
}

.rank-card-vertical:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.rank-card-header {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.rank-label {
  font-size: 10px;
  font-weight: 800;
  color: #64748b;
  letter-spacing: 0.1em;
}

:root.dark .rank-label {
  color: #94a3b8;
}

.rank-info-icon {
  font-size: 14px;
  opacity: 0.7;
}

.rank-icon-large {
  font-size: 64px;
  margin-bottom: 8px;
  filter: drop-shadow(0 4px 10px rgba(0, 0, 0, 0.1));
}

.floating-anim {
  animation: floatRank 3s ease-in-out infinite;
}

@keyframes floatRank {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-6px);
  }
}

.rank-name-large {
  font-size: 20px;
  font-weight: 900;
  color: #0f172a;
  text-transform: uppercase;
  margin-bottom: 4px;
  letter-spacing: 0.05em;
}

:root.dark .rank-name-large {
  color: white;
}

.rank-elo-large {
  font-size: 14px;
  font-weight: 700;
  color: #4f46e5;
  margin-bottom: 16px;
}

:root.dark .rank-elo-large {
  color: #fbbf24;
}

.rank-progress-container {
  width: 100%;
}

.rank-progress-bar {
  width: 100%;
  height: 8px;
  background-color: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

:root.dark .rank-progress-bar {
  background-color: rgba(255, 255, 255, 0.1);
}

.rank-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4f46e5, #ec4899);
  border-radius: 4px;
  transition: width 0.5s ease-out;
}

.rank-progress-text {
  font-size: 11px;
  color: #64748b;
  font-weight: 600;
}

:root.dark .rank-progress-text {
  color: #94a3b8;
}

/* === MODAL RANK SYSTEM === */
.rank-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(15, 23, 42, 0.9);
  backdrop-filter: blur(8px);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  animation: fadeIn 0.2s ease-out;
}

.rank-modal-content {
  background-color: #ffffff;
  width: 100%;
  max-width: 500px;
  max-height: 80vh;
  border-radius: 24px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

:root.dark .rank-modal-content {
  background-color: #1e293b;
  border: 1px solid #334155;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.rank-modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  background: rgba(0, 0, 0, 0.05);
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  color: #0f172a;
  cursor: pointer;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

:root.dark .rank-modal-close {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.rank-modal-close:hover {
  background: rgba(0, 0, 0, 0.1);
}

:root.dark .rank-modal-close:hover {
  background: rgba(255, 255, 255, 0.2);
}

.rank-modal-header {
  padding: 24px;
  text-align: center;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
}

:root.dark .rank-modal-header {
  border-bottom: 1px solid #334155;
  background: #0f172a;
}

.rank-modal-header h2 {
  font-size: 24px;
  color: #0f172a;
  margin-bottom: 8px;
  font-weight: 800;
}

:root.dark .rank-modal-header h2 {
  color: white;
}

.rank-modal-header p {
  color: #64748b;
  font-size: 14px;
  line-height: 1.4;
}

:root.dark .rank-modal-header p {
  color: #94a3b8;
}

.rank-road {
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

/* Стиль элемента пути славы */
.rank-road-item {
  display: flex;
  height: 80px; /* Фиксированная высота шага */
}

.rank-road-left {
  width: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.rank-road-icon {
  font-size: 32px;
}

.rank-road-center {
  width: 40px;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.rank-road-line {
  position: absolute;
  top: 50%;
  bottom: -50%; /* Линия идет вниз */
  width: 4px;
  background-color: #e2e8f0;
  z-index: 1;
}

:root.dark .rank-road-line {
  background-color: #334155;
}

.rank-road-item:last-child .rank-road-line {
  display: none; /* У последнего элемента нет линии вниз */
}

.rank-road-dot {
  width: 16px;
  height: 16px;
  background-color: #e2e8f0;
  border: 4px solid #ffffff;
  border-radius: 50%;
  z-index: 2;
  margin-top: auto;
  margin-bottom: auto;
  transition: all 0.3s ease;
}

:root.dark .rank-road-dot {
  background-color: #334155;
  border-color: #1e293b;
}

.dot-active {
  background-color: #22c55e;
  box-shadow: 0 0 10px rgba(34, 197, 94, 0.5);
}

.rank-road-right {
  flex: 1;
  display: flex;
  align-items: center;
  padding-left: 16px;
}

.rank-road-card {
  background: #f8fafc;
  border-radius: 12px;
  padding: 12px 16px;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}

:root.dark .rank-road-card {
  background: #334155;
  border-color: transparent;
}

.current-user-rank .rank-road-card {
  border-color: #4f46e5;
  background: rgba(79, 70, 229, 0.05);
}

:root.dark .current-user-rank .rank-road-card {
  background: rgba(79, 70, 229, 0.15);
}

.rank-road-title {
  color: #0f172a;
  font-weight: 700;
  font-size: 16px;
}

:root.dark .rank-road-title {
  color: white;
}

.rank-road-elo {
  color: #64748b;
  font-size: 13px;
  font-weight: 600;
}

:root.dark .rank-road-elo {
  color: #cbd5e1;
}

.current-badge {
  font-size: 10px;
  background: #4f46e5;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 800;
  margin-left: 8px;
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

.text-draw {
  color: #f59e0b;
}

.text-already_in_match {
  color: #dc2626;
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

/* === НОВЫЕ СТИЛИ ДЛЯ ИСТОРИИ (FULL WIDTH) === */
.history-full-container {
  margin-top: 24px;
  max-width: 1000px;
  margin-left: auto;
  margin-right: auto;
  background-color: white;
  border-radius: 20px;
  padding: 24px;
  border: 1px solid #f1f5f9;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.history-full-title {
  font-size: 20px;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 20px;
}

.history-full-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-full-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background-color: #f8fafc;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  transition: transform 0.2s ease;
}

.history-full-item:hover {
  transform: translateX(4px);
  background-color: #f1f5f9;
}

.history-players {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 700;
  font-size: 15px;
  color: #0f172a;
  flex: 1;
}

.player-me {
  color: #4f46e5;
}

.vs-badge {
  font-size: 12px;
  color: #94a3b8;
  text-transform: uppercase;
  font-weight: 800;
}

.player-opp {
  color: #0f172a;
}

.history-result-text {
  flex: 1;
  text-align: center;
  font-weight: 800;
  text-transform: uppercase;
  font-size: 13px;
  letter-spacing: 0.05em;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.result-icon-small {
  font-size: 16px;
}

.res-text-win {
  color: #22c55e;
}
.res-text-loss {
  color: #ef4444;
}
.res-text-draw {
  color: #f59e0b;
}
.res-text-neutral {
  color: #64748b;
}

.history-meta {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.history-elo-raw {
  font-weight: 800;
  font-size: 15px;
}

.elo-plus {
  color: #22c55e;
}
.elo-minus {
  color: #ef4444;
}

.history-date-full {
  font-size: 11px;
  color: #94a3b8;
  font-weight: 600;
}

.loading-history {
  color: #94a3b8;
  font-size: 14px;
  text-align: center;
  padding: 20px;
  font-weight: 500;
}

.load-more-btn {
  width: 100%;
  padding: 12px;
  margin-top: 12px;
  background-color: #f1f5f9;
  border: none;
  border-radius: 12px;
  color: #475569;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.load-more-btn:hover {
  background-color: #e2e8f0;
  color: #0f172a;
}

/* Анимации */
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* ==================== ТЁМНАЯ ТЕМА ==================== */

:root.dark .pvp-container {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

:root.dark .idle-state {
  background-color: #1e293b;
  border-color: #334155;
}

:root.dark .arena-badge {
  background-color: rgba(59, 130, 246, 0.2);
  color: rgba(147, 197, 253, 0.8);
  border-color: rgba(59, 130, 246, 0.3);
}

:root.dark .arena-description {
  color: #a5b4fc;
}

:root.dark .searching-state,
:root.dark .result-state {
  background-color: #1e293b;
  border-color: #334155;
  color: #f1f5f9;
}

:root.dark .searching-text h2 {
  color: #f8fafc;
}

:root.dark .searching-text p {
  color: #cbd5e1;
}

:root.dark .playing-state {
  background-color: #1e293b;
  border-color: #334155;
}

:root.dark .match-header {
  background-color: #334155;
}

:root.dark .task-container {
  background-color: #0f172a;
}

:root.dark .task-title {
  color: #f8fafc;
}

:root.dark .task-description p {
  color: #cbd5e1;
}

:root.dark .game-controls {
  background-color: #1e293b;
  border-top-color: #334155;
}

:root.dark .game-logs {
  color: #e2e8f0;
}

:root.dark .answer-input {
  background-color: #334155;
  border-color: #475569;
  color: #f1f5f9;
}

:root.dark .answer-input:focus {
  border-color: #3b82f6;
}

:root.dark .answer-input::placeholder {
  color: #94a3b8;
}

:root.dark .stats-card {
  background-color: #1e293b;
  border-color: #334155;
  color: #f1f5f9;
}

:root.dark .stats-title {
  color: #f8fafc;
}

:root.dark .stat-item {
  background-color: #334155;
}

:root.dark .stat-label {
  color: #cbd5e1;
}

:root.dark .stat-value {
  color: #f1f5f9;
}

/* History dark */
:root.dark .history-full-container {
  background-color: #1e293b;
  border-color: #334155;
}

:root.dark .history-full-title {
  color: #f8fafc;
}

:root.dark .history-full-item {
  background-color: #0f172a;
  border-color: #334155;
}

:root.dark .history-full-item:hover {
  background-color: #334155;
}

:root.dark .player-me {
  color: #818cf8;
}

:root.dark .player-opp {
  color: #f1f5f9;
}

:root.dark .history-date-full {
  color: #64748b;
}

:root.dark .load-more-btn {
  background-color: #334155;
  color: #cbd5e1;
}

:root.dark .load-more-btn:hover {
  background-color: #475569;
  color: #f1f5f9;
}

/* Loading task */
:root.dark .loading-task {
  color: #94a3b8;
}

/* Game logs */
:root.dark .log-system {
  color: #60a5fa;
}

:root.dark .log-error {
  color: #f87171;
}

:root.dark .log-user {
  color: #cbd5e1;
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

  .stats-card {
    padding: 24px;
  }

  .history-full-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .history-meta {
    align-items: flex-start;
    flex-direction: row;
    justify-content: space-between;
    width: 100%;
  }

  .idle-layout {
    grid-template-columns: 1fr;
  }

  .rank-card-vertical {
    margin-top: 16px;
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

  .stats-card {
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

  .pvp-grid,
  .history-full-container {
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

  .stats-card {
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

  .pvp-grid,
  .history-full-container {
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

  .pvp-grid,
  .history-full-container {
    max-width: 1400px;
  }

  .idle-state {
    min-height: 450px;
  }

  .arena-title {
    font-size: 52px;
  }

  .stats-card {
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

  .pvp-grid,
  .history-full-container {
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

  .stats-card {
    padding: 36px;
    border-radius: 28px;
  }
}
</style>
