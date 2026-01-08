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
  <div class="min-h-screen bg-slate-50 py-12 px-6 font-sans">
    <div class="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">

      <div class="lg:col-span-2 space-y-8">

        <div v-if="gameState === 'idle'" class="relative overflow-hidden bg-slate-900 rounded-[2.5rem] p-10 shadow-2xl shadow-indigo-200 h-96 flex flex-col justify-center items-start">
          <div class="relative z-10 space-y-6">
            <div class="inline-block px-4 py-1 bg-indigo-500/20 text-indigo-300 text-[10px] font-black uppercase tracking-widest rounded-full border border-indigo-500/30">
              PvP Arena
            </div>
            <h1 class="text-5xl font-black text-white tracking-tight">Готов к битве?</h1>
            <p class="text-indigo-200 max-w-md font-medium">Сразись с реальным противником. Кто первый решит задачу — забирает рейтинг.</p>

            <button
              @click="connectPvp"
              class="flex items-center gap-3 px-10 py-5 bg-[#1fb141] hover:bg-[#199435] text-white font-black rounded-2xl shadow-xl transition-all transform hover:scale-105 active:scale-95"
            >
              🔥 Найти противника
            </button>
          </div>
          <div class="absolute -right-20 -bottom-20 w-80 h-80 bg-indigo-600/20 rounded-full blur-3xl"></div>
        </div>

        <div v-else-if="gameState === 'searching'" class="bg-white rounded-[2.5rem] p-10 shadow-xl border border-slate-100 h-96 flex flex-col items-center justify-center text-center space-y-6">
          <div class="relative">
            <div class="w-20 h-20 border-4 border-indigo-100 border-t-indigo-600 rounded-full animate-spin"></div>
            <div class="absolute inset-0 flex items-center justify-center text-2xl">⚔️</div>
          </div>
          <div>
            <h2 class="text-2xl font-black text-slate-900">Поиск оппонента...</h2>
            <p class="text-slate-500 font-medium mt-2">Подбираем равного по силе соперника</p>
          </div>
          <button @click="disconnect" class="text-sm font-bold text-red-500 hover:text-red-600">Отмена</button>
        </div>

        <div v-else-if="gameState === 'playing'" class="bg-white rounded-[2.5rem] border border-slate-100 shadow-xl overflow-hidden flex flex-col h-[600px]">
          <div class="bg-slate-900 px-8 py-6 flex justify-between items-center text-white">
            <div class="flex items-center gap-3">
              <span class="w-3 h-3 bg-red-500 rounded-full animate-pulse"></span>
              <span class="font-black tracking-widest uppercase text-sm">Live Match</span>
            </div>
            <div class="text-xs font-bold text-indigo-300">Решай быстрее!</div>
          </div>

          <div class="flex-1 overflow-y-auto p-8 bg-slate-50">
            <div v-if="activeTask" class="space-y-6 max-w-3xl mx-auto">
              <div>
                <div class="flex gap-2 mb-4">
                  <span class="px-3 py-1 bg-white border border-slate-200 rounded-lg text-[10px] font-black uppercase text-slate-500">{{ activeTask.subject }}</span>
                  <span class="px-3 py-1 bg-indigo-50 border border-indigo-100 text-indigo-600 rounded-lg text-[10px] font-black uppercase">{{ activeTask.difficulty }}</span>
                </div>
                <h2 class="text-2xl font-black text-slate-900">{{ activeTask.title }}</h2>
              </div>
              <div class="prose prose-slate">
                <p class="text-slate-700 font-medium whitespace-pre-wrap leading-relaxed">{{ activeTask.description }}</p>
              </div>
            </div>
            <div v-else class="h-full flex items-center justify-center text-slate-400 font-bold animate-pulse">
              Загрузка задачи...
            </div>
          </div>

          <div class="border-t border-slate-200 bg-white p-6 space-y-4">
            <div ref="logContainer" class="h-32 overflow-y-auto space-y-2 pr-2 mb-2 custom-scrollbar">
              <div v-for="log in logs" :key="log.id" class="text-sm font-medium">
                <span v-if="log.type === 'system'" class="text-indigo-500">🤖 {{ log.text }}</span>
                <span v-else-if="log.type === 'error'" class="text-red-500">❌ {{ log.text }}</span>
                <span v-else class="text-slate-700">👤 Вы: {{ log.text }}</span>
              </div>
            </div>

            <form @submit.prevent="sendAnswer" class="flex gap-3">
              <input
                v-model="userAnswer"
                placeholder="Введите ответ..."
                class="flex-1 bg-slate-50 border-2 border-slate-200 rounded-xl px-4 py-3 font-bold text-slate-900 focus:outline-none focus:border-indigo-500 transition-colors"
                autoFocus
              >
              <button type="submit" class="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-black rounded-xl shadow-lg transition-transform active:scale-95">
                Отправить
              </button>
            </form>
          </div>
        </div>

        <div v-else-if="gameState === 'result'" class="bg-white rounded-[2.5rem] p-10 shadow-xl border border-slate-100 h-96 flex flex-col items-center justify-center text-center space-y-6">
          <div class="text-6xl mb-2">
            {{ gameResult === 'win' ? '🏆' : (gameResult === 'loss' ? '💀' : '🔌') }}
          </div>
          <div>
            <h1 class="text-4xl font-black" :class="gameResult === 'win' ? 'text-green-600' : 'text-red-600'">
              {{ gameResult === 'win' ? 'ПОБЕДА!' : (gameResult === 'loss' ? 'ПОРАЖЕНИЕ' : 'ОППОНЕНТ ВЫШЕЛ') }}
            </h1>
            <p class="text-slate-500 font-bold mt-2 text-lg">
              {{ gameResult === 'win' ? '+25 очков рейтинга' : (gameResult === 'loss' ? '-25 очков рейтинга' : 'Вам присуждена техническая победа') }}
            </p>
          </div>
          <button @click="connectPvp" class="px-8 py-4 bg-slate-900 text-white font-black rounded-xl shadow-lg hover:bg-slate-800 transition-all">
            Играть снова
          </button>
        </div>

      </div>

      <div class="space-y-8">
        <div class="bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-xl">
          <h3 class="text-xl font-black text-slate-900 mb-6">Твои успехи</h3>
          <div class="space-y-4">
            <div class="flex justify-between items-center p-4 bg-slate-50 rounded-2xl">
              <span class="text-xs font-bold text-slate-400 uppercase">Ранг</span>
              <span class="font-black text-indigo-600">{{ stats.rank }}</span>
            </div>
            <div class="flex justify-between items-center p-4 bg-slate-50 rounded-2xl">
              <span class="text-xs font-bold text-slate-400 uppercase">Очки</span>
              <span class="font-black text-slate-900">{{ stats.points }}</span>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden rounded-[2.5rem] border border-slate-100 shadow-xl">
          <div class="p-6 bg-slate-900 text-white font-black text-center">
            🏆 ТОП МАСТЕРОВ
          </div>
          <div class="p-2">
            <div v-for="(player, index) in leaderboard" :key="player.id" class="flex items-center gap-4 p-4 hover:bg-slate-50 rounded-2xl transition-colors">
              <span class="w-6 text-sm font-black text-slate-300">#{{ index + 1 }}</span>
              <div class="w-10 h-10 bg-slate-100 rounded-xl flex items-center justify-center text-lg">
                {{ player.avatar }}
              </div>
              <div class="flex-1">
                <p class="text-sm font-bold text-slate-800">{{ player.name }}</p>
                <p class="text-[10px] font-black text-indigo-500 uppercase">{{ player.points }} PTS</p>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 20px;
}
</style>
