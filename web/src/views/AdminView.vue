<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useConstantsStore } from '@/pinia/ConstantsStore.js' // 1. Импорт стора

const constants = useConstantsStore() // 2. Инициализация

// --- СОСТОЯНИЕ ИНТЕРФЕЙСА ---
const currentTab = ref('dashboard')
const accessDenied = ref(false)
const loading = ref(false)
const showTaskModal = ref(false)
const fileInput = ref(null)
const isSidebarCollapsed = ref(false)

// --- УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ ---
const activeMenuId = ref(null)
const showUserEditModal = ref(false)
const userEditForm = ref({ id: null, username: '', email: '', rating: 0 })

// --- РЕДАКТИРОВАНИЕ ЗАДАЧ ---
const isEditMode = ref(false)
const currentEditId = ref(null)
const tagsInput = ref('')

// --- СОРТИРОВКА ЗАДАЧ ---
const sortKey = ref('id')
const sortOrder = ref('asc')

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
const logs = ref([])

const getBadgeClass = (action) => {
  const act = action.toLowerCase()
  if (act.includes('delete') || act.includes('ban')) return 'hard'
  if (act.includes('update') || act.includes('edit')) return 'medium'
  if (act.includes('create') || act.includes('add')) return 'easy'
  return ''
}

const taskForm = ref({
  title: '',
  description: '',
  subject: '',
  tags: [],
  difficulty: '',
  correct_answer: '',
  hint: ''
})

