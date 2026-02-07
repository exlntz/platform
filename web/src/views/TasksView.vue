<script setup>
import { ref, reactive, watch, onMounted, onUnmounted, shallowRef } from 'vue'
import { useRouter, useRoute } from 'vue-router'

import { useConstantsStore } from '@/pinia/ConstantsStore'

// --- Config & Store ---
const API_URL = '/tasks/'
const constantsStore = useConstantsStore()
const router = useRouter()
const route = useRoute()

// --- State ---
const tasks = shallowRef([])
const totalTasks = ref(0)
const loading = ref(true)
const error = ref(null)

// --- Filters State ---
const filters = reactive({
  search: route.query.search || '',
  subject: route.query.subject || '',
  difficulty: route.query.difficulty || '',
})

// --- Pagination State ---
const pagination = reactive({
  page: Number(route.query.page) || 1,
  limit: 12,
})

// --- Utils ---
let searchTimeout = null
let abortController = null

// --- Responsive ---
const screenSize = ref('mobile')
const updateScreenSize = () => {
  const width = window.innerWidth
  if (width < 640) screenSize.value = 'mobile'
  else if (width < 768) screenSize.value = 'sm'
  else if (width < 1024) screenSize.value = 'tablet'
  else if (width < 1280) screenSize.value = 'desktop'
  else screenSize.value = 'large'
}

// --- Helpers (Логика отображения) ---

const getDisplayTags = (taskData) => {
  let rawTags = []

  // Обработка и массива тегов, и строки (старый/новый формат)
  if (Array.isArray(taskData.tags)) {
    rawTags = taskData.tags
  } else if (typeof taskData.theme === 'string') {
    rawTags = taskData.theme.split(',').map(t => t.trim())
  }

  // Обрезаем количество для мобилок
  const slicedTags = rawTags.slice(0, screenSize.value === 'mobile' ? 2 : 3)

  // Маппим ключи в русские лейблы через Store
  return slicedTags.map(tagKey => {
    const foundTag = constantsStore.tags.find(t => t.key === tagKey)
    return foundTag ? foundTag.label : tagKey
  })
}

// Возвращаем Tailwind классы для цветов сложности,
// так как бейджи используют комбинацию CSS геометрии и Tailwind цветов
const getDifficultyColorClass = (diffKey) => {
  const key = diffKey ? diffKey.toUpperCase() : ''

  const map = {
    'EASY': 'text-emerald-700 bg-emerald-50 border-emerald-200 dark:bg-emerald-900/30 dark:text-emerald-400 dark:border-emerald-800',
    'MEDIUM': 'text-amber-700 bg-amber-50 border-amber-200 dark:bg-amber-900/30 dark:text-amber-400 dark:border-amber-800',
    'HARD': 'text-rose-700 bg-rose-50 border-rose-200 dark:bg-rose-900/30 dark:text-rose-400 dark:border-rose-800',
  }
  return map[key] || 'text-slate-600 bg-slate-100 border-slate-200 dark:bg-slate-800 dark:text-slate-400'
}

const getDifficultyLabel = (diffKey) => {
  return constantsStore.getDifficultyLabel(diffKey)
}

const getSubjectLabel = (subjKey) => {
  return constantsStore.getSubjectLabel(subjKey)
}

const navigateToTask = (id) => {
  router.push(`/tasks/${id}`)
}

// --- Fetch Actions ---

const fetchTasks = async () => {
  // Отмена предыдущего запроса
  if (abortController) abortController.abort()
  abortController = new AbortController()

  loading.value = true
  error.value = null

  try {
    const params = {
      skip: (pagination.page - 1) * pagination.limit,
      limit: pagination.limit,
      ...(filters.search && { search: filters.search }),
      ...(filters.subject && { subject: filters.subject }),
      ...(filters.difficulty && { difficulty: filters.difficulty }),
    }

    const token = localStorage.getItem('user-token') || localStorage.getItem('token')
    const headers = token ? { Authorization: `Bearer ${token}` } : {}

    const response = await api.get(API_URL, {
      params,
      headers,
      signal: abortController.signal,
    })

    const data = response.data

    if (Array.isArray(data)) {
      tasks.value = data
      totalTasks.value = data.length
    } else {
      tasks.value = data.items || data.data || []
      totalTasks.value = data.total || data.count || 0
    }

    updateUrl()

  } catch (err) {} finally {
    setTimeout(() => { loading.value = false }, 300)
  }
}

