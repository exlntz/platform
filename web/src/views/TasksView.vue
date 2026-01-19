<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useTimerStore } from '@/TimerStore.js'

const timer = useTimerStore()

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
  timer.startTask()
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
  <div class="tasks-container">
    <div class="tasks-content">
      <div class="tasks-header">
        <div class="header-text">
          <h1 class="title">Тренировочные задачи</h1>
          <p class="description">
            Улучшайте свои навыки, решая задачи разной сложности.
            Ваш прогресс сохраняется автоматически.
          </p>
        </div>

        <div v-if="!loading" class="tasks-counter">
          <span class="counter-badge">Доступно задач: {{ filteredTasks.length }}</span>
        </div>
      </div>

      <div class="filters-container">
        <div class="search-group">
          <div class="search-icon">🔍</div>
          <input
            v-model="filters.search"
            type="text"
            placeholder="Поиск по названию или теме..."
            class="search-input"
          />
        </div>

        <div class="filter-group">
          <div class="select-wrapper">
            <select
              v-model="filters.subject"
              class="filter-select"
            >
              <option value="">Все предметы</option>
              <option v-for="s in subjects" :key="s" :value="s">{{ s }}</option>
            </select>
            <div class="select-arrow">▼</div>
          </div>

          <div class="select-wrapper">
            <select
              v-model="filters.difficulty"
              class="filter-select"
            >
              <option value="">Сложность</option>
              <option v-for="d in difficulties" :key="d.value" :value="d.value">{{ d.label }}</option>
            </select>
            <div class="select-arrow">▼</div>
          </div>

          <button
            @click="resetFilters"
            class="reset-btn"
            title="Сбросить фильтры"
          >
            ✕
          </button>
        </div>
      </div>

      <div v-if="error" class="error-state">
        <div class="error-icon">🔌</div>
        <h3 class="error-title">Ошибка соединения</h3>
        <p class="error-message">{{ error }}</p>
        <button @click="fetchTasks" class="retry-btn">Попробовать снова</button>
      </div>

      <div v-else class="tasks-grid">
        <template v-if="loading">
          <div v-for="i in 6" :key="i" class="task-card-skeleton">
            <div class="skeleton-header">
              <div class="skeleton-tag"></div>
              <div class="skeleton-difficulty"></div>
            </div>
            <div class="skeleton-title"></div>
            <div class="skeleton-description">
              <div class="skeleton-line"></div>
              <div class="skeleton-line short"></div>
            </div>
            <div class="skeleton-footer">
              <div class="skeleton-tags"></div>
              <div class="skeleton-button"></div>
            </div>
          </div>
        </template>

        <template v-else-if="filteredTasks.length === 0">
          <div class="empty-state">
            <div class="empty-icon">🔍</div>
            <h3 class="empty-title">Задачи не найдены</h3>
            <p class="empty-description">
              Попробуйте изменить параметры поиска или сбросить фильтры.
            </p>
            <button @click="resetFilters" class="reset-filters-btn">
              Сбросить все фильтры
            </button>
          </div>
        </template>

        <template v-else>
          <div
            v-for="task in filteredTasks"
            :key="task.id"
            class="task-card"
            @click="navigateToTask(task.id)"
          >
            <div class="task-accent"></div>

            <div class="task-header">
              <span class="subject-tag">{{ task.subject }}</span>
              <span class="difficulty-badge" :class="getDifficultyClass(task.difficulty)">
                {{ task.difficulty }}
              </span>
            </div>

            <h3 class="task-title">{{ task.title }}</h3>

            <p class="task-description">
              {{ task.description }}
            </p>

            <div class="task-footer">
              <div class="task-tags">
                <span
                  v-for="(tag, idx) in getTags(task.theme)"
                  :key="idx"
                  class="tag"
                >
                  #{{ tag }}
                </span>
              </div>

              <button class="solve-btn">
                Решать
                <span class="btn-arrow">→</span>
              </button>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.tasks-container {
  min-height: 100vh;
  background-color: #f8fafc;
  font-family: sans-serif;
}
.tasks-content {
  max-width: 1280px;
  margin: 0 auto;
  padding: 40px 24px;
}
.tasks-header {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-bottom: 32px;
}
@media (min-width: 768px) {
  .tasks-header {
    flex-direction: row;
    align-items: flex-end;
    justify-content: space-between;
    gap: 24px;
  }
}
.header-text {
  flex: 1;
}
.title {
  font-size: 30px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.025em;
  margin-bottom: 8px;
}
@media (min-width: 768px) {
  .title {
    font-size: 36px;
  }
}
.description {
  color: #64748b;
  font-weight: 500;
  font-size: 18px;
  line-height: 1.75;
  max-width: 768px;
}
.tasks-counter {
  display: none;
}
@media (min-width: 768px) {
  .tasks-counter {
    display: block;
  }
}
.counter-badge {
  display: inline-flex;
  align-items: center;
  padding: 8px 16px;
  background-color: white;
  border: 1px solid #e2e8f0;
  color: #475569;
  font-weight: 700;
  border-radius: 9999px;
  font-size: 14px;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}