// --- ВЫЧИСЛЯЕМЫЕ СВОЙСТВА (СОРТИРОВКА) ---
const sortedTasks = computed(() => {
  return [...tasks.value].sort((a, b) => {
    let modifier = sortOrder.value === 'asc' ? 1 : -1

    let valA = a[sortKey.value]
    let valB = b[sortKey.value]

    // Веса для сложности (используем ключи UPPERCASE)
    if (sortKey.value === 'difficulty') {
      const weights = { 'EASY': 1, 'MEDIUM': 2, 'HARD': 3 }
      valA = weights[valA] || 0
      valB = weights[valB] || 0
    }

    if (typeof valA === 'number' && typeof valB === 'number') {
      return (valA - valB) * modifier
    }

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
    alert('Ошибка: ' + (err.response?.data?.detail || err.message))
  }
}

const formatLogDate = (dateString) => {
  if (!dateString) return '-'
  const dateValue = dateString.endsWith('Z') ? dateString : dateString + 'Z'
  return new Date(dateValue).toLocaleString('ru-RU', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit', second: '2-digit'
  })
}

// --- ЗАГРУЗКА ДАННЫХ ---
const fetchStats = async () => {
  try {
    const response = await axios.get('/admin/stats', getAuthHeader())
    stats.value = response.data
    accessDenied.value = false
  } catch (err) { handleApiError(err) }
}

const fetchUsers = async () => {
  if (accessDenied.value) return
  loading.value = true
  try {
    const response = await axios.get('/admin/users?limit=50', getAuthHeader())
    users.value = response.data
  } catch (err) { handleApiError(err) }
  finally { loading.value = false }
}

const fetchTasks = async () => {
  if (accessDenied.value) return
  loading.value = true
  try {
    const response = await axios.get('/tasks/', getAuthHeader())
    tasks.value = response.data
  } catch (err) { handleApiError(err) }
  finally { loading.value = false }
}

const fetchLogs = async () => {
  if (accessDenied.value) return
  loading.value = true
  try {
    const response = await axios.get('/admin/logs?limit=50', getAuthHeader())
    logs.value = response.data
  } catch (err) { handleApiError(err) }
  finally { loading.value = false }
}

// --- УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ ---
const toggleMenu = (event, id) => {
  event.stopPropagation()
  activeMenuId.value = activeMenuId.value === id ? null : id
}

const openEditUser = (user) => {
  userEditForm.value = { ...user }
  showUserEditModal.value = true
  activeMenuId.value = null
}

const updateUserAction = async (userId, data, successMessage = null) => {
  try {
    await axios.patch(`/admin/users/${userId}`, data, getAuthHeader())
    if (successMessage) alert(successMessage)
    fetchUsers()
    showUserEditModal.value = false
  } catch (err) { handleApiError(err) }
}

const deleteUser = async (user) => {
  if (!confirm(`Вы уверены, что хотите безвозвратно удалить пользователя ${user.username}?`)) return
  try {
    await axios.delete(`/admin/users/${user.id}`, getAuthHeader())
    users.value = users.value.filter(u => u.id !== user.id)
    fetchStats()
  } catch (err) { handleApiError(err) }
}

// --- УПРАВЛЕНИЕ ЗАДАЧАМИ ---

const openCreateModal = () => {
  isEditMode.value = false
  currentEditId.value = null
  tagsInput.value = ''

  // Инициализация дефолтными значениями из стора (берем первый доступный элемент или запасной вариант)
  taskForm.value = {
    title: '',
    description: '',
    subject: constants.subjects[0]?.key || '', 
    tags: [],
    difficulty: constants.difficulty[0]?.key || 'EASY',
    correct_answer: '',
    hint: ''
  }
  showTaskModal.value = true
}

const openEditModal = async (task) => {
  isEditMode.value = true
  currentEditId.value = task.id
  taskForm.value = { ...task }
  tagsInput.value = (task.tags && Array.isArray(task.tags)) ? task.tags.join(', ') : ''
  showTaskModal.value = true
  try {
    const { data } = await axios.get(`/admin/tasks/${task.id}`, getAuthHeader())
    taskForm.value = { ...data }
    tagsInput.value = (data.tags && Array.isArray(data.tags)) ? data.tags.join(', ') : ''
  } catch (e) { handleApiError(e) }
}

const saveTask = async () => {
  try {
    taskForm.value.tags = tagsInput.value
      .split(',')
      .map(tag => tag.trim())
      .filter(tag => tag.length > 0)

    const finalUrl = isEditMode.value
       ? `/admin/tasks/${currentEditId.value}`
       : '/admin/tasks/create'

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
    await axios.delete(`/admin/tasks/${taskId}`, getAuthHeader())
    tasks.value = tasks.value.filter(t => t.id !== taskId)
    fetchStats()
  } catch (err) { handleApiError(err) }
}

const exportTasks = async () => {
  try {
    const response = await axios.get('/admin/tasks/export', { ...getAuthHeader(), responseType: 'blob' })
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
    const response = await axios.post('/admin/tasks/import', formData, {
      headers: { ...getAuthHeader().headers, 'Content-Type': 'multipart/form-data' }
    })
    alert(`Импорт завершен!\nСоздано: ${response.data.created}\nОбновлено: ${response.data.updated}`)
    fetchTasks(); fetchStats()
  } catch (err) { handleApiError(err) }
  finally { loading.value = false; event.target.value = '' }
}

const toggleSidebar = () => { isSidebarCollapsed.value = !isSidebarCollapsed.value }

onMounted(() => {
  window.addEventListener('click', () => { activeMenuId.value = null })
  fetchStats()
  fetchUsers()
  // Если константы еще не загружены (например, прямой заход), подгружаем
  if (constants.subjects.length === 0) {
    constants.fetchConstants()
  }
})
</script>

<template>
  <div v-if="accessDenied" class="access-denied-container">
    <div class="access-denied-content">
      <div class="access-denied-icon"><span>🔒</span></div>
      <div class="access-denied-text">
        <h1>Доступ запрещен</h1>
        <p>У вас недостаточно прав для просмотра этой страницы.<br>Эта зона только для администраторов.</p>
      </div>
      <div class="access-denied-actions">
        <router-link to="/" class="home-btn">На главную</router-link>
      </div>
      <p class="error-code">ERROR CODE: 403 FORBIDDEN</p>
    </div>
  </div>

  <div v-else class="admin-container">
    <div class="mobile-menu-btn" @click="toggleSidebar">
      <span class="burger-line"></span>
      <span class="burger-line"></span>
      <span class="burger-line"></span>
    </div>

    <div class="mobile-overlay" v-if="isSidebarCollapsed" @click="toggleSidebar"></div>

    <aside class="admin-sidebar" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
      <div class="sidebar-header">
        <div class="sidebar-logo">A</div>
        <span class="sidebar-title">Admin Panel</span>
        <button class="sidebar-close" @click="toggleSidebar">✕</button>
      </div>

      <nav class="sidebar-nav">
        <button @click="currentTab = 'dashboard'; isSidebarCollapsed = false" class="nav-btn" :class="{ active: currentTab === 'dashboard' }">
          <span class="nav-icon">📊</span> <span class="nav-text">Дашборд</span>
        </button>
        <button @click="currentTab = 'users'; isSidebarCollapsed = false" class="nav-btn" :class="{ active: currentTab === 'users' }">
          <span class="nav-icon">👥</span> <span class="nav-text">Пользователи</span>
        </button>
        <button @click="currentTab = 'tasks'; fetchTasks(); isSidebarCollapsed = false" class="nav-btn" :class="{ active: currentTab === 'tasks' }">
          <span class="nav-icon">📝</span> <span class="nav-text">Задачи</span>
        </button>
        <button @click="currentTab = 'logs'; fetchLogs(); isSidebarCollapsed = false" class="nav-btn" :class="{ active: currentTab === 'logs' }">
          <span class="nav-icon">🛡️</span> <span class="nav-text">Логи</span>
        </button>
      </nav>

      <div class="sidebar-footer">
        <router-link to="/" class="back-to-site" @click="isSidebarCollapsed = false">← Вернуться на сайт</router-link>
      </div>
    </aside>

    <main class="admin-main">
      <div v-if="currentTab === 'dashboard'" class="dashboard-tab">
        <div class="dashboard-header">
          <h1>Обзор системы</h1>
          <span class="live-badge">Live Updates</span>
        </div>
        <div class="stats-container">
          <div class="stat-card">
            <div class="stat-header"><div class="stat-icon users-icon">👥</div><span class="stat-label">Всего</span></div>
            <p class="stat-value">{{ stats.total_users }}</p><p class="stat-description">пользователей</p>
          </div>
          <div class="stat-card">
            <div class="stat-header"><div class="stat-icon growth-icon">🔥</div><span class="stat-label">Динамика</span></div>
            <p class="stat-value">+{{ stats.new_users_24h }}</p><p class="stat-description">за 24 часа</p>
          </div>
          <div class="stat-card">
            <div class="stat-header"><div class="stat-icon skill-icon">⭐</div><span class="stat-label">Скилл</span></div>
            <p class="stat-value">{{ stats.average_rating }}</p><p class="stat-description">средний ELO</p>
          </div>
          <div class="stat-card">
            <div class="stat-header"><div class="stat-icon trends-icon">📚</div><span class="stat-label">Тренды</span></div>
            <p class="stat-value">{{ stats.most_popular_subject }}</p><p class="stat-description">выбор игроков</p>
          </div>
        </div>
      </div>

      <div v-if="currentTab === 'users'" class="users-tab">
        <div class="tab-header">
          <h1>Управление пользователями</h1>
          <button @click="fetchUsers" class="refresh-btn">🔄 Обновить</button>
        </div>
        <div class="table-wrapper">
          <div class="responsive-table">
            <table class="users-table">
              <thead>
                <tr class="table-head">
                  <th>ID</th><th class="user-column">Пользователь</th><th>Рейтинг</th><th class="date-column">Дата регистрации</th><th class="status-column">Роль / Статус</th><th class="actions-header">Действия</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in users" :key="user.id" class="table-row">
                  <td class="user-id">#{{ user.id }}</td>
                  <td class="user-cell">
                    <div class="user-avatar">{{ user.username.charAt(0).toUpperCase() }}</div>
                    <div class="user-details"><p class="user-name">{{ user.username }}</p><p class="user-email">{{ user.email }}</p></div>
                  </td>
                  <td class="rating-cell"><span class="rating-badge">{{ user.rating }}</span></td>
                  <td class="register-date">{{ formatDate(user.created_at) }}</td>
                  <td class="status-cell">
                    <div class="status-container">
                      <span class="status-badge" :class="{ banned: user.is_banned }">{{ user.is_banned ? 'Banned' : 'Active' }}</span>
                      <span v-if="user.is_admin" class="admin-badge">Admin</span>
                    </div>
                  </td>
                  <td class="actions-cell">
                    <button @click="toggleMenu($event, user.id)" class="actions-btn">Действия ▾</button>
                    <div v-if="activeMenuId === user.id" class="actions-dropdown">
                      <button @click="openEditUser(user)" class="dropdown-item"><span class="item-icon">✏️</span> <span>Изменить данные</span></button>
                      <button @click="updateUserAction(user.id, { is_admin: !user.is_admin })" class="dropdown-item"><span class="item-icon">{{ user.is_admin ? '⭐' : '👑' }}</span> <span>{{ user.is_admin ? 'Снять админа' : 'Сделать админом' }}</span></button>
                      <button @click="updateUserAction(user.id, { is_banned: !user.is_banned })" class="dropdown-item"><span class="item-icon">{{ user.is_banned ? '🔓' : '🚫' }}</span> <span>{{ user.is_banned ? 'Разблокировать' : 'Заблокировать' }}</span></button>
                      <div class="dropdown-divider"></div>
                      <button @click="deleteUser(user)" class="dropdown-item delete-item"><span class="item-icon">🗑️</span> <span>Удалить</span></button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-if="!loading && users.length === 0" class="empty-table"><div class="empty-icon">🔍</div><p class="empty-title">Пользователи не найдены</p></div>
        </div>
      </div>

      <div v-if="currentTab === 'tasks'" class="tasks-tab">
        <div class="tab-header tasks-tab-header">
          <h1>Управление задачами</h1>
          <div class="tasks-actions">
            <input type="file" ref="fileInput" class="file-upload" accept=".json" @change="handleImport">
            <button @click="triggerImport" class="import-btn" title="Импорт задач">📥</button>
            <button @click="exportTasks" class="export-btn" title="Экспорт задач">📤</button>
            <button @click="openCreateModal" class="create-btn"><span class="plus-icon">+</span> Создать</button>
          </div>
        </div>

        <div class="table-wrapper">
          <div class="responsive-table">
            <table class="tasks-table">
              <thead>
                <tr class="table-head">
                  <th @click="sortBy('id')" class="sortable-column">ID <span v-if="sortKey === 'id'" class="sort-indicator">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span></th>
                  <th @click="sortBy('title')" class="sortable-column task-column">Задача <span v-if="sortKey === 'title'" class="sort-indicator">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span></th>
                  <th @click="sortBy('subject')" class="sortable-column">Предмет <span v-if="sortKey === 'subject'" class="sort-indicator">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span></th>
                  <th @click="sortBy('difficulty')" class="sortable-column">Сложность <span v-if="sortKey === 'difficulty'" class="sort-indicator">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span></th>
                  <th class="answer-column">Ответ</th>
                  <th class="actions-header">Действие</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="task in sortedTasks" :key="task.id" class="table-row task-row">
                  <td class="task-id">#{{ task.id }}</td>
                  <td class="task-cell"><p class="task-title">{{ task.title }}</p><p class="task-description">{{ task.description.substring(0, 60) }}...</p></td>
                  <td>
                    <span class="subject-badge">{{ constants.getSubjectLabel(task.subject) }}</span>
                  </td>
                  <td>
                    <span class="difficulty-badge" :class="task.difficulty.toLowerCase()">
                      {{ constants.getDifficultyLabel(task.difficulty) }}
                    </span>
                  </td>
                  <td class="answer-cell"><code class="answer-code">{{ task.correct_answer || '***' }}</code><span class="answer-placeholder">***</span></td>
                  <td class="task-actions-cell">
                    <button @click="openEditModal(task)" class="action-icon edit-icon" title="Редактировать"><span>✏️</span></button>
                    <button @click="deleteTask(task.id)" class="action-icon delete-icon" title="Удалить задачу"><span>🗑️</span></button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-if="!loading && tasks.length === 0" class="empty-tasks">Задач пока нет. Создайте первую!</div>
        </div>
      </div>
    </main>

    <div v-if="showTaskModal" class="modal-overlay">
      <div class="task-modal">
        <div class="modal-header">
          <h2>{{ isEditMode ? 'Редактировать задачу' : 'Новая задача' }}</h2>
          <button @click="showTaskModal = false" class="close-modal">✕</button>
        </div>

        <form @submit.prevent="saveTask" class="modal-form">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Предмет</label>
              <select v-model="taskForm.subject" required class="form-select">
                <option v-for="s in constants.subjects" :key="s.key" :value="s.key">
                  {{ s.label }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Сложность</label>
              <select v-model="taskForm.difficulty" required class="form-select">
                <option v-for="d in constants.difficulty" :key="d.key" :value="d.key">
                  {{ d.label }}
                </option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Название</label>
            <input v-model="taskForm.title" required placeholder="Например: Сумма двух чисел" class="form-input" />
          </div>

          <div class="form-group">
            <label class="form-label">Теги (через запятую)</label>
            <input v-model="tagsInput" placeholder="Например: Арифметика, 5 класс" class="form-input" />
          </div>

          <div class="form-group">
            <label class="form-label">Подсказка</label>
            <textarea v-model="taskForm.hint" rows="2" placeholder="Необязательная подсказка..." class="form-textarea"></textarea>
          </div>

          <div class="form-group">
            <label class="form-label">Условие</label>
            <textarea v-model="taskForm.description" required rows="4" placeholder="Текст условия..." class="form-textarea"></textarea>
          </div>

          <div class="form-group">
            <label class="form-label">Ответ</label>
            <input v-model="taskForm.correct_answer" required placeholder="Точное совпадение" class="form-input answer-field" />
          </div>

          <div class="form-submit">
            <button type="submit" class="submit-btn">{{ isEditMode ? 'Сохранить изменения' : 'Создать задачу' }}</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showUserEditModal" class="modal-overlay">
      <div class="user-modal">
        <div class="modal-header"><h2>Редактировать профиль</h2><button @click="showUserEditModal = false" class="close-modal">✕</button></div>
        <form @submit.prevent="updateUserAction(userEditForm.id, userEditForm, 'Данные сохранены')" class="modal-form">
          <div class="form-group"><label class="form-label">Имя пользователя</label><input v-model="userEditForm.username" class="form-input"></div>
          <div class="form-group"><label class="form-label">Email</label><input v-model="userEditForm.email" class="form-input"></div>
          <div class="form-group"><label class="form-label">Рейтинг ELO</label><input v-model.number="userEditForm.rating" type="number" class="form-input"></div>
          <div class="form-actions"><button type="submit" class="save-btn">Сохранить</button><button @click="showUserEditModal = false" type="button" class="cancel-btn">Отмена</button></div>
        </form>
      </div>
    </div>

    <div v-if="currentTab === 'logs'" class="logs-tab">
      <div class="tab-header"><h1>Аудит действий</h1><button @click="fetchLogs" class="refresh-btn">🔄 Обновить</button></div>
      <div class="table-wrapper">
        <div class="responsive-table">
          <table class="users-table">
            <thead><tr class="table-head"><th>ID</th><th>Время</th><th>Администратор</th><th>Действие</th><th>Цель</th><th style="width: 40%">Детали</th></tr></thead>
            <tbody>
            <tr v-for="log in logs" :key="log.id" class="table-row">
              <td class="user-id">#{{ log.id }}</td>
              <td class="register-date">{{ formatLogDate(log.created_at) }}</td>
              <td class="user-cell">
                <div class="user-avatar" :class="{'admin-badge-bg': true}">{{ log.admin_username ? log.admin_username.charAt(0).toUpperCase() : '?' }}</div>
                <div class="user-details"><p class="user-name">{{ log.admin_username || 'Неизвестно' }}</p><p class="user-email">Admin ID: {{ log.admin_id }}</p></div>
              </td>
              <td><span class="difficulty-badge" :class="getBadgeClass(log.action)">{{ log.action }}</span></td>
              <td class="user-id">{{ log.target_id ? '#' + log.target_id : '-' }}</td>
              <td class="task-cell" style="max-width: 300px;"><p class="task-description" :title="log.details">{{ log.details }}</p></td>
            </tr>
            </tbody>
          </table>
        </div>
        <div v-if="!loading && logs.length === 0" class="empty-table"><div class="empty-icon">📝</div><p class="empty-title">Логов пока нет</p></div>
      </div>
    </div>
  </div>
</template>
<style scoped>
/* ==================== БАЗОВЫЕ СТИЛИ ==================== */

/* Access Denied Page */
.access-denied-container {
  min-height: 100vh;
  background-color: #f8fafc;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 16px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
.access-denied-content {
  max-width: 448px;
  width: 100%;
  text-align: center;
}
.access-denied-icon {
  width: 80px;
  height: 80px;
  background-color: #fee2e2;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  box-shadow: 0 10px 15px -3px rgba(254, 202, 202, 0.5);
}
.access-denied-icon span {
  font-size: 40px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.access-denied-text h1 {
  font-size: 28px;
  font-weight: 900;
  color: #0f172a;
  letter-spacing: -0.025em;
  margin-bottom: 12px;
  line-height: 1.2;
}
.access-denied-text p {
  color: #64748b;
  font-weight: 500;
  font-size: 16px;
  line-height: 1.5;
  margin-bottom: 24px;
}
.access-denied-actions {
  display: flex;
  flex-direction: column;
  gap: 16px;
  justify-content: center;
  padding-top: 16px;
}
.home-btn {
  padding: 14px 28px;
  background-color: #0f172a;
  color: white;
  font-weight: 700;
  border-radius: 12px;
  text-decoration: none;
  box-shadow: 0 8px 12px -3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
  border: none;
  cursor: pointer;
  display: inline-block;
  font-size: 14px;
}
.home-btn:hover {
  background-color: #1e293b;
}
.home-btn:active {
  transform: scale(0.98);
}
.error-code {
  font-size: 11px;
  color: #94a3b8;
  font-family: monospace;
  margin-top: 24px;
}

/* Admin Layout */
.admin-container {
  min-height: 100vh;
  background-color: #f8fafc;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  position: relative;
}

/* Мобильное меню */
.mobile-menu-btn {
  position: fixed;
  top: 10px;
  left: 16px;
  z-index: 100;
  width: 40px;
  height: 40px;
  background: white;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  padding: 8px;
}

.burger-line {
  width: 20px;
  height: 2px;
  background-color: #4f46e5;
  border-radius: 1px;
  transition: all 0.3s ease;
}

.mobile-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 90;
}

.admin-sidebar {
  width: 256px;
  background-color: #0f172a;
  color: white;
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100%;
  z-index: 95;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  transform: translateX(-100%);
  transition: transform 0.3s ease;
}

.sidebar-collapsed {
  transform: translateX(0);
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #1e293b;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.sidebar-logo {
  width: 32px;
  height: 32px;
  background-color: #6366f1;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  box-shadow: 0 8px 12px -3px rgba(99, 102, 241, 0.2);
  font-size: 14px;
}
.sidebar-title {
  font-weight: 700;
  font-size: 16px;
  letter-spacing: -0.025em;
}
.sidebar-close {
  display: none;
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 20px;
  cursor: pointer;
  padding: 4px;
}

.sidebar-nav {
  flex: 1;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.nav-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 12px;
  transition: all 0.2s ease;
  font-weight: 500;
  font-size: 14px;
  border: none;
  cursor: pointer;
  background: none;
  color: #94a3b8;
}
.nav-btn.active {
  background-color: #4f46e5;
  color: white;
  box-shadow: 0 8px 12px -3px rgba(79, 70, 229, 0.25);
}
.nav-btn:not(.active):hover {
  background-color: #1e293b;
  color: white;
}
.nav-icon {
  font-size: 18px;
  transition: transform 0.2s ease;
  flex-shrink: 0;
}
.nav-btn:hover .nav-icon {
  transform: scale(1.1);
}
.sidebar-footer {
  padding: 16px;
  border-top: 1px solid #1e293b;
}
.back-to-site {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #94a3b8;
  font-size: 14px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  text-decoration: none;
  transition: color 0.2s ease;
  padding: 8px;
  border-radius: 8px;
}
.back-to-site:hover {
  color: white;
  background-color: #1e293b;
}
.admin-main {
  flex: 1;
  padding: 16px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow-x: hidden;
}

/* Dashboard Tab */
.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
}
.dashboard-header h1 {
  font-size: 24px;
  font-weight: 900;
  color: #0f172a;
  letter-spacing: -0.025em;
  line-height: 1.2;
}
.live-badge {
  font-size: 12px;
  font-weight: 700;
  color: #64748b;
  background-color: white;
  padding: 4px 10px;
  border-radius: 20px;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  border: 1px solid #f1f5f9;
}
.stats-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}
.stat-card {
  background-color: white;
  padding: 20px;
  border-radius: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border: 1px solid #f1f5f9;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px -2px rgba(0, 0, 0, 0.15);
}
.stat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}
.users-icon {
  background-color: #dbeafe;
  color: #2563eb;
}
.growth-icon {
  background-color: #dcfce7;
  color: #16a34a;
}
.skill-icon {
  background-color: #fef3c7;
  color: #d97706;
}
.trends-icon {
  background-color: #f3e8ff;
  color: #9333ea;
}
.stat-label {
  font-size: 12px;
  font-weight: 900;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}
