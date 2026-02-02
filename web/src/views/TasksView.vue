<script setup>
import { ref, onMounted, watch, computed, onUnmounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useTimerStore } from '@/pinia/TimerStore.js'

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

// Определение размеров экрана для адаптивности
const screenSize = ref('mobile')

const updateScreenSize = () => {
  const width = window.innerWidth
  if (width < 640) screenSize.value = 'mobile'
  else if (width < 768) screenSize.value = 'sm'
  else if (width < 1024) screenSize.value = 'tablet'
  else if (width < 1280) screenSize.value = 'desktop'
  else screenSize.value = 'large'
}

// --- ЛОГИКА ---

// Хелпер для заголовков авторизации
const getAuthHeader = () => {
  const token = localStorage.getItem('user-token')
  return token ? { headers: { Authorization: `Bearer ${token}` } } : {}
}

// Функция загрузки задач с защитой от "дребезга" (Debounce)
let debounceTimer = null

const fetchTasks = async () => {
  loading.value = true
  error.value = null

  try {
    const params = {}
    if (filters.value.subject) params.subject = filters.value.subject
    if (filters.value.difficulty) params.difficulty = filters.value.difficulty

    const response = await axios.get('/tasks/', {
      params,
      ...getAuthHeader()
    })

    tasks.value = response.data
  } catch (err) {
    console.error('Ошибка загрузки:', err)
    error.value = 'Сервер временно недоступен. Попробуйте обновить страницу.'
  } finally {
    setTimeout(() => { loading.value = false }, 400)
  }
}

// Дебаунс-обертка для вотчера
const debouncedFetch = () => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    fetchTasks()
  }, 500)
}

// Клиентская фильтрация поиска
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
    .slice(0, screenSize.value === 'mobile' ? 2 : 3) // Меньше тегов на мобильных
}

const getDifficultyClass = (diff) => {
  const found = difficulties.find(d => d.value === diff)
  return found ? found.color : 'text-slate-600 bg-slate-100 border-slate-200'
}

// Переход к решению
const navigateToTask = (id) => {

  router.push(`/tasks/${id}`)
}

// Следим за фильтрами
watch(() => [filters.value.subject, filters.value.difficulty], () => {
  fetchTasks()
})

onMounted(() => {
  updateScreenSize()
  window.addEventListener('resize', updateScreenSize)
  fetchTasks()
})

