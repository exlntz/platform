<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

// --- СОСТОЯНИЕ ИНТЕРФЕЙСА ---
const currentTab = ref('dashboard')
const accessDenied = ref(false)
const loading = ref(false)
const showTaskModal = ref(false)
const fileInput = ref(null)

// --- НОВОЕ: УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ ---
const activeMenuId = ref(null) // ID пользователя, у которого открыто меню действий
const showUserEditModal = ref(false) // Флаг показа модалки редактирования профиля
const userEditForm = ref({ id: null, username: '', email: '', rating: 0 })

// --- РЕДАКТИРОВАНИЕ ЗАДАЧ ---
const isEditMode = ref(false)
const currentEditId = ref(null)
// Временное хранилище для ввода тегов строкой "тег1, тег2"
const tagsInput = ref('')

// --- СОРТИРОВКА ЗАДАЧ ---
const sortKey = ref('id') // По умолчанию сортируем по ID
const sortOrder = ref('asc') // По возрастанию (1, 2, 3...)

// --- ДАННЫЕ ---
const stats = ref({
  total_users: 0,
  total_tasks: 0,
  average_rating: 0,
  new_users_24h: 0,
  most_popular_subject: 'Загрузка...'
})
const users = ref([])
const tasks = ref([])

// Форма задачи (Обновлена структура под новые требования)
const taskForm = ref({
  title: '',
  description: '',
  subject: '',
  tags: [], // Массив строк вместо theme
  difficulty: 'Easy',
  correct_answer: '',
  hint: '' // Новое поле
})

const difficultyOptions = ['Easy', 'Medium', 'Hard']
const subjectOptions = ['Математика', 'Информатика', 'Физика', 'Алгоритмы']

// --- ВЫЧИСЛЯЕМЫЕ СВОЙСТВА (СОРТИРОВКА) ---
const sortedTasks = computed(() => {
  return [...tasks.value].sort((a, b) => {
    let modifier = sortOrder.value === 'asc' ? 1 : -1

    let valA = a[sortKey.value]
    let valB = b[sortKey.value]

    // Веса для сложности
    if (sortKey.value === 'difficulty') {
      const weights = { 'Easy': 1, 'Medium': 2, 'Hard': 3 }
      valA = weights[valA] || 0
      valB = weights[valB] || 0
    }

    // Числа
    if (typeof valA === 'number' && typeof valB === 'number') {
      return (valA - valB) * modifier
    }

    // Строки
    if (typeof valA === 'string' && typeof valB === 'string') {
      return valA.localeCompare(valB) * modifier
    }

    return 0
  })
})

const sortBy = (key) => {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'asc'
  }
}

// --- API ХЕЛПЕРЫ ---
const getAuthHeader = () => {
  return { headers: { Authorization: `Bearer ${localStorage.getItem('user-token')}` } }
}

const handleApiError = (err) => {
  if (err.response && err.response.status === 403) {
    accessDenied.value = true
  } else {
    console.error('API Error:', err)
    // Показываем сообщение об ошибке (например, "Имя пользователя занято")
    alert('Ошибка: ' + (err.response?.data?.detail || err.message))
  }
}

// --- ЗАГРУЗКА ДАННЫХ ---
const fetchStats = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/admin/stats', getAuthHeader())
    stats.value = response.data
    accessDenied.value = false
  } catch (err) { handleApiError(err) }
}

const fetchUsers = async () => {
  if (accessDenied.value) return
  loading.value = true
  try {
    const response = await axios.get('http://127.0.0.1:8000/admin/users?limit=50', getAuthHeader())
    users.value = response.data
  } catch (err) { handleApiError(err) }
  finally { loading.value = false }
}

const fetchTasks = async () => {
  if (accessDenied.value) return
  loading.value = true
  try {
    const response = await axios.get('http://127.0.0.1:8000/tasks/', getAuthHeader())
    tasks.value = response.data
  } catch (err) { handleApiError(err) }
  finally { loading.value = false }
}

// --- УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ (НОВОЕ) ---