.stat-value {
  font-size: 14px;
  font-weight: 900;
  color: #0f172a;
  line-height: 1.2;
}
.stat-description {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
  margin-top: 4px;
}

/* Common Tab Styles */
.tab-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}
.tab-header h1 {
  font-size: 22px;
  font-weight: 900;
  color: #0f172a;
  line-height: 1.2;
}
.refresh-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background-color: white;
  border: 1px solid #e2e8f0;
  color: #475569;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  white-space: nowrap;
}
.refresh-btn:hover {
  background-color: #f8fafc;
}
.table-wrapper {
  background-color: white;
  border-radius: 20px;
  box-shadow: 0 10px 15px -3px rgba(148, 163, 184, 0.2);
  border: 1px solid #f1f5f9;
  overflow: auto;
  max-width: 100%;
}

/* Users Table */
.responsive-table {
  overflow-x: auto;
  max-width: 100%;
}
.users-table {
  width: 100%;
  min-width: 800px;
  text-align: left;
  border-collapse: collapse;
}
.table-head {
  background-color: rgba(248, 250, 252, 0.5);
  border-bottom: 1px solid #f1f5f9;
  font-size: 10px;
  text-transform: uppercase;
  color: #94a3b8;
  font-weight: 900;
  letter-spacing: 0.2em;
}
.table-head th {
  padding: 16px;
}
.actions-header {
  text-align: right;
}
.table-row {
  transition: background-color 0.2s ease;
  border-bottom: 1px solid #f8fafc;
}
.table-row:hover {
  background-color: #f8fafc;
}
.table-row td {
  padding: 16px;
}
.user-id {
  color: #cbd5e1;
  font-family: monospace;
  font-size: 11px;
  font-weight: 700;
}
.user-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}
.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background-color: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 900;
  color: #64748b;
  transition: all 0.2s ease;
  flex-shrink: 0;
}
.table-row:hover .user-avatar {
  transform: scale(1.1);
  background-color: #e0e7ff;
  color: #4f46e5;
}
.user-details {
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.user-name {
  font-weight: 700;
  color: #0f172a;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.user-email {
  font-size: 11px;
  color: #64748b;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.rating-badge {
  font-weight: 700;
  color: #334155;
  background-color: #f1f5f9;
  padding: 4px 8px;
  border-radius: 8px;
  font-size: 12px;
}
.register-date {
  font-size: 11px;
  color: #64748b;
  font-weight: 700;
  white-space: nowrap;
}
.status-container {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.status-badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  background-color: #d1fae5;
  color: #059669;
  border: 1px solid #a7f3d0;
  white-space: nowrap;
}
.status-badge.banned {
  background-color: #fee2e2;
  color: #dc2626;
  border: 1px solid #fecaca;
}
.admin-badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  background-color: #e0e7ff;
  color: #4f46e5;
  border: 1px solid #c7d2fe;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  white-space: nowrap;
}
.actions-cell {
  text-align: right;
  position: relative;
}
.actions-btn {
  padding: 6px 12px;
  background-color: #f1f5f9;
  color: #475569;
  font-size: 11px;
  font-weight: 900;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease;
  white-space: nowrap;
}
.actions-btn:hover {
  background-color: #e2e8f0;
}
.actions-dropdown {
  position: absolute;
  right: 16px;
  top: 45px;
  width: 200px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.25);
  border: 1px solid #f1f5f9;
  z-index: 50;
  padding: 8px 0;
  animation: fadeIn 0.2s ease-out;
}
.dropdown-item {
  width: 100%;
  text-align: left;
  padding: 10px 16px;
  font-size: 12px;
  font-weight: 700;
  color: #334155;
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.2s ease;
}
.dropdown-item:hover {
  background-color: #f8fafc;
}
.delete-item {
  color: #ef4444;
}
.dropdown-divider {
  margin: 4px 0;
  border: none;
  border-top: 1px solid #f1f5f9;
}
.empty-table {
  padding: 40px 20px;
  text-align: center;
}
.empty-icon {
  font-size: 32px;
  margin-bottom: 8px;
}
.empty-title {
  color: #0f172a;
  font-weight: 700;
  font-size: 16px;
}
.empty-subtitle {
  color: #94a3b8;
  font-size: 13px;
}