onUnmounted(() => {
  window.removeEventListener('resize', updateScreenSize)
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

        <div v-if="!loading && screenSize !== 'mobile' && screenSize !== 'sm'" class="tasks-counter">
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
              :class="{ 'compact': screenSize === 'mobile' }"
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
              :class="{ 'compact': screenSize === 'mobile' }"
            >
              <option value="">Сложность</option>
              <option v-for="d in difficulties" :key="d.value" :value="d.value">{{ d.label }}</option>
            </select>
            <div class="select-arrow">▼</div>
          </div>

          <button
            @click="resetFilters"
            class="reset-btn"
            :class="{ 'compact': screenSize === 'mobile' }"
            :title="screenSize === 'mobile' ? '' : 'Сбросить фильтры'"
          >
            {{ screenSize === 'mobile' ? 'Сброс' : '✕' }}
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
          <div v-for="i in screenSize === 'mobile' ? 4 : 6" :key="i" class="task-card-skeleton">
            <div class="skeleton-header">
              <div class="skeleton-tag" :class="{ 'mobile': screenSize === 'mobile' }"></div>
              <div class="skeleton-difficulty" :class="{ 'mobile': screenSize === 'mobile' }"></div>
            </div>
            <div class="skeleton-title" :class="{ 'mobile': screenSize === 'mobile' }"></div>
            <div class="skeleton-description">
              <div class="skeleton-line" :class="{ 'mobile': screenSize === 'mobile' }"></div>
              <div class="skeleton-line short" :class="{ 'mobile': screenSize === 'mobile' }"></div>
            </div>
            <div class="skeleton-footer">
              <div class="skeleton-tags" :class="{ 'mobile': screenSize === 'mobile' }"></div>
              <div class="skeleton-button" :class="{ 'mobile': screenSize === 'mobile' }"></div>
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
              <span class="subject-tag" :class="{ 'mobile': screenSize === 'mobile' }">{{ task.subject }}</span>
              <span class="difficulty-badge" :class="[getDifficultyClass(task.difficulty), { 'mobile': screenSize === 'mobile' }]">
                {{ screenSize === 'mobile' ? task.difficulty.charAt(0) : task.difficulty }}
              </span>
            </div>

            <h3 class="task-title" :class="{ 'mobile': screenSize === 'mobile' }">{{ task.title }}</h3>

            <p class="task-description" :class="{ 'mobile': screenSize === 'mobile' }">
              {{ task.description }}
            </p>

            <div class="task-footer" :class="{ 'mobile': screenSize === 'mobile' }">
              <div class="task-tags">
                <span
                  v-for="(tag, idx) in getTags(task.theme)"
                  :key="idx"
                  class="tag"
                  :class="{ 'mobile': screenSize === 'mobile' }"
                >
                  #{{ tag }}
                </span>
              </div>

              <button class="solve-btn" :class="{ 'mobile': screenSize === 'mobile' }">
                {{ screenSize === 'mobile' ? '→' : 'Решать' }}
                <span v-if="screenSize !== 'mobile'" class="btn-arrow">→</span>
              </button>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ==================== БАЗОВЫЕ СТИЛИ ==================== */
.tasks-container {
  min-height: 100vh;
  background-color: #f8fafc;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  line-height: 1.5;
}

.tasks-content {
  max-width: 1280px;
  margin: 0 auto;
  padding: 16px;
}

/* ==================== ЗАГОЛОВОК ==================== */
.tasks-header {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 28px;
}

.header-text {
  flex: 1;
}

.title {
  font-size: 24px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.025em;
  margin-bottom: 8px;
  line-height: 1.2;
}

.description {
  color: #64748b;
  font-weight: 500;
  font-size: 14px;
  line-height: 1.6;
  max-width: 100%;
}

.tasks-counter {
  display: none;
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

/* ==================== ФИЛЬТРЫ ==================== */
.filters-container {
  background-color: white;
  padding: 16px;
  border-radius: 16px;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  transition: all 0.2s ease;
  margin-bottom: 24px;
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
  font-size: 18px;
  transition: color 0.2s ease;
}

.search-group:focus-within .search-icon {
  color: #4f46e5;
}

.search-input {
  width: 100%;
  padding: 12px 12px 12px 40px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  background-color: #f8fafc;
  color: #0f172a;
  font-size: 15px;
  font-weight: 500;
  outline: none;
  transition: all 0.2s ease;
  font-family: inherit;
}

.search-input:focus {
  background-color: white;
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.search-input::placeholder {
  color: #94a3b8;
}

.filter-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.select-wrapper {
  position: relative;
  flex: 1;
  min-width: 120px;
}

.filter-select {
  appearance: none;
  display: block;
  width: 100%;
  padding: 12px 36px 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  background-color: white;
  color: #334155;
  font-weight: 600;
  font-size: 14px;
  outline: none;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.filter-select.compact {
  padding: 10px 32px 10px 12px;
  font-size: 13px;
}

.filter-select:hover {
  border-color: #a5b4fc;
}

.filter-select:focus {
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.select-arrow {
  pointer-events: none;
  position: absolute;
  top: 50%;
  right: 12px;
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
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  background-color: white;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 18px;
  flex-shrink: 0;
}

.reset-btn.compact {
  width: auto;
  min-width: 60px;
  height: 44px;
  padding: 0 12px;
  font-size: 13px;
  font-weight: 600;
}

.reset-btn:hover {
  color: #ef4444;
  background-color: #fef2f2;
  border-color: #fecaca;
}

/* ==================== СООБЩЕНИЯ ОБ ОШИБКАХ ==================== */
.error-state {
  background-color: #fef2f2;
  border: 2px solid #fecaca;
  border-radius: 20px;
  padding: 24px;
  text-align: center;
  animation: fadeIn 0.5s ease-out;
  margin-top: 20px;
}

.error-icon {
  font-size: 40px;
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
  font-size: 14px;
  margin-bottom: 20px;
  line-height: 1.5;
}

.retry-btn {
  padding: 10px 24px;
  background-color: white;
  color: #dc2626;
  font-weight: 700;
  font-size: 14px;
  border-radius: 10px;
  border: 2px solid #fecaca;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.retry-btn:hover {
  background-color: #fef2f2;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* ==================== СЕТКА ЗАДАЧ ==================== */
.tasks-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 20px;
  margin-top: 24px;
}

/* ==================== СКЕЛЕТОНЫ ЗАГРУЗКИ ==================== */
.task-card-skeleton {
  background-color: white;
  border-radius: 20px;
  border: 1px solid #f1f5f9;
  padding: 20px;
  height: 260px;
  display: flex;
  flex-direction: column;
  animation: pulse 2s infinite;
}

.skeleton-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.skeleton-tag {
  height: 24px;
  width: 80px;
  background-color: #f1f5f9;
  border-radius: 9999px;
}

.skeleton-tag.mobile {
  width: 60px;
  height: 20px;
}

.skeleton-difficulty {
  height: 24px;
  width: 60px;
  background-color: #f1f5f9;
  border-radius: 9999px;
}

.skeleton-difficulty.mobile {
  width: 40px;
  height: 20px;
}

.skeleton-title {
  height: 28px;
  width: 75%;
  background-color: #f1f5f9;
  border-radius: 8px;
  margin-bottom: 16px;
}

.skeleton-title.mobile {
  height: 24px;
  width: 85%;
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

.skeleton-line.mobile {
  height: 14px;
}

.skeleton-line.short {
  width: 83%;
}

.skeleton-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #f8fafc;
}

.skeleton-tags {
  height: 24px;
  width: 80px;
  background-color: #f1f5f9;
  border-radius: 9999px;
}

.skeleton-tags.mobile {
  width: 60px;
  height: 20px;
}

.skeleton-button {
  height: 40px;
  width: 90px;
  background-color: #f1f5f9;
  border-radius: 12px;
}

.skeleton-button.mobile {
  height: 36px;
  width: 36px;
  border-radius: 10px;
}

/* ==================== ПУСТОЕ СОСТОЯНИЕ ==================== */
.empty-state {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  width: 80px;
  height: 80px;
  background-color: #f1f5f9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  margin-bottom: 20px;
}

.empty-title {
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 8px;
}

.empty-description {
  color: #64748b;
  font-size: 14px;
  max-width: 320px;
  margin-bottom: 20px;
  line-height: 1.5;
}

.reset-filters-btn {
  color: #4f46e5;
  font-weight: 700;
  background: none;
  border: none;
  cursor: pointer;
  text-decoration: underline;
  transition: color 0.2s ease;
  font-size: 14px;
  padding: 8px 0;
}

.reset-filters-btn:hover {
  color: #3730a3;
}

/* ==================== КАРТОЧКИ ЗАДАЧ ==================== */
.task-card {
  background-color: white;
  border-radius: 20px;
  border: 1px solid #f1f5f9;
  padding: 20px;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  height: 100%;
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

.subject-tag.mobile {
  padding: 4px 8px;
  font-size: 11px;
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
  border: 2px solid;
}

.difficulty-badge.mobile {
  padding: 4px 8px;
  font-size: 11px;
  min-width: 24px;
  justify-content: center;
}

.task-title {
  font-size: 18px;
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

.task-title.mobile {
  font-size: 16px;
  -webkit-line-clamp: 2;
}

.task-card:hover .task-title {
  color: #4f46e5;
}

.task-description {
  color: #6b7280;
  font-size: 14px;
  font-weight: 500;
  line-height: 1.6;
  flex: 1;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  margin-bottom: 20px;
}

.task-description.mobile {
  font-size: 13px;
  -webkit-line-clamp: 2;
}

.task-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-top: 20px;
  border-top: 1px solid #f8fafc;
}

.task-footer.mobile {
  gap: 8px;
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

.tag.mobile {
  font-size: 9px;
  padding: 3px 6px;
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

.solve-btn.mobile {
  padding: 8px;
  width: 40px;
  height: 40px;
  justify-content: center;
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

/* ==================== АНИМАЦИИ ==================== */

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* ==================== ТЁМНАЯ ТЕМА ==================== */

:root.dark .tasks-container {
  background-color: #0f172a;
  color: #f1f5f9;
}

:root.dark .title {
  color: #f8fafc;
}

:root.dark .description {
  color: #cbd5e1;
}

:root.dark .counter-badge {
  background-color: #1e293b;
  border-color: #334155;
  color: #cbd5e1;
}

:root.dark .filters-container {
  background-color: #1e293b;
  border-color: #334155;
}

:root.dark .search-input {
  background-color: #334155;
  border-color: #475569;
  color: #f1f5f9;
}

:root.dark .search-input:focus {
  background-color: #334155;
  border-color: #3b82f6;
}

:root.dark .search-input::placeholder {
  color: #94a3b8;
}

:root.dark .filter-select {
  background-color: #334155;
  border-color: #475569;
  color: #f1f5f9;
}

:root.dark .filter-select:hover {
  border-color: #60a5fa;
}

:root.dark .filter-select:focus {
  border-color: #3b82f6;
}

:root.dark .reset-btn {
  background-color: #334155;
  border-color: #475569;
  color: #cbd5e1;
}

:root.dark .reset-btn:hover {
  background-color: #475569;
  color: #f87171;
  border-color: #f87171;
}

:root.dark .task-card {
  background-color: #1e293b;
  border-color: #334155;
  color: #f1f5f9;
}

:root.dark .task-card:hover {
  box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.2);
}

:root.dark .subject-tag {
  background-color: #334155;
  color: #cbd5e1;
}

:root.dark .task-title {
  color: #f8fafc;
}

:root.dark .task-card:hover .task-title {
  color: #60a5fa;
}

:root.dark .task-description {
  color: #94a3b8;
}

:root.dark .task-footer {
  border-top-color: #334155;
}

:root.dark .tag {
  background-color: #334155;
  border-color: #475569;
  color: #cbd5e1;
}

:root.dark .solve-btn {
  background-color: #334155;
  color: #f1f5f9;
}

:root.dark .task-card:hover .solve-btn {
  background-color: #3b82f6;
}

:root.dark .empty-state {
  color: #f1f5f9;
}

:root.dark .empty-icon {
  background-color: #334155;
}

:root.dark .empty-title {
  color: #f8fafc;
}

:root.dark .empty-description {
  color: #cbd5e1;
}

:root.dark .reset-filters-btn {
  color: #60a5fa;
}

:root.dark .reset-filters-btn:hover {
  color: #93c5fd;
}

:root.dark .error-state {
  background-color: #7f1d1d;
  border-color: #991b1b;
  color: #fecaca;
}

:root.dark .error-title {
  color: #fca5a5;
}

:root.dark .error-message {
  color: #fecaca;
}

:root.dark .retry-btn {
  background-color: #1e293b;
  color: #fca5a5;
  border-color: #dc2626;
}

:root.dark .retry-btn:hover {
  background-color: #991b1b;
}

/* Skeleton loading */
:root.dark .task-card-skeleton,
:root.dark .skeleton-tag,
:root.dark .skeleton-difficulty,
:root.dark .skeleton-title,
:root.dark .skeleton-line,
:root.dark .skeleton-tags,
:root.dark .skeleton-button {
  background-color: #334155;
}


/* ==================== АДАПТИВНЫЕ СТИЛИ ==================== */

@media (max-width: 320px) {
  .tasks-content {
    padding: 12px;
  }

  .title {
    font-size: 22px;
  }

  .description {
    font-size: 13px;
  }

  .filters-container {
    padding: 12px;
    gap: 12px;
  }

  .search-input {
    padding: 10px 10px 10px 36px;
    font-size: 14px;
  }

  .search-icon {
    font-size: 16px;
    left: 10px;
  }

  .filter-select {
    padding: 10px 32px 10px 12px;
    font-size: 13px;
  }

  .reset-btn.compact {
    min-width: 56px;
    padding: 0 8px;
    font-size: 12px;
  }

  .task-card-skeleton,
  .task-card {
    padding: 16px;
  }

  .empty-icon {
    width: 64px;
    height: 64px;
    font-size: 28px;
  }

  .empty-title {
    font-size: 18px;
  }

  .empty-description {
    font-size: 13px;
  }
}


@media (min-width: 321px) and (max-width: 375px) {
  .tasks-content {
    padding: 14px;
  }

  .title {
    font-size: 23px;
  }

  .filter-select {
    min-width: 100px;
  }
}


@media (min-width: 376px) {
  .tasks-content {
    padding: 16px;
  }

  .title {
    font-size: 24px;
  }
}


@media (min-width: 640px) {
  .tasks-content {
    padding: 24px;
  }

  .title {
    font-size: 28px;
  }

  .description {
    font-size: 15px;
  }

  .filters-container {
    padding: 20px;
    border-radius: 20px;
  }

  .search-input {
    padding: 14px 14px 14px 44px;
    font-size: 16px;
  }

  .search-icon {
    font-size: 20px;
    left: 14px;
  }

  .filter-select {
    font-size: 15px;
  }

  .error-state {
    padding: 32px;
  }

  .empty-icon {
    width: 96px;
    height: 96px;
    font-size: 36px;
  }

  .empty-title {
    font-size: 22px;
  }

  .empty-description {
    font-size: 15px;
  }

  .task-card-skeleton,
  .task-card {
    padding: 24px;
    border-radius: 24px;
  }
}


@media (min-width: 768px) {
  .tasks-header {
    flex-direction: row;
    align-items: flex-end;
    justify-content: space-between;
    gap: 24px;
  }

  .tasks-counter {
    display: block;
  }

  .title {
    font-size: 32px;
  }

  .description {
    font-size: 16px;
  }

  .filters-container {
    flex-direction: row;
    align-items: center;
  }

  .filter-group {
    flex-wrap: nowrap;
  }

  .select-wrapper {
    min-width: 160px;
  }

  .tasks-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
  }
}


@media (min-width: 1024px) {
  .tasks-content {
    padding: 32px 40px;
  }

  .title {
    font-size: 36px;
  }

  .filters-container {
    padding: 24px;
  }

  .tasks-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}


@media (min-width: 1280px) {
  .tasks-content {
    padding: 40px;
    max-width: 1280px;
  }

  .title {
    font-size: 40px;
  }

  .description {
    font-size: 17px;
  }

  .tasks-grid {
    gap: 32px;
  }
}


@media (min-width: 1536px) {
  .tasks-content {
    max-width: 1440px;
    padding: 48px;
  }

  .title {
    font-size: 44px;
  }

  .description {
    font-size: 18px;
  }

  .tasks-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>