// Переключение меню действий
const toggleMenu = (event, id) => {
  event.stopPropagation()
  activeMenuId.value = activeMenuId.value === id ? null : id
}

// Открытие модалки редактирования
const openEditUser = (user) => {
  userEditForm.value = { ...user }
  showUserEditModal.value = true
  activeMenuId.value = null // Закрыть меню
}

// Универсальное обновление пользователя (Бан, Роль, Данные)
const updateUserAction = async (userId, data, successMessage = null) => {
  try {
    await axios.patch(`http://127.0.0.1:8000/admin/users/${userId}`, data, getAuthHeader())

    if (successMessage) alert(successMessage)

    fetchUsers() // Обновляем таблицу
    showUserEditModal.value = false // Закрываем модалку при успехе
  } catch (err) {
    // Здесь ловится 400 Bad Request, если имя занято
    handleApiError(err)
  }
}

// Удаление пользователя
const deleteUser = async (user) => {
  if (!confirm(`Вы уверены, что хотите безвозвратно удалить пользователя ${user.username}?`)) return
  try {
    await axios.delete(`http://127.0.0.1:8000/admin/users/${user.id}`, getAuthHeader())
    users.value = users.value.filter(u => u.id !== user.id)
    fetchStats()
  } catch (err) { handleApiError(err) }
}

// --- УПРАВЛЕНИЕ ЗАДАЧАМИ ---

const openCreateModal = () => {
  isEditMode.value = false
  currentEditId.value = null
  tagsInput.value = '' // Очищаем поле тегов

  // Инициализируем форму с пустыми значениями и пустым hint
  taskForm.value = {
    title: '',
    description: '',
    subject: 'Математика',
    tags: [],
    difficulty: 'Easy',
    correct_answer: '',
    hint: ''
  }
  showTaskModal.value = true
}

const openEditModal = async (task) => {
  isEditMode.value = true
  currentEditId.value = task.id
  taskForm.value = { ...task }

  // Превращаем массив тегов в строку для отображения в input
  tagsInput.value = (task.tags && Array.isArray(task.tags)) ? task.tags.join(', ') : ''

  showTaskModal.value = true
  try {
    const { data } = await axios.get(`http://127.0.0.1:8000/admin/tasks/${task.id}`, getAuthHeader())
    taskForm.value = { ...data }
    // Обновляем теги и hint из полных данных задачи
    tagsInput.value = (data.tags && Array.isArray(data.tags)) ? data.tags.join(', ') : ''
  } catch (e) { handleApiError(e) }
}

const saveTask = async () => {
  try {
    // Превращаем строку тегов обратно в массив перед отправкой
    taskForm.value.tags = tagsInput.value
      .split(',')
      .map(tag => tag.trim())
      .filter(tag => tag.length > 0)

    const finalUrl = isEditMode.value
       ? `http://127.0.0.1:8000/admin/tasks/${currentEditId.value}`
       : 'http://127.0.0.1:8000/admin/tasks/create'

    const method = isEditMode.value ? 'patch' : 'post'

    await axios[method](finalUrl, taskForm.value, getAuthHeader())

    alert(isEditMode.value ? 'Задача обновлена!' : 'Задача создана!')
    showTaskModal.value = false
    fetchTasks()
    fetchStats()
  } catch (err) { handleApiError(err) }
}

const deleteTask = async (taskId) => {
  if (!confirm(`Вы уверены, что хотите удалить задачу #${taskId}?`)) return
  try {
    await axios.delete(`http://127.0.0.1:8000/admin/tasks/${taskId}`, getAuthHeader())
    tasks.value = tasks.value.filter(t => t.id !== taskId)
    fetchStats()
  } catch (err) { handleApiError(err) }
}

const exportTasks = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/admin/tasks/export', { ...getAuthHeader(), responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `tasks_export_${new Date().toISOString().slice(0,10)}.json`)
    document.body.appendChild(link); link.click(); link.remove()
  } catch (err) { handleApiError(err) }
}

const triggerImport = () => fileInput.value.click()

