<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

// --- СОСТОЯНИЕ ---
const currentTab = ref('dashboard') // 'dashboard' | 'users' | 'tasks'
const accessDenied = ref(false)
const loading = ref(false)
const showTaskModal = ref(false)
const fileInput = ref(null)

// --- НОВОЕ ДЛЯ РЕДАКТИРОВАНИЯ ---
const isEditMode = ref(false)
const currentEditId = ref(null)

// Данные
const stats = ref({
  total_users: 0,
  total_tasks: 0,
  average_rating: 0,
  new_users_24h: 0,
  most_popular_subject: 'Загрузка...'
})
const users = ref([])
const tasks = ref([])

// Форма задачи
const taskForm = ref({
  title: '',
  description: '',
  subject: '',
  theme: '',
  difficulty: 'Easy',
  correct_answer: ''
})

const difficultyOptions = ['Easy', 'Medium', 'Hard']
const subjectOptions = ['Математика', 'Информатика', 'Физика', 'Алгоритмы']

// --- API ---
const getAuthHeader = () => {
  return { headers: { Authorization: `Bearer ${localStorage.getItem('user-token')}` } }
}

const handleApiError = (err) => {
  if (err.response && err.response.status === 403) {
    accessDenied.value = true
  } else {
    console.error('API Error:', err)
    alert('Ошибка: ' + (err.response?.data?.detail || err.message))
  }
}

// 1. Статистика
const fetchStats = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/admin/stats', getAuthHeader())
    stats.value = response.data
    accessDenied.value = false
  } catch (err) { handleApiError(err) }
}

// 2. Пользователи
const fetchUsers = async () => {
  if (accessDenied.value) return
  loading.value = true
  try {
    const response = await axios.get('http://127.0.0.1:8000/admin/users?limit=50', getAuthHeader())
    users.value = response.data
  } catch (err) { handleApiError(err) }
  finally { loading.value = false }
}

const toggleBan = async (user) => {
  if (!confirm(`Вы уверены, что хотите ${user.is_banned ? 'разбанить' : 'забанить'} ${user.username}?`)) return
  try {
    await axios.patch(`http://127.0.0.1:8000/admin/users/${user.id}/ban`, {}, getAuthHeader())
    user.is_banned = !user.is_banned
  } catch (err) { alert('Ошибка: ' + (err.response?.data?.detail || err.message)) }
}

/**
 * НОВОЕ: Смена роли пользователя (Админ/Юзер)
 * Вызывает эндпоинт PATCH /admin/users/{id}/role
 */
const changeRole = async (user) => {
  const action = user.is_admin ? 'снять права администратора с' : 'сделать администратором'
  if (!confirm(`Вы уверены, что хотите ${action} ${user.username}?`)) return
  try {
    await axios.patch(`http://127.0.0.1:8000/admin/users/${user.id}/role`, {}, getAuthHeader())
    user.is_admin = !user.is_admin
  } catch (err) { handleApiError(err) }
}

// 3. Задачи
const fetchTasks = async () => {
  if (accessDenied.value) return
  loading.value = true
  try {
    const response = await axios.get('http://127.0.0.1:8000/tasks/', getAuthHeader())
    tasks.value = response.data
  } catch (err) { handleApiError(err) }
  finally { loading.value = false }
}

// Функции открытия модалки
const openCreateModal = () => {
  isEditMode.value = false
  currentEditId.value = null
  taskForm.value = { title: '', description: '', subject: 'Математика', theme: '', difficulty: 'Easy', correct_answer: '' }
  showTaskModal.value = true
}

// ИЗМЕНЕНО: Запрос теперь идет на защищенный админский эндпоинт для получения ответа
const openEditModal = async (task) => {
  isEditMode.value = true
  currentEditId.value = task.id

  // 1. Предварительно заполняем тем, что есть в таблице (чтобы интерфейс не "моргал")
  taskForm.value = { ...task }
  showTaskModal.value = true

  // 2. Делаем безопасный запрос к админке за полными данными (включая correct_answer)
  try {
    const { data } = await axios.get(`http://127.0.0.1:8000/admin/tasks/${task.id}`, getAuthHeader())

    // Обновляем форму полными данными, включая ответ
    taskForm.value = {
      title: data.title,
      description: data.description,
      subject: data.subject,
      theme: data.theme,
      difficulty: data.difficulty,
      correct_answer: data.correct_answer // Теперь это поле точно заполнится
    }
  } catch (e) {
    console.error('Не удалось загрузить детали задачи', e)
    if (e.response?.status === 403) {
        alert('У вас нет прав на просмотр ответа')
    }
  }
}

