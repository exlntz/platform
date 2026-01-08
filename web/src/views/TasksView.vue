<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()

// --- СОСТОЯНИЕ ---
const tasks = ref([])
const loading = ref(true)
const error = ref(null)

// Фильтры
const filters = ref({
  search: '',      // Поиск по названию или теме
  subject: '',     // Предмет
  difficulty: ''   // Сложность
})

// Опции (можно вынести в отдельный константный файл)
const subjects = ['Математика', 'Информатика', 'Физика', 'Алгоритмы']
const difficulties = [
  { value: 'Easy', label: 'Легкая', color: 'text-emerald-700 bg-emerald-50 border-emerald-200' },
  { value: 'Medium', label: 'Средняя', color: 'text-amber-700 bg-amber-50 border-amber-200' },
  { value: 'Hard', label: 'Сложная', color: 'text-rose-700 bg-rose-50 border-rose-200' }
]

// --- ЛОГИКА ---

// Хелпер для заголовков авторизации
const getAuthHeader = () => {
  const token = localStorage.getItem('user-token')
  return token ? { headers: { Authorization: `Bearer ${token}` } } : {}
}

// Функция загрузки задач с защитой от "дребезга" (Debounce)
// Чтобы не отправлять запрос на каждую букву в поиске
let debounceTimer = null

const fetchTasks = async () => {
  loading.value = true
  error.value = null

  try {
    const params = {}
    if (filters.value.subject) params.subject = filters.value.subject
    if (filters.value.difficulty) params.difficulty = filters.value.difficulty
    // Если бы бэкенд поддерживал поиск, мы бы добавили params.search = filters.value.search
    // Пока реализуем фильтрацию поиска на клиенте для мгновенного отклика (если задач < 1000 это ок)

    const response = await axios.get('http://127.0.0.1:8000/tasks/', {
      params,
      ...getAuthHeader()
    })

    tasks.value = response.data
  } catch (err) {
    console.error('Ошибка загрузки:', err)
    error.value = 'Сервер временно недоступен. Попробуйте обновить страницу.'
  } finally {
    // Имитация задержки для плавности анимации (можно убрать в проде)
    setTimeout(() => { loading.value = false }, 400)
  }
}

// Дебаунс-обертка для вотчера
const debouncedFetch = () => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    fetchTasks()
  }, 500) // Ждем 500мс после ввода, прежде чем грузить
}

// Клиентская фильтрация поиска (пока бэкенд не научится искать по text)
const filteredTasks = computed(() => {
  if (!filters.value.search) return tasks.value

  const searchLower = filters.value.search.toLowerCase()
  return tasks.value.filter(task =>
    task.title.toLowerCase().includes(searchLower) ||
    (task.theme && task.theme.toLowerCase().includes(searchLower))
  )
})

const resetFilters = () => {
  filters.value = { search: '', subject: '', difficulty: '' }
  fetchTasks()
}

// Парсинг тегов из строки "Тема1, Тема2"
const getTags = (themeStr) => {
  if (!themeStr) return []
  return themeStr.split(',')
    .map(t => t.trim())
    .filter(t => t.length > 0)
    .slice(0, 3) // Показываем максимум 3 тега
}

const getDifficultyClass = (diff) => {
  const found = difficulties.find(d => d.value === diff)
  return found ? found.color : 'text-slate-600 bg-slate-100 border-slate-200'
}

// Переход к решению
const navigateToTask = (id) => {
  router.push(`/tasks/${id}`)
}

// Следим за фильтрами (кроме поиска, он фильтруется на клиенте)
watch(() => [filters.value.subject, filters.value.difficulty], () => {
  fetchTasks()
})

onMounted(() => {
  fetchTasks()
})
</script>