const handleImport = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  const formData = new FormData(); formData.append('file', file)
  try {
    loading.value = true
    const response = await axios.post('http://127.0.0.1:8000/admin/tasks/import', formData, {
      headers: { ...getAuthHeader().headers, 'Content-Type': 'multipart/form-data' }
    })
    alert(`Импорт завершен!\nСоздано: ${response.data.created}\nОбновлено: ${response.data.updated}`)
    fetchTasks(); fetchStats()
  } catch (err) { handleApiError(err) }
  finally { loading.value = false; event.target.value = '' }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

// Жизненный цикл
onMounted(() => {
  window.addEventListener('click', () => { activeMenuId.value = null }) // Закрываем меню при клике вне
  fetchStats()
  fetchUsers()
})
</script>

<template>
  <div v-if="accessDenied" class="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-4">
    <div class="max-w-md w-full text-center space-y-8 animate-fade-in-up">
      <div class="w-24 h-24 bg-red-100 rounded-full flex items-center justify-center mx-auto shadow-xl shadow-red-100/50">
        <span class="text-5xl drop-shadow-sm">🔒</span>
      </div>
      <div class="space-y-3">
        <h1 class="text-4xl font-black text-slate-900 tracking-tight">Доступ запрещен</h1>
        <p class="text-slate-500 font-medium text-lg leading-relaxed">
          У вас недостаточно прав для просмотра этой страницы. <br>
          Эта зона только для администраторов.
        </p>
      </div>
      <div class="flex flex-col sm:flex-row gap-4 justify-center pt-4">
        <router-link to="/" class="px-8 py-4 bg-slate-900 text-white font-bold rounded-2xl shadow-lg hover:bg-slate-800 transition-all active:scale-95">
          На главную
        </router-link>
      </div>
      <p class="text-xs text-slate-400 font-mono mt-8">ERROR CODE: 403 FORBIDDEN</p>
    </div>
  </div>

  <div v-else class="min-h-screen bg-slate-50 flex font-sans">

    <aside class="w-64 bg-slate-900 text-white flex flex-col fixed h-full z-20 shadow-2xl">
      <div class="p-6 border-b border-slate-800 flex items-center gap-3">
        <div class="w-8 h-8 bg-indigo-500 rounded-lg flex items-center justify-center font-black shadow-lg shadow-indigo-500/20">A</div>
        <span class="font-bold text-lg tracking-tight">Admin Panel</span>
      </div>

      <nav class="flex-1 p-4 space-y-2">
        <button
          @click="currentTab = 'dashboard'"
          class="w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium text-sm group"
          :class="currentTab === 'dashboard' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-900/50' : 'text-slate-400 hover:bg-slate-800 hover:text-white'"
        >
          <span class="text-xl group-hover:scale-110 transition-transform">📊</span> Дашборд
        </button>
        <button
          @click="currentTab = 'users'"
          class="w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium text-sm group"
          :class="currentTab === 'users' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-900/50' : 'text-slate-400 hover:bg-slate-800 hover:text-white'"
        >
          <span class="text-xl group-hover:scale-110 transition-transform">👥</span> Пользователи
        </button>
        <button
          @click="currentTab = 'tasks'; fetchTasks()"
          class="w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium text-sm group"
          :class="currentTab === 'tasks' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-900/50' : 'text-slate-400 hover:bg-slate-800 hover:text-white'"
        >
          <span class="text-xl group-hover:scale-110 transition-transform">📝</span> Задачи
        </button>
      </nav>

      <div class="p-4 border-t border-slate-800">
        <router-link to="/" class="flex items-center gap-2 text-slate-400 hover:text-white text-xs font-bold uppercase tracking-widest transition-colors p-2 hover:bg-slate-800 rounded-lg">
          ← Вернуться на сайт
        </router-link>
      </div>
    </aside>

    <main class="flex-1 ml-64 p-8">

      <div v-if="currentTab === 'dashboard'" class="space-y-8 animate-fade-in">
        <div class="flex items-end justify-between">
            <h1 class="text-4xl font-black text-slate-900 tracking-tight">Обзор системы</h1>
            <span class="text-sm font-bold text-slate-400 bg-white px-3 py-1 rounded-full shadow-sm border border-slate-100">Live Updates</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
            <div class="flex items-center justify-between mb-4">
              <div class="w-12 h-12 rounded-2xl bg-blue-50 flex items-center justify-center text-blue-600 text-2xl">👥</div>
              <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Всего</span>
            </div>
            <p class="text-3xl font-black text-slate-900">{{ stats.total_users }}</p>
            <p class="text-sm text-slate-500 font-medium mt-1">пользователей</p>
          </div>

          <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
            <div class="flex items-center justify-between mb-4">
              <div class="w-12 h-12 rounded-2xl bg-green-50 flex items-center justify-center text-green-600 text-2xl">🔥</div>
              <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Динамика</span>
            </div>
            <p class="text-3xl font-black text-slate-900">+{{ stats.new_users_24h }}</p>
            <p class="text-sm text-slate-500 font-medium mt-1">за 24 часа</p>
          </div>

          <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
            <div class="flex items-center justify-between mb-4">
              <div class="w-12 h-12 rounded-2xl bg-amber-50 flex items-center justify-center text-amber-600 text-2xl">⭐</div>
              <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Скилл</span>
            </div>
            <p class="text-3xl font-black text-slate-900">{{ stats.average_rating }}</p>
            <p class="text-sm text-slate-500 font-medium mt-1">средний ELO</p>
          </div>

          <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
            <div class="flex items-center justify-between mb-4">
              <div class="w-12 h-12 rounded-2xl bg-purple-50 flex items-center justify-center text-purple-600 text-2xl">📚</div>
              <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Тренды</span>
            </div>
            <p class="text-xl font-black text-slate-900 truncate">{{ stats.most_popular_subject }}</p>
            <p class="text-sm text-slate-500 font-medium mt-1">выбор игроков</p>
          </div>
        </div>
      </div>

      <div v-if="currentTab === 'users'" class="space-y-6 animate-fade-in">
        <div class="flex items-center justify-between">
          <h1 class="text-3xl font-black text-slate-900">Управление пользователями</h1>
          <button @click="fetchUsers" class="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-xl text-slate-600 text-sm font-bold hover:bg-slate-50 transition-colors shadow-sm">
            🔄 Обновить
          </button>
        </div>

        <div class="bg-white rounded-[2rem] shadow-xl shadow-slate-200/40 border border-slate-100 overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="bg-slate-50/50 border-b border-slate-100 text-[10px] uppercase text-slate-400 font-black tracking-widest">
                  <th class="px-8 py-5">ID</th>
                  <th class="px-8 py-5">Пользователь</th>
                  <th class="px-8 py-5">Рейтинг</th>
                  <th class="px-8 py-5">Дата регистрации</th>
                  <th class="px-8 py-5">Роль / Статус</th>
                  <th class="px-8 py-5 text-right">Действия</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-50">
                <tr v-for="user in users" :key="user.id" class="hover:bg-slate-50 transition-colors group">
                  <td class="px-8 py-5 text-slate-300 font-mono text-xs font-bold">#{{ user.id }}</td>
                  <td class="px-8 py-5">
                    <div class="flex items-center gap-4">
                      <div class="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-sm font-black text-slate-500 group-hover:scale-110 group-hover:bg-indigo-100 group-hover:text-indigo-600 transition-all">
                        {{ user.username.charAt(0).toUpperCase() }}
                      </div>
                      <div>
                        <p class="font-bold text-slate-900 text-sm">{{ user.username }}</p>
                        <p class="text-xs text-slate-400 font-medium">{{ user.email }}</p>
                      </div>
                    </div>
                  </td>
                  <td class="px-8 py-5">
                    <span class="font-bold text-slate-700 bg-slate-100 px-2 py-1 rounded-lg text-xs">{{ user.rating }}</span>
                  </td>
                  <td class="px-8 py-5 text-xs text-slate-500 font-bold">
                    {{ formatDate(user.created_at) }}
                  </td>
                  <td class="px-8 py-5">
                    <div class="flex items-center gap-2">
                        <span
                        class="px-2.5 py-1 rounded-lg text-[10px] font-black uppercase tracking-wider shadow-sm"
                        :class="user.is_banned ? 'bg-red-50 text-red-600 border border-red-100' : 'bg-emerald-50 text-emerald-600 border border-emerald-100'"
                        >
                        {{ user.is_banned ? 'Banned' : 'Active' }}
                        </span>
                        <span v-if="user.is_admin" class="px-2.5 py-1 rounded-lg text-[10px] font-black uppercase tracking-wider bg-indigo-50 text-indigo-600 border border-indigo-100 shadow-sm">
                        Admin
                        </span>
                    </div>
                  </td>

                  <td class="px-8 py-5 text-right relative">
                    <button
                      @click="toggleMenu($event, user.id)"
                      class="px-4 py-2 bg-slate-100 text-slate-600 text-xs font-black rounded-xl hover:bg-slate-200 transition-colors"
                    >
                      Действия ▾
                    </button>

                    <div v-if="activeMenuId === user.id" class="absolute right-8 top-14 w-52 bg-white rounded-2xl shadow-2xl border border-slate-100 z-50 py-2 text-left animate-fade-in">
                      <button @click="openEditUser(user)" class="w-full text-left px-5 py-3 text-xs font-bold text-slate-700 hover:bg-slate-50 flex items-center gap-2">
                        <span>✏️</span> Изменить данные
                      </button>
                      <button @click="updateUserAction(user.id, { is_admin: !user.is_admin })" class="w-full text-left px-5 py-3 text-xs font-bold text-indigo-600 hover:bg-indigo-50 flex items-center gap-2">
                         <span>{{ user.is_admin ? '⭐' : '👑' }}</span> {{ user.is_admin ? 'Снять админа' : 'Сделать админом' }}
                      </button>
                      <button @click="updateUserAction(user.id, { is_banned: !user.is_banned })" class="w-full text-left px-5 py-3 text-xs font-bold text-amber-600 hover:bg-amber-50 flex items-center gap-2">
                         <span>{{ user.is_banned ? '🔓' : '🚫' }}</span> {{ user.is_banned ? 'Разблокировать' : 'Заблокировать' }}
                      </button>
                      <hr class="my-1 border-slate-50">
                      <button @click="deleteUser(user)" class="w-full text-left px-5 py-3 text-xs font-bold text-red-500 hover:bg-red-50 flex items-center gap-2">
                         <span>🗑️</span> Удалить
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="!loading && users.length === 0" class="p-12 text-center">
            <div class="text-4xl mb-2">🔍</div>
            <p class="text-slate-900 font-bold">Пользователи не найдены</p>
            <p class="text-slate-400 text-sm">Список пуст или произошла ошибка загрузки</p>
          </div>
        </div>
      </div>

      <div v-if="currentTab === 'tasks'" class="space-y-6 animate-fade-in">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <h1 class="text-3xl font-black text-slate-900">Управление задачами</h1>

          <div class="flex gap-2">
            <input type="file" ref="fileInput" class="hidden" accept=".json" @change="handleImport">

            <button @click="triggerImport" class="px-4 py-2 bg-white border border-slate-200 text-slate-600 rounded-xl text-sm font-bold hover:bg-slate-50 transition-colors shadow-sm flex items-center gap-2">
              📥 Импорт
            </button>
            <button @click="exportTasks" class="px-4 py-2 bg-white border border-slate-200 text-slate-600 rounded-xl text-sm font-bold hover:bg-slate-50 transition-colors shadow-sm flex items-center gap-2">
              📤 Экспорт
            </button>
            <button @click="openCreateModal" class="px-6 py-2 bg-indigo-600 text-white rounded-xl text-sm font-bold hover:bg-indigo-700 shadow-lg shadow-indigo-100 transition-all flex items-center gap-2">
              <span>+</span> Создать
            </button>
          </div>
        </div>

        <div class="bg-white rounded-[2rem] shadow-xl shadow-slate-200/40 border border-slate-100 overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="bg-slate-50/50 border-b border-slate-100 text-[10px] uppercase text-slate-400 font-black tracking-widest cursor-pointer select-none">
                  <th @click="sortBy('id')" class="px-8 py-5 hover:bg-slate-100 transition-colors">
                    ID <span v-if="sortKey === 'id'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                  </th>
                  <th @click="sortBy('title')" class="px-8 py-5 hover:bg-slate-100 transition-colors">
                    Задача <span v-if="sortKey === 'title'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                  </th>
                  <th @click="sortBy('subject')" class="px-8 py-5 hover:bg-slate-100 transition-colors">
                    Предмет <span v-if="sortKey === 'subject'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                  </th>
                  <th @click="sortBy('difficulty')" class="px-8 py-5 hover:bg-slate-100 transition-colors">
                    Сложность <span v-if="sortKey === 'difficulty'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                  </th>
                  <th class="px-8 py-5">Ответ</th>
                  <th class="px-8 py-5 text-right">Действие</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-50">
                <tr v-for="task in sortedTasks" :key="task.id" class="hover:bg-slate-50 group transition-colors">
                  <td class="px-8 py-5 text-xs font-mono text-slate-300 font-bold">#{{ task.id }}</td>
                  <td class="px-8 py-5">
                    <p class="font-bold text-slate-900 text-sm line-clamp-1">{{ task.title }}</p>
                    <p class="text-xs text-slate-400 font-medium line-clamp-1 mt-0.5">{{ task.description.substring(0, 60) }}...</p>
                  </td>
                  <td class="px-8 py-5">
                    <span class="px-2.5 py-1 bg-slate-100 rounded-lg text-xs font-bold text-slate-600 border border-slate-200">{{ task.subject }}</span>
                  </td>
                  <td class="px-8 py-5">
                    <span
                      class="text-[10px] font-black uppercase tracking-widest px-2.5 py-1 rounded-lg border shadow-sm"
                      :class="{
                        'text-green-600 border-green-100 bg-green-50': task.difficulty === 'Easy',
                        'text-amber-600 border-amber-100 bg-amber-50': task.difficulty === 'Medium',
                        'text-red-600 border-red-100 bg-red-50': task.difficulty === 'Hard',
                      }"
                    >
                      {{ task.difficulty }}
                    </span>
                  </td>
                  <td class="px-8 py-5">
                    <code class="bg-slate-100 px-2 py-1 rounded text-xs text-slate-500 font-mono font-bold hidden group-hover:inline-block border border-slate-200">
                      {{ task.correct_answer || '***' }}
                    </code>
                    <span class="text-xs text-slate-300 font-black tracking-widest group-hover:hidden">***</span>
                  </td>
                  <td class="px-8 py-5 text-right flex justify-end gap-2">
                    <button
                      @click="openEditModal(task)"
                      class="w-10 h-10 flex items-center justify-center bg-white border border-slate-100 text-slate-400 rounded-xl hover:bg-indigo-50 hover:text-indigo-600 transition-all shadow-sm active:scale-90"
                      title="Редактировать"
                    >
                      <span class="text-sm">✏️</span>
                    </button>
                    <button
                      @click="deleteTask(task.id)"
                      class="w-10 h-10 flex items-center justify-center bg-white border border-slate-100 text-red-400 rounded-xl hover:bg-red-50 hover:text-red-600 hover:border-red-100 transition-all shadow-sm active:scale-90"
                      title="Удалить задачу"
                    >
                      <span class="text-lg">🗑️</span>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="!loading && tasks.length === 0" class="p-12 text-center text-slate-400 font-medium">
            Задач пока нет. Создайте первую!
          </div>
        </div>
      </div>

    </main>

    <div v-if="showTaskModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
      <div class="bg-white rounded-[2rem] w-full max-w-2xl shadow-2xl p-8 space-y-6 animate-fade-in-up border border-slate-100 max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center border-b border-slate-50 pb-4">
          <h2 class="text-2xl font-black text-slate-900">{{ isEditMode ? 'Редактировать задачу' : 'Новая задача' }}</h2>
          <button @click="showTaskModal = false" class="w-10 h-10 rounded-xl bg-slate-50 flex items-center justify-center text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors">✕</button>
        </div>

        <form @submit.prevent="saveTask" class="space-y-5">
          <div class="grid grid-cols-2 gap-5">
            <div class="space-y-1.5">
              <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Предмет</label>
              <select v-model="taskForm.subject" required class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3.5 font-bold text-slate-700 outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all">
                <option v-for="s in subjectOptions" :key="s" :value="s">{{ s }}</option>
              </select>
            </div>
            <div class="space-y-1.5">
              <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Сложность</label>
              <select v-model="taskForm.difficulty" required class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3.5 font-bold text-slate-700 outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all">
                <option v-for="d in difficultyOptions" :key="d" :value="d">{{ d }}</option>
              </select>
            </div>
          </div>

          <div class="space-y-1.5">
            <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Название</label>
            <input v-model="taskForm.title" required placeholder="Например: Сумма двух чисел" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3.5 font-bold text-slate-900 outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all" />
          </div>

          <div class="space-y-1.5">
            <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Теги (через запятую)</label>
            <input v-model="tagsInput" placeholder="Например: Арифметика, 5 класс" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3.5 font-bold text-slate-900 outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all" />
          </div>

          <div class="space-y-1.5">
            <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Подсказка</label>
            <textarea v-model="taskForm.hint" rows="2" placeholder="Необязательная подсказка для режима тренировки..." class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3.5 font-medium text-slate-700 outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all resize-none"></textarea>
          </div>

          <div class="space-y-1.5">
            <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Условие</label>
            <textarea v-model="taskForm.description" required rows="4" placeholder="Текст условия..." class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3.5 font-medium text-slate-900 outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all resize-none"></textarea>
          </div>

          <div class="space-y-1.5">
            <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Ответ</label>
            <input v-model="taskForm.correct_answer" required placeholder="Точное совпадение" class="w-full bg-green-50/50 border border-green-200 rounded-xl px-4 py-3.5 font-bold text-green-800 outline-none focus:ring-2 focus:ring-green-500 focus:bg-white transition-all" />
          </div>

          <div class="pt-4">
            <button type="submit" class="w-full py-4 bg-indigo-600 hover:bg-indigo-700 text-white font-black rounded-xl shadow-xl shadow-indigo-200 transition-all active:scale-[0.98]">
              {{ isEditMode ? 'Сохранить изменения' : 'Создать задачу' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showUserEditModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
      <div class="bg-white rounded-[2rem] w-full max-w-md shadow-2xl p-8 space-y-6 animate-fade-in-up">
        <h2 class="text-2xl font-black text-slate-900">Редактировать профиль</h2>
        <form @submit.prevent="updateUserAction(userEditForm.id, userEditForm, 'Данные сохранены')" class="space-y-4">
          <div>
            <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Имя пользователя</label>
            <input v-model="userEditForm.username" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 font-bold focus:ring-2 focus:ring-indigo-500 outline-none">
          </div>
          <div>
            <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Email</label>
            <input v-model="userEditForm.email" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 font-bold focus:ring-2 focus:ring-indigo-500 outline-none">
          </div>
          <div>
            <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Рейтинг ELO</label>
            <input v-model.number="userEditForm.rating" type="number" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 font-bold focus:ring-2 focus:ring-indigo-500 outline-none">
          </div>
          <div class="flex gap-3 pt-4">
            <button type="submit" class="flex-1 py-4 bg-indigo-600 text-white font-black rounded-xl hover:bg-indigo-700 transition-colors">Сохранить</button>
            <button @click="showUserEditModal = false" type="button" class="px-6 py-4 bg-slate-100 text-slate-500 font-black rounded-xl hover:bg-slate-200 transition-colors">Отмена</button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<style scoped>
.animate-fade-in { animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
.animate-fade-in-up { animation: fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1); }

@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.99); }
  to { opacity: 1; transform: scale(1); }
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