/* Tasks Tab */
.tasks-tab-header {
  flex-direction: column;
  align-items: flex-start;
  gap: 16px;
}
.tasks-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.file-upload {
  display: none;
}
.import-btn,
.export-btn {
  padding: 8px;
  background-color: white;
  border: 1px solid #e2e8f0;
  color: #475569;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 40px;
  min-height: 40px;
}
.import-btn:hover,
.export-btn:hover {
  background-color: #f8fafc;
}
.create-btn {
  padding: 8px 16px;
  background-color: #4f46e5;
  color: white;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 700;
  border: none;
  cursor: pointer;
  box-shadow: 0 8px 12px -3px rgba(79, 70, 229, 0.1);
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
}
.create-btn:hover {
  background-color: #4338ca;
}
.plus-icon {
  font-size: 16px;
}
.tasks-table {
  width: 100%;
  min-width: 800px;
  text-align: left;
  border-collapse: collapse;
}
.sortable-column {
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s ease;
}
.sortable-column:hover {
  background-color: #f1f5f9;
}
.sort-indicator {
  margin-left: 4px;
  color: #4f46e5;
}
.task-row:hover {
  background-color: #f8fafc;
}
.task-id {
  font-size: 11px;
  font-family: monospace;
  color: #cbd5e1;
  font-weight: 700;
}
.task-cell {
  max-width: 200px;
}
.task-title {
  font-weight: 700;
  color: #0f172a;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 4px;
}
.task-description {
  font-size: 11px;
  color: #64748b;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.subject-badge {
  padding: 4px 8px;
  background-color: #f1f5f9;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  color: #475569;
  border: 1px solid #e2e8f0;
  white-space: nowrap;
}
.difficulty-badge {
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  white-space: nowrap;
}
.difficulty-badge.easy {
  color: #059669;
  background-color: #d1fae5;
  border-color: #a7f3d0;
}
.difficulty-badge.medium {
  color: #d97706;
  background-color: #fef3c7;
  border-color: #fde68a;
}
.difficulty-badge.hard {
  color: #dc2626;
  background-color: #fee2e2;
  border-color: #fecaca;
}
.answer-cell {
  position: relative;
}
.answer-code {
  background-color: #f1f5f9;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  color: #64748b;
  font-family: monospace;
  font-weight: 700;
  border: 1px solid #e2e8f0;
  display: none;
}
.task-row:hover .answer-code {
  display: inline;
}
.answer-placeholder {
  font-size: 11px;
  color: #cbd5e1;
  font-weight: 900;
  letter-spacing: 0.1em;
}
.task-row:hover .answer-placeholder {
  display: none;
}
.task-actions-cell {
  text-align: right;
  display: flex;
  justify-content: flex-end;
  gap: 6px;
}
.action-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: white;
  border: 1px solid #f1f5f9;
  color: #94a3b8;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  flex-shrink: 0;
}
.action-icon:hover {
  transform: scale(0.9);
}
.edit-icon:hover {
  background-color: #e0e7ff;
  color: #4f46e5;
  border-color: #c7d2fe;
}
.delete-icon:hover {
  background-color: #fee2e2;
  color: #dc2626;
  border-color: #fecaca;
}
.empty-tasks {
  padding: 40px 20px;
  text-align: center;
  color: #94a3b8;
  font-weight: 500;
  font-size: 14px;
}