// Сохранение (Создание или Обновление)
const saveTask = async () => {
  try {
    if (isEditMode.value) {
      // PATCH запрос для обновления
      await axios.patch(`http://127.0.0.1:8000/tasks/${currentEditId.value}`, taskForm.value, getAuthHeader())
      alert('Задача успешно обновлена!')
    } else {
      // POST запрос для создания
      await axios.post('http://127.0.0.1:8000/tasks/', taskForm.value, getAuthHeader())
      alert('Задача успешно создана!')
    }
    showTaskModal.value = false
    fetchTasks()
    fetchStats()
  } catch (err) { handleApiError(err) }
}

// Метод удаления задачи
const deleteTask = async (taskId) => {
  if (!confirm(`Вы уверены, что хотите безвозвратно удалить задачу #${taskId}?`)) return
  try {
    await axios.delete(`http://127.0.0.1:8000/tasks/${taskId}`, getAuthHeader())
    // Обновляем локальный список
    tasks.value = tasks.value.filter(t => t.id !== taskId)
    // Обновляем общую статистику
    fetchStats()
  } catch (err) { handleApiError(err) }
}

const exportTasks = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/tasks/export', {
      ...getAuthHeader(),
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `tasks_export_${new Date().toISOString().slice(0,10)}.json`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (err) { handleApiError(err) }
}

const triggerImport = () => fileInput.value.click()

const handleImport = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)
  try {
    loading.value = true
    const response = await axios.post('http://127.0.0.1:8000/tasks/import', formData, {
      headers: { ...getAuthHeader().headers, 'Content-Type': 'multipart/form-data' }
    })
    alert(`Импорт завершен!\nСоздано: ${response.data.created}\nОбновлено: ${response.data.updated}`)
    fetchTasks()
    fetchStats()
  } catch (err) { handleApiError(err) }
  finally {
    loading.value = false
    event.target.value = ''
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('ru-RU', {
    day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
  })
}

onMounted(() => {
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
                  <td class="px-8 py-5 text-right flex justify-end gap-2">
                    <button
                      @click="changeRole(user)"
                      class="text-xs font-bold px-4 py-2 rounded-xl transition-all active:scale-95 shadow-sm border"
                      :class="user.is_admin ? 'bg-indigo-50 text-indigo-600 border-indigo-100 hover:bg-indigo-100' : 'bg-white text-slate-600 border-slate-100 hover:bg-slate-50'"
                    >
                      {{ user.is_admin ? 'Снять админа' : 'Сделать админом' }}
                    </button>
                    <button
                      @click="toggleBan(user)"
                      class="text-xs font-bold px-4 py-2 rounded-xl transition-all active:scale-95 shadow-sm border"
                      :class="user.is_banned ? 'bg-emerald-50 text-emerald-600 border-emerald-100 hover:bg-emerald-100' : 'bg-white text-red-500 border-slate-100 hover:bg-red-50 hover:border-red-100'"
                    >
                      {{ user.is_banned ? 'Разблокировать' : 'Заблокировать' }}
                    </button>
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
                <tr class="bg-slate-50/50 border-b border-slate-100 text-[10px] uppercase text-slate-400 font-black tracking-widest">
                  <th class="px-8 py-5">ID</th>
                  <th class="px-8 py-5">Задача</th>
                  <th class="px-8 py-5">Предмет</th>
                  <th class="px-8 py-5">Сложность</th>
                  <th class="px-8 py-5 text-right">Действие</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-50">
                <tr v-for="task in tasks" :key="task.id" class="hover:bg-slate-50 group transition-colors">
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
      <div class="bg-white rounded-[2rem] w-full max-w-2xl shadow-2xl p-8 space-y-6 animate-fade-in-up border border-slate-100">
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
            <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Тема</label>
            <input v-model="taskForm.theme" required placeholder="Например: Арифметика" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3.5 font-bold text-slate-900 outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all" />
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