const updateUrl = () => {
  router.replace({
    query: {
      ...filters,
      page: pagination.page > 1 ? pagination.page : undefined,
    }
  })
}

const handlePageChange = (newPage) => {
  if (newPage < 1) return
  const maxPage = Math.ceil(totalTasks.value / pagination.limit)
  if (newPage > maxPage && maxPage > 0) return

  pagination.page = newPage
  fetchTasks()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const resetFilters = () => {
  filters.search = ''
  filters.subject = ''
  filters.difficulty = ''
  pagination.page = 1
  fetchTasks()
}

// --- Watchers ---

watch(
  () => [filters.subject, filters.difficulty],
  () => {
    pagination.page = 1
    fetchTasks()
  }
)

watch(
  () => filters.search,
  () => {
    clearTimeout(searchTimeout)
    searchTimeout = setTimeout(() => {
      pagination.page = 1
      fetchTasks()
    }, 500)
  }
)

// --- Lifecycle ---

onMounted(async () => {
  updateScreenSize()
  window.addEventListener('resize', updateScreenSize)

  if (!constantsStore.isLoaded) {
    await constantsStore.fetchConstants()
  }

  await fetchTasks()
})

onUnmounted(() => {
  window.removeEventListener('resize', updateScreenSize)
  if (abortController) abortController.abort()
  clearTimeout(searchTimeout)
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
          <span class="counter-badge">
            Всего задач: {{ totalTasks }}
          </span>
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
              :disabled="constantsStore.loading"
            >
              <option value="">Все предметы</option>
              <option
                v-for="subj in constantsStore.subjects"
                :key="subj.key"
                :value="subj.key"
              >
                {{ subj.label }}
              </option>
            </select>
            <div class="select-arrow">▼</div>
          </div>

          <div class="select-wrapper">
            <select
              v-model="filters.difficulty"
              class="filter-select"
              :class="{ 'compact': screenSize === 'mobile' }"
              :disabled="constantsStore.loading"
            >
              <option value="">Сложность</option>
              <option
                v-for="diff in constantsStore.difficulty"
                :key="diff.key"
                :value="diff.key"
              >
                {{ diff.label }}
              </option>
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
        <button @click="fetchTasks" class="retry-btn">
          Попробовать снова
        </button>
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

        <template v-else-if="tasks.length === 0">
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
            v-for="task in tasks"
            :key="task.id"
            class="task-card"
            @click="navigateToTask(task.id)"
          >
            <div class="task-accent"></div>

            <div class="task-header">
              <span class="subject-tag" :class="{ 'mobile': screenSize === 'mobile' }">
                {{ getSubjectLabel(task.subject) }}
              </span>

              <span
                class="difficulty-badge"
                :class="[getDifficultyColorClass(task.difficulty), { 'mobile': screenSize === 'mobile' }]"
              >
                {{ screenSize === 'mobile' ? getDifficultyLabel(task.difficulty).charAt(0) : getDifficultyLabel(task.difficulty) }}
              </span>
            </div>

            <h3 class="task-title" :class="{ 'mobile': screenSize === 'mobile' }">
              {{ task.title }}
            </h3>

            <p class="task-description" :class="{ 'mobile': screenSize === 'mobile' }">
              {{ task.description }}
            </p>

            <div class="task-footer" :class="{ 'mobile': screenSize === 'mobile' }">
              <div class="task-tags">
                <span
                  v-for="(tagName, idx) in getDisplayTags(task)"
                  :key="idx"
                  class="tag"
                  :class="{ 'mobile': screenSize === 'mobile' }"
                >
                  #{{ tagName }}
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

      <div v-if="!loading && totalTasks > 0" class="pagination-container">
        <button
          :disabled="pagination.page === 1"
          @click="handlePageChange(pagination.page - 1)"
          class="page-btn"
        >
          ← Назад
        </button>

        <span class="page-info">
          Стр. {{ pagination.page }}
        </span>

        <button
          :disabled="tasks.length < pagination.limit"
          @click="handlePageChange(pagination.page + 1)"
          class="page-btn"
        >
          Вперед →
        </button>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* ==================== THEME CONFIGURATION ====================
   Мы используем CSS Variables для управления темой.
   Это гарантирует, что стили переключаются мгновенно и корректно,
   независимо от специфичности селекторов.
*/
.tasks-container {
  /* LIGHT THEME (Default) */
  --bg-page: #f8fafc;
  --bg-card: #ffffff;
  --bg-input: #f8fafc;
  --bg-tag: #f1f5f9;

  --text-primary: #0f172a;
  --text-secondary: #64748b;
  --text-tertiary: #94a3b8;

  --border-light: #e2e8f0;
  --border-medium: #cbd5e1;

  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-hover: 0 10px 15px -3px rgba(79, 70, 229, 0.1);

  --accent-color: #4f46e5;
  --accent-hover: #4338ca;

  --btn-bg: white;
  --btn-text: #334155;
  --btn-border: #e2e8f0;
  --btn-hover-bg: #f8fafc;

  --skeleton-base: #f1f5f9;
  --skeleton-highlight: #e2e8f0;
}

/* DARK THEME OVERRIDES */
/* :global(.dark) позволяет "увидеть" класс .dark, который висит на <html> */
:global(.dark) .tasks-container {
  --bg-page: #0f172a;
  --bg-card: #1e293b;
  --bg-input: #334155;
  --bg-tag: #334155;

  --text-primary: #f8fafc;
  --text-secondary: #cbd5e1;
  --text-tertiary: #94a3b8;

  --border-light: #334155;
  --border-medium: #475569;

  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
  --shadow-hover: 0 10px 15px -3px rgba(59, 130, 246, 0.2);

  --accent-color: #60a5fa;
  --accent-hover: #3b82f6;

  --btn-bg: #1e293b;
  --btn-text: #cbd5e1;
  --btn-border: #334155;
  --btn-hover-bg: #334155;

  --skeleton-base: #1e293b;
  --skeleton-highlight: #334155;
}

/* ==================== BASIC LAYOUT ==================== */
.tasks-container {
  min-height: 100vh;
  background-color: var(--bg-page);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  line-height: 1.5;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.tasks-content {
  max-width: 1280px;
  margin: 0 auto;
  padding: 16px;
}

/* ==================== HEADER ==================== */
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
  color: var(--text-primary);
  letter-spacing: -0.025em;
  margin-bottom: 8px;
  line-height: 1.2;
}

.description {
  color: var(--text-secondary);
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
  background-color: var(--bg-card);
  border: 1px solid var(--border-light);
  color: var(--text-secondary);
  font-weight: 700;
  border-radius: 9999px;
  font-size: 14px;
  box-shadow: var(--shadow-sm);
}

/* ==================== FILTERS ==================== */
.filters-container {
  background-color: var(--bg-card);
  padding: 16px;
  border-radius: 16px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
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
  color: var(--text-tertiary);
  font-size: 18px;
  transition: color 0.2s ease;
}

.search-group:focus-within .search-icon {
  color: var(--accent-color);
}

.search-input {
  width: 100%;
  padding: 12px 12px 12px 40px;
  border: 2px solid var(--border-light);
  border-radius: 12px;
  background-color: var(--bg-input);
  color: var(--text-primary);
  font-size: 15px;
  font-weight: 500;
  outline: none;
  transition: all 0.2s ease;
  font-family: inherit;
}

.search-input:focus {
  background-color: var(--bg-card);
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.search-input::placeholder {
  color: var(--text-tertiary);
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
  border: 2px solid var(--border-light);
  border-radius: 12px;
  background-color: var(--bg-input);
  color: var(--text-primary);
  font-weight: 600;
  font-size: 14px;
  outline: none;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: var(--shadow-sm);
}

.filter-select.compact {
  padding: 10px 32px 10px 12px;
  font-size: 13px;
}

.filter-select:hover {
  border-color: var(--border-medium);
}

.filter-select:focus {
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.select-arrow {
  pointer-events: none;
  position: absolute;
  top: 50%;
  right: 12px;
  transform: translateY(-50%);
  color: var(--text-secondary);
  font-size: 12px;
}

.reset-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border: 2px solid var(--border-light);
  border-radius: 12px;
  background-color: var(--bg-card);
  color: var(--text-secondary);
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
  background-color: var(--bg-input);
  border-color: #fecaca;
}

/* ==================== ERROR STATE ==================== */
.error-state {
  background-color: #fef2f2;
  border: 2px solid #fecaca;
  border-radius: 20px;
  padding: 24px;
  text-align: center;
  animation: fadeIn 0.5s ease-out;
  margin-top: 20px;
}

:global(.dark) .error-state {
  background-color: #450a0a;
  border-color: #7f1d1d;
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

:global(.dark) .error-title {
  color: #fca5a5;
}

.error-message {
  color: #dc2626;
  font-size: 14px;
  margin-bottom: 20px;
  line-height: 1.5;
}

:global(.dark) .error-message {
  color: #fecaca;
}

.retry-btn {
  padding: 10px 24px;
  background-color: var(--bg-card);
  color: #dc2626;
  font-weight: 700;
  font-size: 14px;
  border-radius: 10px;
  border: 2px solid #fecaca;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: var(--shadow-sm);
}

:global(.dark) .retry-btn {
  border-color: #7f1d1d;
  color: #fca5a5;
  background-color: #1e293b;
}

.retry-btn:hover {
  box-shadow: var(--shadow-md);
}

/* ==================== TASKS GRID ==================== */
.tasks-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 20px;
  margin-top: 24px;
}

/* ==================== PAGINATION ==================== */
.pagination-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 40px;
  padding-bottom: 20px;
}

.page-btn {
  padding: 10px 20px;
  background-color: var(--btn-bg);
  border: 2px solid var(--btn-border);
  border-radius: 12px;
  color: var(--btn-text);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-btn:hover:not(:disabled) {
  border-color: var(--accent-color);
  color: var(--accent-color);
  background-color: var(--btn-hover-bg);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: var(--bg-input);
}

.page-info {
  font-weight: 600;
  color: var(--text-secondary);
}

/* ==================== SKELETONS ==================== */
.task-card-skeleton {
  background-color: var(--bg-card);
  border-radius: 20px;
  border: 1px solid var(--border-light);
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
  background-color: var(--skeleton-base);
  border-radius: 9999px;
}

.skeleton-tag.mobile {
  width: 60px;
  height: 20px;
}

.skeleton-difficulty {
  height: 24px;
  width: 60px;
  background-color: var(--skeleton-base);
  border-radius: 9999px;
}

.skeleton-difficulty.mobile {
  width: 40px;
  height: 20px;
}

.skeleton-title {
  height: 28px;
  width: 75%;
  background-color: var(--skeleton-base);
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
  background-color: var(--skeleton-base);
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
  border-top: 1px solid var(--border-light);
}

.skeleton-tags {
  height: 24px;
  width: 80px;
  background-color: var(--skeleton-base);
  border-radius: 9999px;
}

.skeleton-tags.mobile {
  width: 60px;
  height: 20px;
}

.skeleton-button {
  height: 40px;
  width: 90px;
  background-color: var(--skeleton-base);
  border-radius: 12px;
}

.skeleton-button.mobile {
  height: 36px;
  width: 36px;
  border-radius: 10px;
}

/* ==================== EMPTY STATE ==================== */
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
  background-color: var(--bg-tag);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  margin-bottom: 20px;
  color: var(--text-tertiary);
}

.empty-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-description {
  color: var(--text-secondary);
  font-size: 14px;
  max-width: 320px;
  margin-bottom: 20px;
  line-height: 1.5;
}

.reset-filters-btn {
  color: var(--accent-color);
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
  color: var(--accent-hover);
}

/* ==================== TASK CARD ==================== */
.task-card {
  background-color: var(--bg-card);
  border-radius: 20px;
  border: 1px solid var(--border-light);
  padding: 20px;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: var(--shadow-sm);
  height: 100%;
}

.task-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-hover);
  border-color: var(--accent-color);
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
  background-color: var(--bg-tag);
  color: var(--text-secondary);
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
  color: var(--text-primary);
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
  color: var(--accent-color);
}

.task-description {
  color: var(--text-secondary);
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
  border-top: 1px solid var(--border-light);
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
  color: var(--text-secondary);
  background-color: var(--bg-tag);
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid var(--border-light);
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
  background-color: #0f172a; /* Кнопка всегда темная по умолчанию в светлой теме */
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

:global(.dark) .solve-btn {
  background-color: var(--bg-tag);
  color: var(--text-primary);
  border: 1px solid var(--border-light);
}

.solve-btn.mobile {
  padding: 8px;
  width: 40px;
  height: 40px;
  justify-content: center;
}

.task-card:hover .solve-btn {
  background-color: var(--accent-color);
  color: white;
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.2);
  border-color: transparent;
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

/* ==================== ANIMATIONS ==================== */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* ==================== RESPONSIVE ==================== */

@media (max-width: 320px) {
  .tasks-content { padding: 12px; }
  .title { font-size: 22px; }
  .description { font-size: 13px; }
  .filters-container { padding: 12px; gap: 12px; }
  .search-input { padding: 10px 10px 10px 36px; font-size: 14px; }
  .search-icon { font-size: 16px; left: 10px; }
  .filter-select { padding: 10px 32px 10px 12px; font-size: 13px; }
  .reset-btn.compact { min-width: 56px; padding: 0 8px; font-size: 12px; }
  .task-card-skeleton, .task-card { padding: 16px; }
  .empty-icon { width: 64px; height: 64px; font-size: 28px; }
  .empty-title { font-size: 18px; }
  .empty-description { font-size: 13px; }
}

@media (min-width: 321px) and (max-width: 375px) {
  .tasks-content { padding: 14px; }
  .title { font-size: 23px; }
  .filter-select { min-width: 100px; }
}

@media (min-width: 376px) {
  .tasks-content { padding: 16px; }
  .title { font-size: 24px; }
}

@media (min-width: 640px) {
  .tasks-content { padding: 24px; }
  .title { font-size: 28px; }
  .description { font-size: 15px; }
  .filters-container { padding: 20px; border-radius: 20px; }
  .search-input { padding: 14px 14px 14px 44px; font-size: 16px; }
  .search-icon { font-size: 20px; left: 14px; }
  .filter-select { font-size: 15px; }
  .error-state { padding: 32px; }
  .empty-icon { width: 96px; height: 96px; font-size: 36px; }
  .empty-title { font-size: 22px; }
  .empty-description { font-size: 15px; }
  .task-card-skeleton, .task-card { padding: 24px; border-radius: 24px; }
}

@media (min-width: 768px) {
  .tasks-header { flex-direction: row; align-items: flex-end; justify-content: space-between; gap: 24px; }
  .tasks-counter { display: block; }
  .title { font-size: 32px; }
  .description { font-size: 16px; }
  .filters-container { flex-direction: row; align-items: center; }
  .filter-group { flex-wrap: nowrap; }
  .select-wrapper { min-width: 160px; }
  .tasks-grid { grid-template-columns: repeat(2, 1fr); gap: 24px; }
}

@media (min-width: 1024px) {
  .tasks-content { padding: 32px 40px; }
  .title { font-size: 36px; }
  .filters-container { padding: 24px; }
  .tasks-grid { grid-template-columns: repeat(3, 1fr); }
}

@media (min-width: 1280px) {
  .tasks-content { padding: 40px; max-width: 1280px; }
  .title { font-size: 40px; }
  .description { font-size: 17px; }
  .tasks-grid { gap: 32px; }
}

@media (min-width: 1536px) {
  .tasks-content { max-width: 1440px; padding: 48px; }
  .title { font-size: 44px; }
  .description { font-size: 18px; }
  .tasks-grid { grid-template-columns: repeat(4, 1fr); }
}
</style>