/* Logs Tab */
.logs-tab {
  padding: 20px;
}

/* Modals */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  background-color: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(8px);
}
.task-modal,
.user-modal {
  background-color: white;
  border-radius: 20px;
  width: 100%;
  max-width: 100%;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.25);
  padding: 24px;
  border: 1px solid #f1f5f9;
  max-height: 90vh;
  overflow-y: auto;
  animation: fadeInUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.user-modal {
  max-width: 400px;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f8fafc;
}
.modal-header h2 {
  font-size: 20px;
  font-weight: 900;
  color: #0f172a;
  line-height: 1.2;
}
.close-modal {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background-color: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}
.close-modal:hover {
  background-color: #e2e8f0;
  color: #475569;
}
.modal-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.form-row {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}
.form-group {
  display: flex;
  flex-direction: column;
}
.form-label {
  font-size: 10px;
  font-weight: 900;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 6px;
  margin-left: 4px;
}
.form-select,
.form-input,
.form-textarea {
  width: 100%;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px 14px;
  font-weight: 700;
  color: #334155;
  outline: none;
  transition: all 0.2s ease;
  font-family: inherit;
  font-size: 14px;
}
.form-select:focus,
.form-input:focus,
.form-textarea:focus {
  background-color: white;
  border-color: #4f46e5;
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.1);
}
.answer-field {
  background-color: rgba(209, 250, 229, 0.5);
  border-color: #a7f3d0;
  color: #065f46;
}
.form-textarea {
  resize: none;
}
.form-submit {
  padding-top: 16px;
}
.submit-btn {
  width: 100%;
  padding: 14px;
  background-color: #4f46e5;
  color: white;
  font-weight: 900;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  box-shadow: 0 8px 12px -3px rgba(79, 70, 229, 0.2);
  transition: all 0.2s ease;
  font-size: 14px;
}
.submit-btn:hover {
  background-color: #4338ca;
}
.submit-btn:active {
  transform: scale(0.98);
}
.form-actions {
  display: flex;
  gap: 10px;
  padding-top: 16px;
}
.save-btn {
  flex: 1;
  padding: 14px;
  background-color: #4f46e5;
  color: white;
  font-weight: 900;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease;
  font-size: 14px;
}
.save-btn:hover {
  background-color: #4338ca;
}
.cancel-btn {
  padding: 14px 20px;
  background-color: #f1f5f9;
  color: #64748b;
  font-weight: 900;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease;
  font-size: 14px;
}
.cancel-btn:hover {
  background-color: #e2e8f0;
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ==================== ТЁМНАЯ ТЕМА ==================== */

:root.dark .admin-container {
  background-color: #0f172a;
  color: #f1f5f9;
}

:root.dark .admin-sidebar {
  background-color: #1e293b;
  border-right: 1px solid #334155;
}

:root.dark .admin-main {
  background-color: #0f172a;
}

:root.dark .access-denied-container {
  background-color: #0f172a;
  color: #f1f5f9;
}

:root.dark .access-denied-text h1 {
  color: #f8fafc;
}

:root.dark .access-denied-text p {
  color: #cbd5e1;
}

:root.dark .access-denied-icon {
  background-color: #334155;
}

:root.dark .home-btn {
  background-color: #3b82f6;
  color: white;
}

:root.dark .home-btn:hover {
  background-color: #2563eb;
}

/* Dashboard */
:root.dark .stat-card {
  background-color: #1e293b;
  border-color: #334155;
  color: #f1f5f9;
}

:root.dark .stat-card:hover {
  box-shadow: 0 6px 12px -2px rgba(0, 0, 0, 0.4);
}

:root.dark .stat-label {
  color: #cbd5e1;
}

:root.dark .stat-value {
  color: #f8fafc;
}

:root.dark .stat-description {
  color: #94a3b8;
}

/* Tables */
:root.dark .table-wrapper {
  background-color: #1e293b;
  border-color: #334155;
}

:root.dark .users-table,
:root.dark .tasks-table {
  background-color: #1e293b;
}

:root.dark .table-head {
  background-color: #334155;
  color: #cbd5e1;
  border-bottom-color: #475569;
}

:root.dark .table-row {
  border-bottom-color: #334155;
}

:root.dark .table-row:hover {
  background-color: #334155;
}

:root.dark .user-name,
:root.dark .task-title {
  color: #f1f5f9;
}

:root.dark .user-email,
:root.dark .task-description {
  color: #94a3b8;
}

:root.dark .rating-badge,
:root.dark .subject-badge {
  background-color: #334155;
  color: #cbd5e1;
}

:root.dark .status-badge:not(.banned) {
  background-color: #064e3b;
  color: #a7f3d0;
  border-color: #065f46;
}

:root.dark .status-badge.banned {
  background-color: #7f1d1d;
  color: #fecaca;
  border-color: #991b1b;
}

:root.dark .admin-badge {
  background-color: #1e3a8a;
  color: #93c5fd;
  border-color: #1e40af;
}

/* Modals */
:root.dark .modal-overlay {
  background-color: rgba(0, 0, 0, 0.7);
}

:root.dark .task-modal,
:root.dark .user-modal {
  background-color: #1e293b;
  border-color: #334155;
  color: #f1f5f9;
}

:root.dark .modal-header {
  border-bottom-color: #334155;
}

:root.dark .modal-header h2 {
  color: #f8fafc;
}

:root.dark .close-modal {
  background-color: #334155;
  color: #94a3b8;
}

:root.dark .close-modal:hover {
  background-color: #475569;
  color: #cbd5e1;
}

:root.dark .form-select,
:root.dark .form-input,
:root.dark .form-textarea {
  background-color: #334155;
  border-color: #475569;
  color: #f1f5f9;
}

:root.dark .form-select:focus,
:root.dark .form-input:focus,
:root.dark .form-textarea:focus {
  background-color: #334155;
  border-color: #3b82f6;
}

:root.dark .form-label {
  color: #cbd5e1;
}

:root.dark .submit-btn {
  background-color: #3b82f6;
}

:root.dark .submit-btn:hover {
  background-color: #2563eb;
}

:root.dark .save-btn {
  background-color: #3b82f6;
}

:root.dark .save-btn:hover {
  background-color: #2563eb;
}

:root.dark .cancel-btn {
  background-color: #334155;
  color: #cbd5e1;
}

:root.dark .cancel-btn:hover {
  background-color: #475569;
}

/* Buttons */
:root.dark .refresh-btn,
:root.dark .import-btn,
:root.dark .export-btn,
:root.dark .create-btn {
  background-color: #334155;
  border-color: #475569;
  color: #cbd5e1;
}

:root.dark .refresh-btn:hover,
:root.dark .import-btn:hover,
:root.dark .export-btn:hover {
  background-color: #475569;
}

:root.dark .create-btn {
  background-color: #3b82f6;
  color: white;
}

:root.dark .create-btn:hover {
  background-color: #2563eb;
}

/* Actions */
:root.dark .actions-btn {
  background-color: #334155;
  color: #cbd5e1;
}

:root.dark .actions-btn:hover {
  background-color: #475569;
}

:root.dark .actions-dropdown {
  background-color: #1e293b;
  border-color: #334155;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
}

:root.dark .dropdown-item {
  color: #cbd5e1;
}

:root.dark .dropdown-item:hover {
  background-color: #334155;
}

:root.dark .action-icon {
  background-color: #334155;
  border-color: #475569;
  color: #94a3b8;
}

:root.dark .action-icon:hover {
  background-color: #475569;
}

/* Mobile menu */
:root.dark .mobile-menu-btn {
  background-color: #1e293b;
  border-color: #334155;
}

:root.dark .burger-line {
  background-color: #cbd5e1;
}

:root.dark .mobile-overlay {
  background-color: rgba(0, 0, 0, 0.7);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Adjust dashboard header for theme toggle */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* ==================== АДАПТИВНЫЕ СТИЛИ ==================== */

@media (max-width: 360px) {
  .admin-main {
    padding: 12px;
  }

  .dashboard-header h1 {
    font-size: 22px;
  }

  .tab-header h1 {
    font-size: 20px;
  }

  .tasks-actions {
    gap: 6px;
  }

  .import-btn,
  .export-btn {
    min-width: 36px;
    min-height: 36px;
    padding: 6px;
  }

  .create-btn {
    padding: 8px 12px;
    font-size: 12px;
  }

  .task-modal,
  .user-modal {
    padding: 20px;
  }

  .modal-header h2 {
    font-size: 18px;
  }

  .stat-card {
    padding: 16px;
  }

  .stat-icon {
    width: 36px;
    height: 36px;
    font-size: 18px;
  }

  .stat-value {
    font-size: 18px;
  }
}

@media (max-width: 640px) {
  .stats-container {
    grid-template-columns: 1fr;
  }

  .stat-card {
    width: 100%;
  }
}

@media (min-width: 641px) and (max-width: 1024px) {
  .stats-container {
    grid-template-columns: repeat(2, 1fr);
  }

  .stat-card {
    width: 100%;
  }
}

@media (min-width: 481px) {
  .admin-main {
    padding: 20px;
  }

  .stat-icon {
    width: 44px;
    height: 44px;
    font-size: 22px;
  }

  .stat-value {
    font-size: 20px;
  }

  .tasks-tab-header {
    flex-direction: row;
    align-items: center;
  }

  .tasks-actions {
    gap: 12px;
  }

  .create-btn {
    padding: 10px 20px;
  }
}

@media (min-width: 641px) {
  .mobile-menu-btn {
    display: none;
  }

  .admin-sidebar {
    transform: translateX(0);
    position: fixed;
  }

  .admin-main {
    margin-left: 256px;
    padding: 24px;
    width: calc(100% - 256px);
  }

  .stats-container {
    grid-template-columns: repeat(2, 2fr);
  }

  .stat-card {
    width: 100%;
  }

  .sidebar-close {
    display: none;
  }

  .dashboard-header h1 {
    font-size: 28px;
  }

  .tab-header h1 {
    font-size: 24px;
  }

  .form-row {
    grid-template-columns: repeat(2, 1fr);
  }

  .task-modal {
    max-width: 600px;
  }

  .users-table,
  .tasks-table {
    min-width: auto;
  }

  .logs-tab {
    padding: 32px;
    margin-left: 256px;
  }
}

@media (min-width: 769px) {
  .admin-main {
    padding: 32px;
  }

  .stat-card {
    padding: 28px;
    border-radius: 24px;
  }

  .stat-icon {
    width: 48px;
    height: 48px;
    font-size: 24px;
  }

  .stat-value {
    font-size: 22px;
  }

  .dashboard-header h1 {
    font-size: 32px;
  }

  .tab-header h1 {
    font-size: 26px;
  }

  .table-head th {
    padding: 20px 24px;
  }

  .table-row td {
    padding: 20px 24px;
  }

  .task-modal {
    max-width: 700px;
    padding: 32px;
    border-radius: 24px;
  }
}

@media (min-width: 1025px) {
  .admin-main {
    padding: 40px;
  }

  .stats-container {
    gap: 24px;
  }

  .stat-card {
    padding: 32px;
    border-radius: 28px;
  }

  .stat-value {
    font-size: 28px;
  }

  .dashboard-header h1 {
    font-size: 36px;
  }

  .tab-header h1 {
    font-size: 30px;
  }

  .table-wrapper {
    border-radius: 24px;
  }

  .task-modal {
    max-width: 800px;
    border-radius: 28px;
  }
}

@media (min-width: 1281px) {
  .admin-main {
    padding: 48px;
    max-width: calc(100% - 256px);
  }

  .stats-container {
    gap: 28px;
  }

  .stat-card {
    padding: 36px;
    border-radius: 32px;
  }

  .stat-icon {
    width: 56px;
    height: 56px;
    font-size: 28px;
  }

  .stat-value {
    font-size: 36px;
  }

  .dashboard-header h1 {
    font-size: 40px;
  }

  .tab-header h1 {
    font-size: 34px;
  }

  .table-wrapper {
    border-radius: 28px;
  }

  .table-head th {
    padding: 24px 32px;
  }

  .table-row td {
    padding: 24px 32px;
  }

  .task-modal {
    max-width: 900px;
    border-radius: 32px;
  }
}

@media (min-width: 1537px) {
  .admin-main {
    padding: 56px;
    max-width: 1400px;
    margin-left: 256px;
  }

  .stats-container {
    gap: 32px;
  }

  .stat-card {
    padding: 40px;
  }

  .stat-value {
    font-size: 40px;
  }

  .dashboard-header h1 {
    font-size: 44px;
  }

  .tab-header h1 {
    font-size: 38px;
  }

  .task-modal {
    max-width: 1000px;
  }
}

@media (min-width: 1920px) {
  .admin-sidebar {
    top: 0;
    z-index: 100;
  }
}

</style>
