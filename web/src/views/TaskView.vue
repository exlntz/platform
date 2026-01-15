<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'


import { useTimerStore } from '@/web/src/TimerStore'
import { useTimerRunner } from '@/web/src/TimerRunner'
const timer = useTimerStore()


const route = useRoute()
const task = ref(null)
const loading = ref(true)
const answer = ref('')
const checkLoading = ref(false)
const checkResult = ref(null)
const isSolved = ref(false) // НОВОЕ: Локальный флаг решения (сбрасывается при обновлении страницы)

const getAuthHeader = () => {
  return { headers: { Authorization: `Bearer ${localStorage.getItem('user-token')}` } }
}

// Загрузка задачи
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

// Отправка ответа
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

    if (response.data.is_correct) {
      isSolved.value = true // БЛОКИРУЕМ интерфейс (только до перезагрузки)
    }
    // Если ответ неверный, isSolved остается false, можно пробовать дальше
  } catch (err) {
    checkResult.value = {
      is_correct: false,
      message: 'Ошибка сервера. Попробуйте позже.'
    }
  } finally {
    checkLoading.value = false
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
              <span class="px-3 py-1 rounded-lg text-xs font-bold uppercase tracking-widest border border-white/10 bg-white/5">
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

            <div v-if="checkResult"
                 class="p-5 rounded-2xl text-sm font-black flex items-center justify-between animate-fade-in-up"
                 :class="checkResult.is_correct ? 'bg-green-50 text-green-700 border border-green-100' : 'bg-red-50 text-red-600 border border-red-100'"
            >
              <div class="flex items-center gap-3">
                <span class="text-2xl">{{ checkResult.is_correct ? '🎉' : '❌' }}</span>
                <span>{{ checkResult.message }}</span>
              </div>
            </div>

            <div class="relative">
              <label class="block text-xs font-black text-slate-400 uppercase tracking-widest mb-2 ml-1">Ваш ответ</label>
              <textarea
                v-model="answer"
                rows="3"
                :disabled="isSolved"
                placeholder="Введите решение..."
                class="w-full bg-slate-50 border-2 border-slate-200 rounded-2xl p-5 text-slate-900 font-medium focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 transition-all resize-none disabled:bg-slate-50 disabled:text-slate-500 disabled:border-slate-100 disabled:cursor-not-allowed"
                :class="{
                  'border-green-500 bg-green-50/10': isSolved,
                  'border-red-300 bg-red-50/30': checkResult && !checkResult.is_correct
                }"
              ></textarea>
            </div>

            <div class="pt-2">
                <router-link
                    v-if="isSolved"
                    to="/tasks"
                    class="w-full py-4 bg-slate-900 hover:bg-slate-800 text-white font-black rounded-2xl shadow-xl transition-all active:scale-[0.98] flex justify-center items-center gap-2"
                >
                    <span>← Вернуться ко всем задачам</span>
                </router-link>

                <button
                    v-else
                    @click="submitAnswer"
                    :disabled="checkLoading || !answer"
                    class="w-full py-4 bg-indigo-600 hover:bg-indigo-700 text-white font-black rounded-2xl shadow-xl shadow-indigo-200 transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2"
                >
                    <span v-if="checkLoading" class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                    <span>{{ checkLoading ? 'Проверка...' : 'Отправить решение' }}</span>
                </button>
            </div>

          </div>
        </div>

      </div>
    </div>
    <div v-if="timer.isAfkAlertVisible" class="modal">
      <p>Are you still here?</p>
      <button @click="timer.confirmAfk">Yes</button>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in-up {
  animation: fadeInUp 0.4s ease-out;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
