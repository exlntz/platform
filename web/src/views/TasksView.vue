<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'

// Состояние данных
const tasks = ref([])
const loading = ref(true)
const error = ref(null)

// Фильтры
const filters = ref({
  subject: '',
  difficulty: ''
})

// Опции для селектов (можно вынести в конфиг)
const subjects = ['Математика', 'Информатика', 'Физика', 'Алгоритмы']
const difficulties = [
  { value: 'Easy', label: 'Легкая', color: 'text-green-600 bg-green-50 border-green-100' },
  { value: 'Medium', label: 'Средняя', color: 'text-amber-600 bg-amber-50 border-amber-100' },
  { value: 'Hard', label: 'Сложная', color: 'text-red-600 bg-red-50 border-red-100' }
]

// Получение заголовка авторизации
const getAuthHeader = () => {
  const token = localStorage.getItem('user-token')
  return token ? { headers: { Authorization: `Bearer ${token}` } } : {}
}

// Функция загрузки задач
const fetchTasks = async () => {
  loading.value = true
  error.value = null
  try {
    // Формируем параметры запроса
    const params = {}
    if (filters.value.subject) params.subject = filters.value.subject
    if (filters.value.difficulty) params.difficulty = filters.value.difficulty

    const response = await axios.get('http://127.0.0.1:8000/tasks/', {
      params,
      ...getAuthHeader()
    })
    tasks.value = response.data
  } catch (err) {
    console.error('Ошибка загрузки задач:', err)
    error.value = 'Не удалось загрузить задачи. Попробуйте позже.'
  } finally {
    // Небольшая задержка для плавности UI, если ответ слишком быстрый
    setTimeout(() => { loading.value = false }, 300)
  }
}

// Вспомогательная функция для цвета сложности
const getDifficultyClass = (diff) => {
  const found = difficulties.find(d => d.value.toLowerCase() === diff.toLowerCase())
  return found ? found.color : 'text-slate-600 bg-slate-100 border-slate-200'
}

// Следим за изменением фильтров и перезагружаем данные
watch(filters, () => {
  fetchTasks()
}, { deep: true })

onMounted(() => {
  fetchTasks()
})
</script>

<template>
  <div class="min-h-screen bg-slate-50 py-12 px-6 font-sans">
    <div class="max-w-7xl mx-auto space-y-10">

      <div class="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div class="space-y-2">
          <h1 class="text-4xl font-black text-slate-900 tracking-tight">Банк задач</h1>
          <p class="text-slate-500 font-medium max-w-xl">
            Выбирай задачи по уровню и предмету. Решай, прокачивай рейтинг и готовься к победам.
          </p>
        </div>

        <div class="flex gap-4">
          <select
            v-model="filters.subject"
            class="bg-white border border-slate-200 text-slate-700 text-sm font-bold rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-indigo-500 shadow-sm transition-all cursor-pointer hover:border-indigo-300"
          >
            <option value="">Все предметы</option>
            <option v-for="subj in subjects" :key="subj" :value="subj">{{ subj }}</option>
          </select>

          <select
            v-model="filters.difficulty"
            class="bg-white border border-slate-200 text-slate-700 text-sm font-bold rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-indigo-500 shadow-sm transition-all cursor-pointer hover:border-indigo-300"
          >
            <option value="">Любая сложность</option>
            <option v-for="diff in difficulties" :key="diff.value" :value="diff.value">{{ diff.label }}</option>
          </select>
        </div>
      </div>

      <div v-if="error" class="bg-red-50 text-red-600 p-6 rounded-2xl border border-red-100 flex items-center gap-3">
        <span class="text-2xl">⚠️</span>
        <span class="font-bold">{{ error }}</span>
        <button @click="fetchTasks" class="ml-auto px-4 py-2 bg-white rounded-lg shadow-sm text-sm font-bold hover:bg-red-50">Повторить</button>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

        <template v-if="loading">
          <div v-for="n in 6" :key="n" class="bg-white p-6 rounded-[2rem] border border-slate-100 h-64 animate-pulse flex flex-col justify-between">
            <div class="space-y-4">
              <div class="flex justify-between">
                <div class="h-6 w-24 bg-slate-100 rounded-full"></div>
                <div class="h-6 w-16 bg-slate-100 rounded-full"></div>
              </div>
              <div class="h-8 w-3/4 bg-slate-100 rounded-xl"></div>
              <div class="space-y-2">
                <div class="h-4 w-full bg-slate-50 rounded-lg"></div>
                <div class="h-4 w-5/6 bg-slate-50 rounded-lg"></div>
              </div>
            </div>
            <div class="h-12 w-full bg-slate-100 rounded-xl mt-4"></div>
          </div>
        </template>

        <template v-else>
          <div
            v-for="task in tasks"
            :key="task.id"
            class="group bg-white p-7 rounded-[2rem] border border-slate-100 shadow-xl shadow-slate-200/40 hover:shadow-2xl hover:shadow-indigo-500/10 hover:-translate-y-1 transition-all duration-300 flex flex-col"
          >
            <div class="flex justify-between items-start mb-4">
              <span class="text-[10px] font-black uppercase tracking-widest text-slate-400 bg-slate-50 px-3 py-1.5 rounded-lg">
                {{ task.subject }}
              </span>
              <span
                class="text-[10px] font-black uppercase tracking-widest px-3 py-1.5 rounded-lg border"
                :class="getDifficultyClass(task.difficulty)"
              >
                {{ task.difficulty }}
              </span>
            </div>

            <h3 class="text-xl font-black text-slate-900 mb-3 group-hover:text-indigo-600 transition-colors line-clamp-2">
              {{ task.title }}
            </h3>

            <p class="text-sm text-slate-500 font-medium mb-6 line-clamp-3 leading-relaxed">
              {{ task.description }}
            </p>

            <div class="mt-auto pt-6 border-t border-slate-50 flex items-center justify-between">
              <div class="text-xs font-bold text-slate-400">
                #{{ task.theme || 'Общее' }}
              </div>
              <router-link
                :to="`/tasks/${task.id}`"
                class="px-6 py-2.5 bg-slate-900 text-white text-sm font-bold rounded-xl shadow-lg group-hover:bg-indigo-600 group-hover:shadow-indigo-200 transition-all active:scale-95 flex items-center gap-2"
              >
                Решать <span class="group-hover:translate-x-1 transition-transform">→</span>
              </router-link>
            </div>
          </div>
        </template>

        <div v-if="!loading && tasks.length === 0" class="col-span-full py-20 text-center">
          <div class="text-6xl mb-4">🔍</div>
          <h3 class="text-2xl font-black text-slate-900">Задачи не найдены</h3>
          <p class="text-slate-500 mt-2">Попробуй изменить фильтры</p>
        </div>

      </div>
    </div>
  </div>
</template>
