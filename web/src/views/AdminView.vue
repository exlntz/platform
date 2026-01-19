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
  <div v-if="accessDenied" class="access-denied-container">
    <div class="access-denied-content">
      <div class="access-denied-icon">
        <span>🔒</span>
      </div>
      <div class="access-denied-text">
        <h1>Доступ запрещен</h1>
        <p>У вас недостаточно прав для просмотра этой страницы. <br>
           Эта зона только для администраторов.</p>
      </div>
      <div class="access-denied-actions">
        <router-link to="/" class="home-btn">
          На главную
        </router-link>
      </div>
      <p class="error-code">ERROR CODE: 403 FORBIDDEN</p>
    </div>
  </div>

  <div v-else class="admin-container">
    <aside class="admin-sidebar">
      <div class="sidebar-header">
        <div class="sidebar-logo">A</div>
        <span class="sidebar-title">Admin Panel</span>
      </div>

      <nav class="sidebar-nav">
        <button
          @click="currentTab = 'dashboard'"
          class="nav-btn"
          :class="{ active: currentTab === 'dashboard' }"
        >
          <span class="nav-icon">📊</span> Дашборд
        </button>
        <button
          @click="currentTab = 'users'"
          class="nav-btn"
          :class="{ active: currentTab === 'users' }"
        >
          <span class="nav-icon">👥</span> Пользователи
        </button>
        <button
          @click="currentTab = 'tasks'; fetchTasks()"
          class="nav-btn"
          :class="{ active: currentTab === 'tasks' }"
        >
          <span class="nav-icon">📝</span> Задачи
        </button>
      </nav>

      <div class="sidebar-footer">
        <router-link to="/" class="back-to-site">
          ← Вернуться на сайт
        </router-link>
      </div>
    </aside>

    <main class="admin-main">
      <!-- Dashboard Tab -->
      <div v-if="currentTab === 'dashboard'" class="dashboard-tab">
        <div class="dashboard-header">
          <h1>Обзор системы</h1>
          <span class="live-badge">Live Updates</span>
        </div>

        <div class="stats-container">
          <div class="stat-card">
            <div class="stat-header">
              <div class="stat-icon users-icon">👥</div>
              <span class="stat-label">Всего</span>
            </div>
            <p class="stat-value">{{ stats.total_users }}</p>
            <p class="stat-description">пользователей</p>
          </div>

          <div class="stat-card">
            <div class="stat-header">
              <div class="stat-icon growth-icon">🔥</div>
              <span class="stat-label">Динамика</span>
            </div>
            <p class="stat-value">+{{ stats.new_users_24h }}</p>
            <p class="stat-description">за 24 часа</p>
          </div>

          <div class="stat-card">
            <div class="stat-header">
              <div class="stat-icon skill-icon">⭐</div>
              <span class="stat-label">Скилл</span>
            </div>
            <p class="stat-value">{{ stats.average_rating }}</p>
            <p class="stat-description">средний ELO</p>
          </div>

          <div class="stat-card">
            <div class="stat-header">
              <div class="stat-icon trends-icon">📚</div>
              <span class="stat-label">Тренды</span>
            </div>
            <p class="stat-value">{{ stats.most_popular_subject }}</p>
            <p class="stat-description">выбор игроков</p>
          </div>
        </div>
      </div>

      <!-- Users Tab -->
      <div v-if="currentTab === 'users'" class="users-tab">
        <div class="tab-header">
          <h1>Управление пользователями</h1>
          <button @click="fetchUsers" class="refresh-btn">
            🔄 Обновить
          </button>
        </div>

        <div class="table-wrapper">
          <table class="users-table">
            <thead>
              <tr class="table-head">
                <th>ID</th>
                <th>Пользователь</th>
                <th>Рейтинг</th>
                <th>Дата регистрации</th>
                <th>Роль / Статус</th>
                <th class="actions-header">Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id" class="table-row">
                <td class="user-id">#{{ user.id }}</td>
                <td class="user-cell">
                  <div class="user-avatar">
                    {{ user.username.charAt(0).toUpperCase() }}
                  </div>
                  <div class="user-details">
                    <p class="user-name">{{ user.username }}</p>
                    <p class="user-email">{{ user.email }}</p>
                  </div>
                </td>
                <td>
                  <span class="rating-badge">{{ user.rating }}</span>
                </td>
                <td class="register-date">
                  {{ formatDate(user.created_at) }}
                </td>
                <td>
                  <div class="status-container">
                    <span class="status-badge" :class="{ banned: user.is_banned }">
                      {{ user.is_banned ? 'Banned' : 'Active' }}
                    </span>
                    <span v-if="user.is_admin" class="admin-badge">
                      Admin
                    </span>
                  </div>
                </td>
                <td class="actions-cell">
                  <button
                    @click="toggleMenu($event, user.id)"
                    class="actions-btn"
                  >
                    Действия ▾
                  </button>

                  <div v-if="activeMenuId === user.id" class="actions-dropdown">
                    <button @click="openEditUser(user)" class="dropdown-item">
                      <span class="item-icon">✏️</span> Изменить данные
                    </button>
                    <button @click="updateUserAction(user.id, { is_admin: !user.is_admin })" class="dropdown-item">
                      <span class="item-icon">{{ user.is_admin ? '⭐' : '👑' }}</span> {{ user.is_admin ? 'Снять админа' : 'Сделать админом' }}
                    </button>
                    <button @click="updateUserAction(user.id, { is_banned: !user.is_banned })" class="dropdown-item">
                      <span class="item-icon">{{ user.is_banned ? '🔓' : '🚫' }}</span> {{ user.is_banned ? 'Разблокировать' : 'Заблокировать' }}
                    </button>
                    <div class="dropdown-divider"></div>
                    <button @click="deleteUser(user)" class="dropdown-item delete-item">
                      <span class="item-icon">🗑️</span> Удалить
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>

          <div v-if="!loading && users.length === 0" class="empty-table">
            <div class="empty-icon">🔍</div>
            <p class="empty-title">Пользователи не найдены</p>
            <p class="empty-subtitle">Список пуст или произошла ошибка загрузки</p>
          </div>
        </div>
      </div>

      <!-- Tasks Tab -->
      <div v-if="currentTab === 'tasks'" class="tasks-tab">
        <div class="tab-header tasks-tab-header">
          <h1>Управление задачами</h1>
          <div class="tasks-actions">
            <input type="file" ref="fileInput" class="file-upload" accept=".json" @change="handleImport">
            <button @click="triggerImport" class="import-btn">
              📥 Импорт
            </button>
            <button @click="exportTasks" class="export-btn">
              📤 Экспорт
            </button>
            <button @click="openCreateModal" class="create-btn">
              <span class="plus-icon">+</span> Создать
            </button>
          </div>
        </div>

        <div class="table-wrapper">
          <table class="tasks-table">
            <thead>
              <tr class="table-head">
                <th @click="sortBy('id')" class="sortable-column">
                  ID <span v-if="sortKey === 'id'" class="sort-indicator">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('title')" class="sortable-column">
                  Задача <span v-if="sortKey === 'title'" class="sort-indicator">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('subject')" class="sortable-column">
                  Предмет <span v-if="sortKey === 'subject'" class="sort-indicator">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('difficulty')" class="sortable-column">
                  Сложность <span v-if="sortKey === 'difficulty'" class="sort-indicator">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th>Ответ</th>
                <th class="actions-header">Действие</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="task in sortedTasks" :key="task.id" class="table-row task-row">
                <td class="task-id">#{{ task.id }}</td>
                <td class="task-cell">
                  <p class="task-title">{{ task.title }}</p>
                  <p class="task-description">{{ task.description.substring(0, 60) }}...</p>
                </td>
                <td>
                  <span class="subject-badge">{{ task.subject }}</span>
                </td>
                <td>
                  <span class="difficulty-badge" :class="task.difficulty.toLowerCase()">
                    {{ task.difficulty }}
                  </span>
                </td>
                <td class="answer-cell">
                  <code class="answer-code">{{ task.correct_answer || '***' }}</code>
                  <span class="answer-placeholder">***</span>
                </td>
                <td class="task-actions-cell">
                  <button
                    @click="openEditModal(task)"
                    class="action-icon edit-icon"
                    title="Редактировать"
                  >
                    <span>✏️</span>
                  </button>
                  <button
                    @click="deleteTask(task.id)"
                    class="action-icon delete-icon"
                    title="Удалить задачу"
                  >
                    <span>🗑️</span>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>

          <div v-if="!loading && tasks.length === 0" class="empty-tasks">
            Задач пока нет. Создайте первую!
          </div>
        </div>
      </div>
    </main>

    <!-- Task Modal -->
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
                <option v-for="s in subjectOptions" :key="s" :value="s">{{ s }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Сложность</label>
              <select v-model="taskForm.difficulty" required class="form-select">
                <option v-for="d in difficultyOptions" :key="d" :value="d">{{ d }}</option>
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
            <textarea v-model="taskForm.hint" rows="2" placeholder="Необязательная подсказка для режима тренировки..." class="form-textarea"></textarea>
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
            <button type="submit" class="submit-btn">
              {{ isEditMode ? 'Сохранить изменения' : 'Создать задачу' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- User Edit Modal -->
    <div v-if="showUserEditModal" class="modal-overlay">
      <div class="user-modal">
        <h2>Редактировать профиль</h2>
        <form @submit.prevent="updateUserAction(userEditForm.id, userEditForm, 'Данные сохранены')" class="modal-form">
          <div class="form-group">
            <label class="form-label">Имя пользователя</label>
            <input v-model="userEditForm.username" class="form-input">
          </div>
          <div class="form-group">
            <label class="form-label">Email</label>
            <input v-model="userEditForm.email" class="form-input">
          </div>
          <div class="form-group">
            <label class="form-label">Рейтинг ELO</label>
            <input v-model.number="userEditForm.rating" type="number" class="form-input">
          </div>
          <div class="form-actions">
            <button type="submit" class="save-btn">Сохранить</button>
            <button @click="showUserEditModal = false" type="button" class="cancel-btn">Отмена</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Access Denied Page */
.access-denied-container {
  min-height: 100vh;
  background-color: #f8fafc;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 16px;
  font-family: sans-serif;
}
.access-denied-content {
  max-width: 448px;
  width: 100%;
  text-align: center;
}
.access-denied-icon {
  width: 96px;
  height: 96px;
  background-color: #fee2e2;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 32px;
  box-shadow: 0 20px 25px -5px rgba(254, 202, 202, 0.5);
}
.access-denied-icon span {
  font-size: 48px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.access-denied-text h1 {
  font-size: 36px;
  font-weight: 900;
  color: #0f172a;
  letter-spacing: -0.025em;
  margin-bottom: 12px;
}
.access-denied-text p {
  color: #64748b;
  font-weight: 500;
  font-size: 18px;
  line-height: 1.75;
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
  padding: 16px 32px;
  background-color: #0f172a;
  color: white;
  font-weight: 700;
  border-radius: 16px;
  text-decoration: none;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
  border: none;
  cursor: pointer;
  display: inline-block;
}
.home-btn:hover {
  background-color: #1e293b;
}
.home-btn:active {
  transform: scale(0.95);
}
.error-code {
  font-size: 12px;
  color: #94a3b8;
  font-family: monospace;
  margin-top: 32px;
}


/* Admin Layout */
.admin-container {
  min-height: 100vh;
  background-color: #f8fafc;
  display: flex;
  font-family: sans-serif;
}
.admin-sidebar {
  width: 256px;
  background-color: #0f172a;
  color: white;
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100%;
  z-index: 20;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}
.sidebar-header {
  padding: 24px;
  border-bottom: 1px solid #1e293b;
  display: flex;
  align-items: center;
  gap: 12px;
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
  box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.2);
}
.sidebar-title {
  font-weight: 700;
  font-size: 18px;
  letter-spacing: -0.025em;
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
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.25);
}
.nav-btn:not(.active):hover {
  background-color: #1e293b;
  color: white;
}
.nav-icon {
  font-size: 20px;
  transition: transform 0.2s ease;
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
  font-size: 12px;
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
  margin-left: 256px;
  padding: 32px;
}


/* Dashboard Tab */
.dashboard-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 32px;
}
.dashboard-header h1 {
  font-size: 36px;
  font-weight: 900;
  color: #0f172a;
  letter-spacing: -0.025em;
}
.live-badge {
  font-size: 14px;
  font-weight: 700;
  color: #64748b;
  background-color: white;
  padding: 4px 12px;
  border-radius: 9999px;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  border: 1px solid #f1f5f9;
}
.stats-container {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 24px;
}
@media (min-width: 768px) {
  .stats-container {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (min-width: 1024px) {
  .stats-container {
    grid-template-columns: repeat(4, 1fr);
  }
}
.stat-card {
  background-color: white;
  padding: 24px;
  border-radius: 32px;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  border: 1px solid #f1f5f9;
  transition: box-shadow 0.2s ease;
}
.stat-card:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
.stat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
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
  font-size: 10px;
  font-weight: 900;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}
.stat-value {
  font-size: 30px;
  font-weight: 900;
  color: #0f172a;
}
.stat-description {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
  margin-top: 4px;
}


/* Common Tab Styles */
.tab-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}
.tab-header h1 {
  font-size: 30px;
  font-weight: 900;
  color: #0f172a;
}
.refresh-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background-color: white;
  border: 1px solid #e2e8f0;
  color: #475569;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}
.refresh-btn:hover {
  background-color: #f8fafc;
}
.table-wrapper {
  background-color: white;
  border-radius: 32px;
  box-shadow: 0 25px 50px -12px rgba(148, 163, 184, 0.4);
  border: 1px solid #f1f5f9;
  overflow: hidden;
}


/* Users Table */
.users-table {
  width: 100%;
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
  padding: 20px 32px;
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
  padding: 20px 32px;
}
.user-id {
  color: #cbd5e1;
  font-family: monospace;
  font-size: 12px;
  font-weight: 700;
}
.user-cell {
  display: flex;
  align-items: center;
  gap: 16px;
}
.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background-color: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 900;
  color: #64748b;
  transition: all 0.2s ease;
}
.table-row:hover .user-avatar {
  transform: scale(1.1);
  background-color: #e0e7ff;
  color: #4f46e5;
}
.user-details {
  display: flex;
  flex-direction: column;
}
.user-name {
  font-weight: 700;
  color: #0f172a;
  font-size: 14px;
}
.user-email {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
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
  font-size: 12px;
  color: #64748b;
  font-weight: 700;
}
.status-container {
  display: flex;
  align-items: center;
  gap: 8px;
}
.status-badge {
  padding: 6px 10px;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  background-color: #d1fae5;
  color: #059669;
  border: 1px solid #a7f3d0;
}
.status-badge.banned {
  background-color: #fee2e2;
  color: #dc2626;
  border: 1px solid #fecaca;
}
.admin-badge {
  padding: 6px 10px;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  background-color: #e0e7ff;
  color: #4f46e5;
  border: 1px solid #c7d2fe;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}
.actions-cell {
  text-align: right;
  position: relative;
}
.actions-btn {
  padding: 8px 16px;
  background-color: #f1f5f9;
  color: #475569;
  font-size: 12px;
  font-weight: 900;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease;
}
.actions-btn:hover {
  background-color: #e2e8f0;
}
.actions-dropdown {
  position: absolute;
  right: 32px;
  top: 56px;
  width: 208px;
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  border: 1px solid #f1f5f9;
  z-index: 50;
  padding: 8px 0;
  animation: fadeIn 0.2s ease-out;
}
.dropdown-item {
  width: 100%;
  text-align: left;
  padding: 12px 20px;
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
  padding: 48px;
  text-align: center;
}
.empty-icon {
  font-size: 36px;
  margin-bottom: 8px;
}
.empty-title {
  color: #0f172a;
  font-weight: 700;
}
.empty-subtitle {
  color: #94a3b8;
  font-size: 14px;
}


/* Tasks Tab */
.tasks-tab-header {
  flex-direction: column;
  align-items: flex-start;
  gap: 16px;
}
@media (min-width: 768px) {
  .tasks-tab-header {
    flex-direction: row;
    align-items: center;
  }
}
.tasks-actions {
  display: flex;
  gap: 8px;
}
.file-upload {
  display: none;
}
.import-btn,
.export-btn {
  padding: 8px 16px;
  background-color: white;
  border: 1px solid #e2e8f0;
  color: #475569;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  gap: 8px;
}
.import-btn:hover,
.export-btn:hover {
  background-color: #f8fafc;
}
.create-btn {
  padding: 8px 24px;
  background-color: #4f46e5;
  color: white;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  border: none;
  cursor: pointer;
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.1);
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}
.create-btn:hover {
  background-color: #4338ca;
}
.plus-icon {
  font-size: 16px;
}
.tasks-table {
  width: 100%;
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
  font-size: 12px;
  font-family: monospace;
  color: #cbd5e1;
  font-weight: 700;
}
.task-cell {
  max-width: 300px;
}
.task-title {
  font-weight: 700;
  color: #0f172a;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 4px;
}
.task-description {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.subject-badge {
  padding: 6px 10px;
  background-color: #f1f5f9;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  color: #475569;
  border: 1px solid #e2e8f0;
}
.difficulty-badge {
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  padding: 6px 10px;
  border-radius: 8px;
  border: 1px solid;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
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
  font-size: 12px;
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
  font-size: 12px;
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
  gap: 8px;
}
.action-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: white;
  border: 1px solid #f1f5f9;
  color: #94a3b8;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
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
  padding: 48px;
  text-align: center;
  color: #94a3b8;
  font-weight: 500;
}