<template>
  <div class="min-h-screen bg-[#F8FAFC] font-sans selection:bg-indigo-100 selection:text-indigo-700">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">

      <div class="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div class="space-y-2">
          <h1 class="text-3xl md:text-4xl font-extrabold text-slate-900 tracking-tight">
            Тренировочные задачи
          </h1>
          <p class="text-slate-500 font-medium max-w-2xl text-lg">
            Улучшайте навыки программирования, решая задачи разной сложности.
            Ваш прогресс сохраняется автоматически.
          </p>
        </div>

        <div v-if="!loading" class="hidden md:block">
          <span class="inline-flex items-center px-4 py-2 rounded-full text-sm font-bold bg-white border border-slate-200 text-slate-600 shadow-sm">
            Доступно задач: {{ filteredTasks.length }}
          </span>
        </div>
      </div>

      <div class="bg-white p-4 rounded-2xl shadow-sm border border-slate-200 flex flex-col lg:flex-row gap-4 sticky top-4 z-30 transition-all">

        <div class="flex-1 relative group">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-slate-400 group-focus-within:text-indigo-500 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input
            v-model="filters.search"
            type="text"
            placeholder="Поиск по названию или теме..."
            class="block w-full pl-10 pr-3 py-3 border border-slate-200 rounded-xl leading-5 bg-slate-50 text-slate-900 placeholder-slate-400 focus:outline-none focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all font-medium sm:text-sm"
          />
        </div>

        <div class="flex flex-col sm:flex-row gap-4">
          <div class="relative min-w-[180px]">
            <select
              v-model="filters.subject"
              class="appearance-none block w-full pl-4 pr-10 py-3 border border-slate-200 rounded-xl leading-5 bg-white text-slate-700 font-bold focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm transition-shadow cursor-pointer hover:border-indigo-300"
            >
              <option value="">Все предметы</option>
              <option v-for="s in subjects" :key="s" :value="s">{{ s }}</option>
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-slate-500">
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
            </div>
          </div>

          <div class="relative min-w-[180px]">
            <select
              v-model="filters.difficulty"
              class="appearance-none block w-full pl-4 pr-10 py-3 border border-slate-200 rounded-xl leading-5 bg-white text-slate-700 font-bold focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm transition-shadow cursor-pointer hover:border-indigo-300"
            >
              <option value="">Сложность</option>
              <option v-for="d in difficulties" :key="d.value" :value="d.value">{{ d.label }}</option>
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-slate-500">
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
            </div>
          </div>

          <button
            @click="resetFilters"
            class="flex items-center justify-center px-4 py-3 border border-slate-200 rounded-xl bg-white text-slate-500 hover:text-red-500 hover:bg-red-50 hover:border-red-100 transition-colors"
            title="Сбросить фильтры"
          >
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
      </div>

      <div v-if="error" class="bg-red-50 border border-red-100 rounded-2xl p-8 text-center animate-fade-in">
        <div class="text-4xl mb-4">🔌</div>
        <h3 class="text-lg font-bold text-red-800 mb-2">Ошибка соединения</h3>
        <p class="text-red-600 mb-6">{{ error }}</p>
        <button @click="fetchTasks" class="px-6 py-2 bg-white text-red-700 font-bold rounded-lg shadow-sm hover:shadow border border-red-100 transition-all">Попробовать снова</button>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

        <template v-if="loading">
          <div v-for="i in 6" :key="i" class="bg-white rounded-[1.5rem] p-6 border border-slate-100 shadow-sm h-72 flex flex-col animate-pulse">
            <div class="flex justify-between mb-6">
              <div class="h-6 w-24 bg-slate-100 rounded-full"></div>
              <div class="h-6 w-16 bg-slate-100 rounded-full"></div>
            </div>
            <div class="h-8 w-3/4 bg-slate-100 rounded-lg mb-4"></div>
            <div class="space-y-2 mb-auto">
              <div class="h-4 w-full bg-slate-50 rounded"></div>
              <div class="h-4 w-5/6 bg-slate-50 rounded"></div>
            </div>
            <div class="h-10 w-full bg-slate-100 rounded-xl mt-4"></div>
          </div>
        </template>

        <template v-else-if="filteredTasks.length === 0">
          <div class="col-span-full flex flex-col items-center justify-center py-20 text-center">
            <div class="w-24 h-24 bg-slate-100 rounded-full flex items-center justify-center mb-6 text-4xl">
              🔍
            </div>
            <h3 class="text-xl font-bold text-slate-900">Задачи не найдены</h3>
            <p class="text-slate-500 mt-2 max-w-sm">
              Попробуйте изменить параметры поиска или сбросить фильтры.
            </p>
            <button @click="resetFilters" class="mt-6 text-indigo-600 font-bold hover:text-indigo-800 hover:underline">
              Сбросить все фильтры
            </button>
          </div>
        </template>

        <template v-else>
          <div
            v-for="task in filteredTasks"
            :key="task.id"
            class="group bg-white rounded-[1.5rem] border border-slate-100 p-6 shadow-sm hover:shadow-xl hover:shadow-indigo-900/5 hover:-translate-y-1 transition-all duration-300 flex flex-col relative overflow-hidden"
          >
            <div class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>

            <div class="flex justify-between items-start mb-4">
              <span class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-bold uppercase tracking-wide bg-slate-100 text-slate-500">
                {{ task.subject }}
              </span>
              <span
                class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-extrabold uppercase tracking-wide border"
                :class="getDifficultyClass(task.difficulty)"
              >
                {{ task.difficulty }}
              </span>
            </div>

            <h3 class="text-xl font-bold text-slate-900 mb-3 group-hover:text-indigo-600 transition-colors line-clamp-2">
              {{ task.title }}
            </h3>

            <p class="text-slate-500 text-sm font-medium leading-relaxed mb-6 line-clamp-3">
              {{ task.description }}
            </p>

            <div class="mt-auto pt-6 border-t border-slate-50 flex items-center justify-between gap-4">

              <div class="flex flex-wrap gap-1.5 overflow-hidden max-h-6">
                <span
                  v-for="(tag, idx) in getTags(task.theme)"
                  :key="idx"
                  class="text-[10px] font-bold text-slate-500 bg-slate-50 px-2 py-0.5 rounded border border-slate-100"
                >
                  #{{ tag }}
                </span>
              </div>

              <button
                @click="navigateToTask(task.id)"
                class="shrink-0 bg-slate-900 text-white text-sm font-bold px-5 py-2.5 rounded-xl shadow-lg shadow-slate-200 group-hover:bg-indigo-600 group-hover:shadow-indigo-200 transition-all active:scale-95 flex items-center gap-2"
              >
                Решать
                <svg class="w-4 h-4 group-hover:translate-x-0.5 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </button>
            </div>
          </div>
        </template>

      </div>
    </div>
  </div>
</template>

<style scoped>
/* Анимация плавного появления */
.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
