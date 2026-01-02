<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const task = ref(null)
const loading = ref(true)
const answer = ref('')
const checkLoading = ref(false)
const checkResult = ref(null) // { is_correct: boolean, message: string }

// Получение заголовка авторизации
const getAuthHeader = () => {
  return { headers: { Authorization: `Bearer ${localStorage.getItem('user-token')}` } }
}

// Загрузка одной задачи
const fetchTask = async () => {
  try {
    const response = await axios.get(`http://127.0.0.1:8000/tasks/${route.params.id}`, getAuthHeader())
    task.value = response.data
  } catch (err) {
    console.error('Ошибка:', err)
  } finally {
    loading.value = false
  }
}

// Проверка ответа
const submitAnswer = async () => {
  if (!answer.value.trim()) return

  checkLoading.value = true
  checkResult.value = null

  try {
    const response = await axios.post(
      `http://127.0.0.1:8000/tasks/${task.value.id}/check`,
      { answer: answer.value },
      getAuthHeader()
    )

    checkResult.value = response.data

    // Если правильно - очищаем поле через пару секунд (опционально)
    if (response.data.is_correct) {
      // Здесь можно добавить логику обновления очков пользователя, если она не на бэке
    }
  } catch (err) {
    checkResult.value = {
      is_correct: false,
      message: 'Ошибка сервера. Попробуйте позже.'
    }
  } finally {
    checkLoading.value = false
  }
}

// Цвет сложности для бейджа
const getDifficultyColor = (diff) => {
  if (!diff) return ''
  switch(diff.toLowerCase()) {
    case 'easy': return 'text-green-600 bg-green-50 border-green-100'
    case 'medium': return 'text-amber-600 bg-amber-50 border-amber-100'
    case 'hard': return 'text-red-600 bg-red-50 border-red-100'
    default: return 'text-slate-600'
  }
}

onMounted(() => {
  fetchTask()
})
</script>

<template>
  <div class="min-h-screen bg-slate-50 py-12 px-6 flex justify-center">

    <div v-if="loading" class="animate-pulse flex flex-col items-center mt-20">
      <div class="h-8 w-64 bg-slate-200 rounded-full mb-4"></div>
      <div class="h-4 w-32 bg-slate-200 rounded-full"></div>
    </div>

    <div v-else-if="task" class="w-full max-w-3xl space-y-8">

      <router-link to="/tasks" class="inline-flex items-center gap-2 text-sm font-bold text-slate-500 hover:text-indigo-600 transition-colors">
        ← Вернуться к списку
      </router-link>

      <div class="bg-white rounded-[2.5rem] shadow-2xl shadow-slate-200/50 border border-slate-100 overflow-hidden">

        <div class="bg-slate-900 p-8 md:p-10 text-white relative overflow-hidden">
          <div class="absolute top-0 right-0 p-10 opacity-10 text-9xl">📝</div>
          <div class="relative z-10">
            <div class="flex gap-3 mb-6">
              <span class="px-3 py-1 bg-white/10 backdrop-blur-md rounded-lg text-xs font-bold uppercase tracking-widest text-indigo-200 border border-white/10">
                {{ task.subject }}
              </span>
              <span
                class="px-3 py-1 rounded-lg text-xs font-bold uppercase tracking-widest border border-white/10 bg-white/5"
              >
                {{ task.difficulty }}
              </span>
            </div>
            <h1 class="text-3xl md:text-4xl font-black tracking-tight leading-tight">
              {{ task.title }}
            </h1>
          </div>
        </div>

        <div class="p-8 md:p-10 space-y-8">
          <div class="prose prose-slate max-w-none">
            <h3 class="text-sm font-black text-slate-400 uppercase tracking-widest mb-4">Условие задачи</h3>
            <p class="text-lg text-slate-700 leading-relaxed font-medium whitespace-pre-wrap">
              {{ task.description }}
            </p>
          </div>

          <hr class="border-slate-100">

          <div class="space-y-4">
            <label class="block text-sm font-black text-slate-900">Ваш ответ</label>

            <div class="relative">
              <textarea
                v-model="answer"
                rows="4"
                placeholder="Введите решение или ответ..."
                class="w-full bg-slate-50 border-2 border-slate-200 rounded-2xl p-5 text-slate-900 font-medium focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 transition-all resize-none"
                :class="{'border-green-500 focus:border-green-500 focus:ring-green-500/10': checkResult?.is_correct, 'border-red-500 focus:border-red-500 focus:ring-red-500/10': checkResult?.is_correct === false}"
              ></textarea>

              <div v-if="checkResult" class="absolute top-4 right-4 text-2xl animate-bounce-short">
                {{ checkResult.is_correct ? '🎉' : '❌' }}
              </div>
            </div>

            <div v-if="checkResult" class="p-4 rounded-xl text-sm font-bold flex items-center gap-2"
              :class="checkResult.is_correct ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-600'"
            >
              <span>{{ checkResult.message }}</span>
            </div>

            <button
              @click="submitAnswer"
              :disabled="checkLoading || !answer"
              class="w-full py-4 bg-indigo-600 hover:bg-indigo-700 text-white font-black rounded-2xl shadow-xl shadow-indigo-100 transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2"
            >
              <span v-if="checkLoading" class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
              <span>{{ checkLoading ? 'Проверка...' : 'Отправить решение' }}</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
/* Анимация для иконки результата */
@keyframes bounce-short {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}
.animate-bounce-short {
  animation: bounce-short 0.3s ease-in-out;
}
</style>