/* Modals */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 50;
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
  border-radius: 32px;
  width: 100%;
  max-width: 896px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  padding: 32px;
  border: 1px solid #f1f5f9;
  max-height: 90vh;
  overflow-y: auto;
  animation: fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}
.user-modal {
  max-width: 448px;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f8fafc;
}
.modal-header h2 {
  font-size: 24px;
  font-weight: 900;
  color: #0f172a;
}
.close-modal {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background-color: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}
.close-modal:hover {
  background-color: #e2e8f0;
  color: #475569;
}
.modal-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.form-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
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
  margin-bottom: 8px;
  margin-left: 4px;
}
.form-select,
.form-input,
.form-textarea {
  width: 100%;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 14px 16px;
  font-weight: 700;
  color: #334155;
  outline: none;
  transition: all 0.2s ease;
  font-family: inherit;
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
  padding: 16px;
  background-color: #4f46e5;
  color: white;
  font-weight: 900;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.2);
  transition: all 0.2s ease;
}
.submit-btn:hover {
  background-color: #4338ca;
}
.submit-btn:active {
  transform: scale(0.98);
}
.form-actions {
  display: flex;
  gap: 12px;
  padding-top: 16px;
}
.save-btn {
  flex: 1;
  padding: 16px;
  background-color: #4f46e5;
  color: white;
  font-weight: 900;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease;
}
.save-btn:hover {
  background-color: #4338ca;
}
.cancel-btn {
  padding: 16px 24px;
  background-color: #f1f5f9;
  color: #64748b;
  font-weight: 900;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease;
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
</style>