.filters-container {
  background-color: white;
  padding: 16px;
  border-radius: 16px;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: sticky;
  top: 16px;
  z-index: 30;
  transition: all 0.2s ease;
}
@media (min-width: 1024px) {
  .filters-container {
    flex-direction: row;
  }
}
.search-group {
  flex: 1;
  position: relative;
}
.search-icon {
  position: absolute;
  top: 50%;
  left: 12px;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 20px;
  transition: color 0.2s ease;
}
.search-group:focus-within .search-icon {
  color: #4f46e5;
}
.search-input {
  width: 100%;
  padding: 12px 12px 12px 40px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background-color: #f8fafc;
  color: #0f172a;
  font-size: 14px;
  font-weight: 500;
  outline: none;
  transition: all 0.2s ease;
}
.search-input:focus {
  background-color: white;
  border-color: #4f46e5;
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.1);
}
.search-input::placeholder {
  color: #94a3b8;
}
.filter-group {
  display: flex;
  gap: 16px;
}
.select-wrapper {
  position: relative;
  min-width: 180px;
}
.filter-select {
  appearance: none;
  display: block;
  width: 100%;
  padding: 12px 40px 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background-color: white;
  color: #334155;
  font-weight: 700;
  font-size: 14px;
  outline: none;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}
.filter-select:hover {
  border-color: #a5b4fc;
}
.filter-select:focus {
  border-color: #4f46e5;
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.1);
}
.select-arrow {
  pointer-events: none;
  position: absolute;
  top: 50%;
  right: 16px;
  transform: translateY(-50%);
  color: #6b7280;
  font-size: 12px;
}
.reset-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background-color: white;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 18px;
}
.reset-btn:hover {
  color: #ef4444;
  background-color: #fef2f2;
  border-color: #fecaca;
}
.error-state {
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 24px;
  padding: 32px;
  text-align: center;
  animation: fadeIn 0.5s ease-out;
}
.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}
.error-title {
  font-size: 18px;
  font-weight: 700;
  color: #991b1b;
  margin-bottom: 8px;
}
.error-message {
  color: #dc2626;
  margin-bottom: 24px;
}
.retry-btn {
  padding: 8px 24px;
  background-color: white;
  color: #dc2626;
  font-weight: 700;
  border-radius: 8px;
  border: 1px solid #fecaca;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}
.retry-btn:hover {
  background-color: #fef2f2;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
.tasks-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 24px;
  margin-top: 32px;
}
@media (min-width: 768px) {
  .tasks-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (min-width: 1024px) {
  .tasks-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
.task-card-skeleton {
  background-color: white;
  border-radius: 24px;
  border: 1px solid #f1f5f9;
  padding: 24px;
  height: 288px;
  display: flex;
  flex-direction: column;
  animation: pulse 2s infinite;
}
.skeleton-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 24px;
}
.skeleton-tag {
  height: 24px;
  width: 96px;
  background-color: #f1f5f9;
  border-radius: 9999px;
}
.skeleton-difficulty {
  height: 24px;
  width: 64px;
  background-color: #f1f5f9;
  border-radius: 9999px;
}
.skeleton-title {
  height: 32px;
  width: 75%;
  background-color: #f1f5f9;
  border-radius: 8px;
  margin-bottom: 16px;
}
.skeleton-description {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.skeleton-line {
  height: 16px;
  width: 100%;
  background-color: #f8fafc;
  border-radius: 4px;
}
.skeleton-line.short {
  width: 5/6;
}
.skeleton-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #f8fafc;
}
.skeleton-tags {
  height: 24px;
  width: 96px;
  background-color: #f1f5f9;
  border-radius: 9999px;
}
.skeleton-button {
  height: 40px;
  width: 96px;
  background-color: #f1f5f9;
  border-radius: 12px;
}
.empty-state {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 24px;
  text-align: center;
}
.empty-icon {
  width: 96px;
  height: 96px;
  background-color: #f1f5f9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  margin-bottom: 24px;
}
.empty-title {
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 8px;
}
.empty-description {
  color: #64748b;
  max-width: 384px;
  margin-bottom: 24px;
}
.reset-filters-btn {
  color: #4f46e5;
  font-weight: 700;
  background: none;
  border: none;
  cursor: pointer;
  text-decoration: underline;
  transition: color 0.2s ease;
}
.reset-filters-btn:hover {
  color: #3730a3;
}
.task-card {
  background-color: white;
  border-radius: 24px;
  border: 1px solid #f1f5f9;
  padding: 24px;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}
.task-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.1);
}
.task-accent {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(to right, #4f46e5, #ec4899, #f59e0b);
  opacity: 0;
  transition: opacity 0.3s ease;
}
.task-card:hover .task-accent {
  opacity: 1;
}
.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}
.subject-tag {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  background-color: #f1f5f9;
  color: #475569;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.difficulty-badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  border: 1px solid;
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
.difficulty-badge.default {
  color: #475569;
  background-color: #f1f5f9;
  border-color: #e2e8f0;
}
.task-title {
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 12px;
  line-height: 1.4;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  transition: color 0.2s ease;
}
.task-card:hover .task-title {
  color: #4f46e5;
}
.task-description {
  color: #6b7280;
  font-size: 14px;
  font-weight: 500;
  line-height: 1.625;
  flex: 1;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  margin-bottom: 24px;
}
.task-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding-top: 24px;
  border-top: 1px solid #f8fafc;
}
.task-tags {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  overflow: hidden;
  max-height: 24px;
}
.tag {
  font-size: 10px;
  font-weight: 700;
  color: #64748b;
  background-color: #f8fafc;
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid #f1f5f9;
  white-space: nowrap;
}
.solve-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background-color: #0f172a;
  color: white;
  font-size: 14px;
  font-weight: 700;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.1);
  transition: all 0.2s ease;
  flex-shrink: 0;
}
.task-card:hover .solve-btn {
  background-color: #4f46e5;
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.2);
}
.solve-btn:active {
  transform: scale(0.95);
}
.btn-arrow {
  font-size: 16px;
  transition: transform 0.2s ease;
}
.task-card:hover .btn-arrow {
  transform: translateX(4px);
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
