<script setup>
import { ref, reactive, watch, onMounted, onUnmounted, shallowRef, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/api/axios' // Наш настроенный инстанс
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

const isAiMode = ref(false) // Активен ли режим решения
const aiTask = ref(null) // Объект сгенерированной задачи
const aiAnswer = ref('') // Ответ пользователя
const aiCheckLoading = ref(false)
const aiCheckResult = ref(null)
const aiIsSolved = ref(false)
const aiShowHint = ref(false)

// --- Filters State ---
const filters = reactive({
  search: route.query.search || '',
  subject: route.query.subject || '',
  difficulty: route.query.difficulty || '',
  tags: route.query.tags || '', // Храним выбранный тег
})

// Dropdown состояния
const dropdowns = reactive({
  subject: false,
  tags: false,
  difficulty: false
})

// Состояние для списка доступных тегов (зависит от предмета)
const availableTags = shallowRef([])
const tagsLoading = ref(false)

// --- Pagination State ---
const pagination = reactive({
  page: Number(route.query.page) || 1,
  limit: 32, // Лимит 32 задачи
})

// --- State (AI Mode) ---
const showAiMenu = ref(false)

const openAiMenu = () => {
  showAiMenu.value = true
}

// --- State (AI Mode Settings) ---
const aiSubject = ref('MATH') // По умолчанию Математика
const aiDifficulty = ref('EASY') // По умолчанию Легко
const aiLoading = ref(false) // Статус загрузки (крутилка на кнопке)

// Функция закрытия меню
const closeAiMenu = () => {
  showAiMenu.value = false
}

const generateAiTask = async () => {
  aiLoading.value = true

  // Сбрасываем состояния
  aiTask.value = null
  aiAnswer.value = ''
  aiCheckResult.value = null
  aiIsSolved.value = false
  aiShowHint.value = false

  try {
    const response = await api.get('/tasks/generate', {
      params: {
        subject: aiSubject.value,
        difficulty: aiDifficulty.value,
      },
      headers: { Authorization: `Bearer ${localStorage.getItem('user-token')}` },
    })

    aiTask.value = response.data
    showAiMenu.value = false // Закрываем меню
    isAiMode.value = true // Включаем режим задачи
  } catch (err) {
    console.error('AI Generation Error:', err)
    alert('ИИ устал или нет связи. Попробуйте позже.')
  } finally {
    aiLoading.value = false
  }
}

const exitAiMode = () => {
  isAiMode.value = false
  aiTask.value = null
}

// --- Функция проверки ответа ---
const submitAiAnswer = async () => {
  if (!aiAnswer.value) return

  aiCheckLoading.value = true
  aiCheckResult.value = null

  try {
    const response = await api.post(
      '/tasks/generated_task_check',
      {
        answer: aiAnswer.value,
      },
      { headers: { Authorization: `Bearer ${localStorage.getItem('user-token')}` } },
    )

    aiCheckResult.value = response.data
    if (response.data.is_correct) {
      aiIsSolved.value = true
    }
  } catch (err) {
    console.error(err)
    aiCheckResult.value = { is_correct: false, message: 'Ошибка проверки' }
  } finally {
    aiCheckLoading.value = false
  }
}

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

  if (Array.isArray(taskData.tags)) {
    rawTags = taskData.tags
  } else if (typeof taskData.theme === 'string') {
    rawTags = taskData.theme.split(',').map((t) => t.trim())
  }

  const slicedTags = rawTags.slice(0, screenSize.value === 'mobile' ? 2 : 3)

  return slicedTags.map((tagKey) => {
    const foundTag = constantsStore.tags.find((t) => t.key === tagKey)
    return foundTag ? foundTag.label : tagKey
  })
}

const getDifficultyColorClass = (diffKey) => {
  const key = diffKey ? diffKey.toUpperCase() : ''

  const map = {
    EASY: 'text-emerald-700 bg-emerald-50 border-emerald-200 dark:bg-emerald-200/40 dark:text-emerald-300 dark:border-emerald-800',
    MEDIUM:
      'text-amber-700 bg-amber-50 border-amber-200 dark:bg-amber-200/40 dark:text-amber-300 dark:border-amber-800',
    HARD: 'text-rose-700 bg-rose-50 border-rose-200 dark:bg-rose-200/40 dark:text-rose-300 dark:border-rose-800',
  }
  return (
    map[key] || 'text-slate-600 bg-slate-100 border-slate-200 dark:bg-slate-800 dark:text-slate-300'
  )
}

const getDifficultyLabel = (diffKey) => {
  return constantsStore.getDifficultyLabel(diffKey)
}

const getSubjectLabel = (subjKey) => {
  return constantsStore.getSubjectLabel(subjKey)
}

const navigateToTask = (id) => {
  const query = { ...route.query }
  delete query.id
  router.push({
    path: `/tasks/${id}`,
    query,
  })
}

// --- Dynamic Tags Logic ---

const updateAvailableTags = async () => {
  if (!filters.subject) {
    availableTags.value = constantsStore.tags
    return
  }

  tagsLoading.value = true
  try {
    const response = await api.get('/constants/tags_for_subject', {
      params: { subject: filters.subject },
    })

    const data = response.data
    if (Array.isArray(data)) {
      availableTags.value = data
    } else {
      availableTags.value = data.items || data.data || []
    }
  } catch (err) {
    console.warn('Не удалось загрузить теги, используем локальный фильтр', err)
    availableTags.value = constantsStore.tags
  } finally {
    tagsLoading.value = false
  }
}

// --- Dropdown Helpers ---
const toggleDropdown = (dropdownName) => {
  Object.keys(dropdowns).forEach(key => {
    if (key !== dropdownName) {
      dropdowns[key] = false
    }
  })
  dropdowns[dropdownName] = !dropdowns[dropdownName]
}

const closeAllDropdowns = () => {
  Object.keys(dropdowns).forEach(key => {
    dropdowns[key] = false
  })
}

const selectFilter = (type, value) => {
  filters[type] = value
  dropdowns[type] = false
  pagination.page = 1
  fetchTasks()
}

// --- Fetch Actions ---

const fetchTasks = async () => {
  if (abortController) abortController.abort()
  abortController = new AbortController()

  loading.value = true
  error.value = null

  try {
    const offset = (pagination.page - 1) * pagination.limit

    const params = {
      offset: offset,
      skip: offset,
      limit: pagination.limit,
      ...(filters.search ? { search: filters.search } : {}),
      ...(filters.subject ? { subject: filters.subject } : {}),
      ...(filters.difficulty ? { difficulty: filters.difficulty } : {}),
      ...(filters.tags ? { tag: filters.tags } : {}),
    }

    const headers = { Authorization: `Bearer ${localStorage.getItem('user-token')}` }

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
  } catch (err) {
    if (err.name !== 'CanceledError') {
      error.value = 'Ошибка загрузки данных. Проверьте соединение.'
    }
  } finally {
    setTimeout(() => {
      loading.value = false
    }, 300)
  }
}

const updateUrl = () => {
  const query = {}
  if (filters.search) query.search = filters.search
  if (filters.subject) query.subject = filters.subject
  if (filters.difficulty) query.difficulty = filters.difficulty
  if (filters.tags) query.tags = filters.tags
  if (pagination.page > 1) query.page = pagination.page

  router.replace({
    query,
    hash: route.hash,
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
  filters.tags = ''
  availableTags.value = constantsStore.tags
  pagination.page = 1
  closeAllDropdowns()
  fetchTasks()
}

// --- FIX: Client-Side Pagination Logic ---
const paginatedTasks = computed(() => {
  if (tasks.value.length > pagination.limit) {
    const start = (pagination.page - 1) * pagination.limit
    const end = start + pagination.limit
    return tasks.value.slice(start, end)
  }
  return tasks.value
})

// --- Watchers ---

watch(
  () => route.query,
  (newQuery) => {
    filters.search = newQuery.search || ''
    filters.subject = newQuery.subject || ''
    filters.difficulty = newQuery.difficulty || ''
    filters.tags = newQuery.tags || ''
    pagination.page = Number(newQuery.page) || 1

    fetchTasks()
  },
  { immediate: true },
)

watch(
  () => filters.subject,
  async () => {
    filters.tags = ''
    pagination.page = 1
    await updateAvailableTags()
    fetchTasks()
  },
)

watch(
  () => [filters.difficulty, filters.tags],
  () => {
    pagination.page = 1
    fetchTasks()
  },
)

watch(
  () => filters.search,
  () => {
    clearTimeout(searchTimeout)
    searchTimeout = setTimeout(() => {
      pagination.page = 1
      fetchTasks()
    }, 500)
  },
)

// --- Lifecycle ---

onMounted(async () => {
  updateScreenSize()
  window.addEventListener('resize', updateScreenSize)
  
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.dropdown-container') && !e.target.closest('.filter-dropdown-trigger')) {
      closeAllDropdowns()
    }
  })

  if (!constantsStore.isLoaded) {
    await constantsStore.fetchConstants()
  }

  await updateAvailableTags()

  await fetchTasks()
})

onUnmounted(() => {
  window.removeEventListener('resize', updateScreenSize)
  document.removeEventListener('click', closeAllDropdowns)
  if (abortController) abortController.abort()
  clearTimeout(searchTimeout)
})
</script>

<template>
  <div class="tasks-container">
    <!-- AI Menu Overlay -->
    <div v-if="showAiMenu" class="ai-menu-overlay" @click.self="closeAiMenu">
      <div class="ai-menu-card">
        <div class="ai-menu-header">
          <div class="ai-icon-large">🤖</div>
          <h2>Режим ИИ</h2>
          <button @click="closeAiMenu" class="close-btn">✕</button>
        </div>

        <p class="ai-desc">
          Нейросеть сгенерирует уникальную задачу специально для вас. Выберите параметры генерации:
        </p>

        <div class="ai-form">
          <div class="form-group">
            <label>Предмет</label>
            <div class="select-wrapper-ai">
              <select v-model="aiSubject" class="ai-select">
                <option v-for="subj in constantsStore.subjects" :key="subj.key" :value="subj.key">
                  {{ subj.label }}
                </option>
              </select>
              <div class="select-arrow">▼</div>
            </div>
          </div>

          <div class="form-group">
            <label>Сложность</label>
            <div class="select-wrapper-ai">
              <select v-model="aiDifficulty" class="ai-select">
                <option v-for="diff in constantsStore.difficulty" :key="diff.key" :value="diff.key">
                  {{ diff.label }}
                </option>
              </select>
              <div class="select-arrow">▼</div>
            </div>
          </div>

          <button @click="generateAiTask" :disabled="aiLoading" class="ai-generate-btn">
            <span v-if="aiLoading" class="spinner"></span>
            {{ aiLoading ? 'Генерация...' : 'Создать задачу' }}
          </button>
        </div>
      </div>
    </div>

    <!-- AI Task View -->
    <div v-if="isAiMode" class="ai-task-view">
      <div class="task-content">
        <button @click="exitAiMode" class="back-link">← Вернуться к списку</button>

        <div v-if="aiLoading && !aiTask" class="loading-placeholder">
          <div class="spinner-large"></div>
          <p>Нейросеть придумывает задачу...</p>
        </div>

        <div v-else-if="aiTask" class="task-card-full">
          <div class="task-header-full">
            <div class="task-header-overlay"></div>
            <div class="task-header-content-full">
              <div class="header-tags">
                <span class="subject-tag-full">{{ getSubjectLabel(aiTask.subject) }}</span>
                <span class="difficulty-tag-full">{{ getDifficultyLabel(aiTask.difficulty) }}</span>
                <span class="ai-badge">🤖 AI Generated</span>
              </div>
              <h1 class="task-title-full">{{ aiTask.title }}</h1>
            </div>
          </div>

          <div class="task-body-full">
            <p class="task-description-full">{{ aiTask.description }}</p>

            <div v-if="aiTask.hint" class="hint-section">
              <button @click="aiShowHint = !aiShowHint" class="hint-btn">
                {{ aiShowHint ? 'Скрыть подсказку' : '💡 Показать подсказку' }}
              </button>
              <div v-if="aiShowHint" class="hint-box">{{ aiTask.hint }}</div>
            </div>

            <div class="answer-section">
              <textarea
                v-model="aiAnswer"
                :disabled="aiIsSolved"
                placeholder="Введите ваш ответ..."
                class="ai-textarea"
                :class="{ correct: aiIsSolved, wrong: aiCheckResult && !aiCheckResult.is_correct }"
              ></textarea>

              <div
                v-if="aiCheckResult"
                class="result-msg"
                :class="aiCheckResult.is_correct ? 'success' : 'error'"
              >
                {{ aiCheckResult.message }}
              </div>

              <div class="ai-actions-footer">
                <button
                  v-if="aiIsSolved"
                  @click="openAiMenu"
                  class="ai-generate-btn"
                  style="background: var(--accent-color)"
                >
                  Сгенерировать еще одну
                </button>
                <button
                  v-else
                  @click="submitAiAnswer"
                  :disabled="aiCheckLoading"
                  class="ai-submit-btn"
                >
                  {{ aiCheckLoading ? 'Проверка...' : 'Отправить ответ' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Tasks View -->
    <div v-else class="tasks-content">
      <div class="tasks-header">
        <div class="header-text">
          <h1 class="title">Тренировочные задачи</h1>
          <p class="description">
            Улучшайте свои навыки, решая задачи разной сложности. Ваш прогресс сохраняется
            автоматически.
          </p>
        </div>

        <div class="header-actions">
          <div
            v-if="!loading && screenSize !== 'mobile' && screenSize !== 'sm'"
            class="tasks-counter"
          >
            <span class="counter-badge"> Всего задач: {{ totalTasks }} </span>
          </div>

          <button @click="openAiMenu" class="ai-mode-btn">
            <span class="ai-icon">✨</span>
            <span class="ai-text">Режим ИИ</span>
          </button>
        </div>
      </div>

      <div class="filters-container">
        <!-- Поиск -->
        <div class="search-row">
          <div class="search-group">
            <div class="search-icon">🔍</div>
            <input
              v-model="filters.search"
              type="text"
              placeholder="Поиск..."
              class="search-input"
            />
          </div>
        </div>

        <!-- Фильтры с dropdown -->
        <div class="filters-row">
          <div class="filter-group">
            <!-- Subject Dropdown -->
            <div class="dropdown-container">
              <button
                @click.stop="toggleDropdown('subject')"
                class="filter-dropdown-trigger"
                :class="{ 'active': dropdowns.subject }"
              >
                <span class="filter-label">
                  {{ filters.subject ? getSubjectLabel(filters.subject) : 'Все предметы' }}
                </span>
                <span class="dropdown-arrow">▼</span>
              </button>
              <div v-if="dropdowns.subject" class="dropdown-menu">
                <div
                  @click="selectFilter('subject', '')"
                  class="dropdown-item"
                  :class="{ 'selected': !filters.subject }"
                >
                  Все предметы
                </div>
                <div
                  v-for="subj in constantsStore.subjects"
                  :key="subj.key"
                  @click="selectFilter('subject', subj.key)"
                  class="dropdown-item"
                  :class="{ 'selected': filters.subject === subj.key }"
                >
                  {{ subj.label }}
                </div>
              </div>
            </div>

            <!-- Tags Dropdown -->
            <div class="dropdown-container">
              <button
                @click.stop="toggleDropdown('tags')"
                class="filter-dropdown-trigger"
                :class="{ 'active': dropdowns.tags }"
                :disabled="tagsLoading || constantsStore.loading"
              >
                <span class="filter-label">
                  {{ filters.tags ? (availableTags.find(t => t.key === filters.tags)?.label || filters.tags) : (tagsLoading ? 'Загрузка...' : 'Все темы') }}
                </span>
                <span class="dropdown-arrow">▼</span>
              </button>
              <div v-if="dropdowns.tags" class="dropdown-menu">
                <div
                  @click="selectFilter('tags', '')"
                  class="dropdown-item"
                  :class="{ 'selected': !filters.tags }"
                >
                  {{ tagsLoading ? 'Загрузка...' : 'Все темы' }}
                </div>
                <div
                  v-for="tag in availableTags"
                  :key="tag.key || tag"
                  @click="selectFilter('tags', tag.key || tag)"
                  class="dropdown-item"
                  :class="{ 'selected': filters.tags === (tag.key || tag) }"
                >
                  {{ tag.label || tag }}
                </div>
              </div>
            </div>

            <!-- Difficulty Dropdown -->
            <div class="dropdown-container">
              <button
                @click.stop="toggleDropdown('difficulty')"
                class="filter-dropdown-trigger"
                :class="{ 'active': dropdowns.difficulty }"
              >
                <span class="filter-label">
                  {{ filters.difficulty ? getDifficultyLabel(filters.difficulty) : 'Сложность' }}
                </span>
                <span class="dropdown-arrow">▼</span>
              </button>
              <div v-if="dropdowns.difficulty" class="dropdown-menu">
                <div
                  @click="selectFilter('difficulty', '')"
                  class="dropdown-item"
                  :class="{ 'selected': !filters.difficulty }"
                >
                  Сложность
                </div>
                <div
                  v-for="diff in constantsStore.difficulty"
                  :key="diff.key"
                  @click="selectFilter('difficulty', diff.key)"
                  class="dropdown-item"
                  :class="{ 'selected': filters.difficulty === diff.key }"
                >
                  {{ diff.label }}
                </div>
              </div>
            </div>

            <button
              @click="resetFilters"
              class="reset-btn"
              :class="{ compact: screenSize === 'mobile' }"
              :title="screenSize === 'mobile' ? '' : 'Сбросить фильтры'"
            >
              {{ screenSize === 'mobile' ? 'Сброс' : '✕' }}
            </button>
          </div>
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
          <div v-for="i in screenSize === 'mobile' ? 4 : 8" :key="i" class="task-card-skeleton">
            <div class="skeleton-header">
              <div class="skeleton-tag" :class="{ mobile: screenSize === 'mobile' }"></div>
              <div class="skeleton-difficulty" :class="{ mobile: screenSize === 'mobile' }"></div>
            </div>
            <div class="skeleton-title" :class="{ mobile: screenSize === 'mobile' }"></div>
            <div class="skeleton-description">
              <div class="skeleton-line" :class="{ mobile: screenSize === 'mobile' }"></div>
              <div class="skeleton-line short" :class="{ mobile: screenSize === 'mobile' }"></div>
            </div>
            <div class="skeleton-footer">
              <div class="skeleton-tags" :class="{ mobile: screenSize === 'mobile' }"></div>
              <div class="skeleton-button" :class="{ mobile: screenSize === 'mobile' }"></div>
            </div>
          </div>
        </template>

        <template v-else-if="paginatedTasks.length === 0">
          <div class="empty-state">
            <div class="empty-icon">🔍</div>
            <h3 class="empty-title">Задачи не найдены</h3>
            <p class="empty-description">
              Попробуйте изменить параметры поиска или сбросить фильтры.
            </p>
            <button @click="resetFilters" class="reset-filters-btn">Сбросить все фильтры</button>
          </div>
        </template>

        <template v-else>
          <div
            v-for="task in paginatedTasks"
            :key="task.id"
            class="task-card"
            @click="navigateToTask(task.id)"
          >
            <div class="task-accent"></div>

            <div class="task-header">
              <span class="subject-tag" :class="{ mobile: screenSize === 'mobile' }">
                {{ getSubjectLabel(task.subject) }}
              </span>

              <span
                class="difficulty-badge"
                :class="[
                  getDifficultyColorClass(task.difficulty),
                  { mobile: screenSize === 'mobile' },
                ]"
              >
                {{
                  screenSize === 'mobile'
                    ? getDifficultyLabel(task.difficulty).charAt(0)
                    : getDifficultyLabel(task.difficulty)
                }}
              </span>
            </div>

            <h3 class="task-title" :class="{ mobile: screenSize === 'mobile' }">
              {{ task.title }}
            </h3>

            <p class="task-description" :class="{ mobile: screenSize === 'mobile' }">
              {{ task.description }}
            </p>

            <div class="task-footer" :class="{ mobile: screenSize === 'mobile' }">
              <div class="task-tags">
                <span
                  v-for="(tagName, idx) in getDisplayTags(task)"
                  :key="idx"
                  class="tag"
                  :class="{ mobile: screenSize === 'mobile' }"
                >
                  #{{ tagName }}
                </span>
              </div>

              <button class="solve-btn" :class="{ mobile: screenSize === 'mobile' }">
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

        <span class="page-info"> Стр. {{ pagination.page }} </span>

        <button
          :disabled="pagination.page * pagination.limit >= totalTasks"
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
/* ==================== THEME CONFIGURATION ==================== */
.tasks-container {
  /* LIGHT THEME (Default) */
  --bg-page: #f8fafc;
  --bg-card: #ffffff;
  --bg-input: #f8fafc;
  --bg-tag: #f1f5f9;
  --bg-subject-tag: #f1f5f9; /* Фон тега предмета */
  --bg-counter: #ffffff; /* Фон счетчика */
  --bg-dropdown: #ffffff;
  --bg-dropdown-hover: #f8fafc;

  --text-primary: #0f172a;
  --text-secondary: #64748b;
  --text-tertiary: #94a3b8;
  --text-subject: #64748b; /* Цвет текста тега предмета */
  --text-counter: #64748b; /* Цвет текста счетчика */

  --border-light: #e2e8f0;
  --border-medium: #cbd5e1;

  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --shadow-hover: 0 10px 15px -3px rgba(79, 70, 229, 0.1);

  --accent-color: #4f46e5;
  --accent-hover: #4338ca;

  --btn-bg: white;
  --btn-text: #334155;
  --btn-border: #e2e8f0;
  --btn-hover-bg: #f8fafc;

  /* Светлые цвета скелетонов */
  --skeleton-base: #f1f5f9;
  --skeleton-highlight: #e2e8f0;
}

/* ==================== DARK THEME VARIABLES ==================== */
:global(.dark) .tasks-container {
  --bg-page: #0f172a;
  --bg-card: #1e293b;
  --bg-input: #334155;
  --bg-tag: #334155;
  --bg-subject-tag: #334155; /* Темный фон для тега предмета */
  --bg-counter: #1e293b; /* Темный фон для счетчика */
  --bg-dropdown: #1e293b;
  --bg-dropdown-hover: #334155;

  --text-primary: #f8fafc;
  --text-secondary: #cbd5e1;
  --text-tertiary: #94a3b8;
  --text-subject: #cbd5e1; /* Светлый текст для тега предмета в темной теме */
  --text-counter: #cbd5e1; /* Светлый текст для счетчика в темной теме */

  --border-light: #334155;
  --border-medium: #475569;

  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
  --shadow-hover: 0 10px 15px -3px rgba(59, 130, 246, 0.2);

  --accent-color: #60a5fa;
  --accent-hover: #3b82f6;

  --btn-bg: #1e293b;
  --btn-text: #cbd5e1;
  --btn-border: #334155;
  --btn-hover-bg: #334155;

  /* ТЕМНЫЕ скелетоны */
  --skeleton-base: #1e293b;
  --skeleton-highlight: #334155;
}

/* ==================== EXPLICIT DARK THEME OVERRIDES (как в первом файле) ==================== */
:root.dark .tasks-container {
  background-color: #0f172a;
  color: #f1f5f9;
}

:root.dark .filters-container {
  background-color: #1e293b;
  border-color: #334155;
}

:root.dark .search-input,
:root.dark .filter-select {
  background-color: #334155;
  border-color: #475569;
  color: #f1f5f9;
}

:root.dark .task-card {
  background-color: #1e293b;
  border-color: #334155;
}

:root.dark .task-card:hover {
  background-color: #1e293b;
  border-color: #3b82f6;
  box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.2);
}

:root.dark .task-title {
  color: #f1f5f9;
}

:root.dark .task-title:hover {
  color: #60a5fa;
}

:root.dark .task-description {
  color: #cbd5e1;
}

:root.dark .reset-btn {
  background-color: #1e293b;
  border-color: #334155;
  color: #cbd5e1;
}

:root.dark .reset-btn:hover {
  background-color: #334155;
  border-color: #475569;
  color: #f87171;
}

/* Темные скелетоны */
:root.dark .task-card-skeleton {
  background-color: #1e293b;
  border-color: #334155;
}

:root.dark .skeleton-tag,
:root.dark .skeleton-difficulty,
:root.dark .skeleton-title,
:root.dark .skeleton-line,
:root.dark .skeleton-tags,
:root.dark .skeleton-button {
  background-color: #334155;
}

:root.dark .loading-title,
:root.dark .loading-subtitle {
  background-color: #334155;
}

/* Темный счетчик задач */
:root.dark .counter-badge {
  background-color: #1e293b;
  border-color: #334155;
  color: #cbd5e1;
}

/* Темный тег предмета */
:root.dark .subject-tag {
  background-color: #334155;
  color: #cbd5e1;
  border-color: #475569;
}

/* Убрать синюю/красную рамку у всего окна в тёмной теме */
:global(.dark) {
  outline: none !important;
  border-color: inherit !important;
}

:global(.dark) *:focus {
  outline: none !important;
  box-shadow: none !important;
}

:global(.dark) body {
  border: none !important;
  outline: none !important;
}

/* ==================== BASIC LAYOUT ==================== */
.tasks-container {
  min-height: 100vh;
  background-color: var(--bg-page);
  color: var(--text-primary);
  font-family: 'Inter', sans-serif;
  line-height: 1.5;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.tasks-content {
  max-width: 1280px;
  margin: 0 auto;
  padding: 16px;
}

/* Убрать синюю рамку фокуса для всех элементов */
.tasks-container *:focus {
  outline: none;
}

.tasks-container button:focus,
.tasks-container input:focus,
.tasks-container select:focus,
.tasks-container textarea:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

/* Убрать красную рамку в тёмной теме */
:global(.dark) .tasks-container button:focus,
:global(.dark) .tasks-container input:focus,
:global(.dark) .tasks-container select:focus,
:global(.dark) .tasks-container textarea:focus {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
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
  background-color: var(--bg-counter);
  border: 1px solid var(--border-light);
  color: var(--text-counter);
  font-weight: 700;
  border-radius: 9999px;
  font-size: 14px;
  box-shadow: var(--shadow-sm);
}

/* ==================== FILTERS CONTAINER ==================== */
.filters-container {
  background-color: var(--bg-card);
  padding: 20px;
  border-radius: 16px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  gap: 16px;
  transition: all 0.2s ease;
  margin-bottom: 24px;
}

/* Поиск */
.search-row {
  width: 100%;
}

.search-group {
  position: relative;
  width: 100%;
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

/* Фильтры с dropdown */
.filters-row {
  width: 100%;
}

.filter-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  width: 100%;
}

/* Dropdown Styles */
.dropdown-container {
  position: relative;
  flex: 1;
  min-width: 140px;
  flex-shrink: 0;
}

@media (min-width: 1024px) {
  .dropdown-container:nth-child(1) {
    flex-basis: 200px;
    max-width: 220px;
  }
  .dropdown-container:nth-child(2) {
    flex-basis: 180px;
    max-width: 200px;
  }
  .dropdown-container:nth-child(3) {
    flex-basis: 150px;
    max-width: 170px;
  }
}

.filter-dropdown-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 12px 16px;
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
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
  text-align: left;
}

.filter-dropdown-trigger.compact {
  padding: 10px 12px;
  font-size: 13px;
}

.filter-dropdown-trigger:hover {
  border-color: var(--border-medium);
}

.filter-dropdown-trigger:focus,
.filter-dropdown-trigger.active {
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.filter-dropdown-trigger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background-color: var(--bg-tag);
}

.filter-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-arrow {
  font-size: 10px;
  margin-left: 8px;
  transition: transform 0.2s ease;
}

.filter-dropdown-trigger.active .dropdown-arrow {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  max-height: 300px;
  overflow-y: auto;
  background-color: var(--bg-dropdown);
  border: 2px solid var(--border-light);
  border-radius: 12px;
  box-shadow: var(--shadow-lg);
  z-index: 100;
  animation: fadeIn 0.2s ease-out;
}

.dropdown-item {
  padding: 12px 16px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  transition: all 0.2s ease;
  border-bottom: 1px solid var(--border-light);
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover {
  background-color: var(--bg-dropdown-hover);
  color: var(--text-primary);
}

.dropdown-item.selected {
  background-color: var(--accent-color);
  color: white;
  font-weight: 600;
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
  background-color: var(--bg-subject-tag);
  color: var(--text-subject);
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

/* FIX: ТЕМНАЯ РАМКА ДЛЯ ТЕГОВ В ТЕМНОЙ ТЕМЕ */
:global(.dark) .tag {
  border-color: #475569;
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

:global(.dark) .solve-btn {
  background-color: #334155;
  color: var(--text-primary);
  border: 1px solid #475569;
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

:global(.dark) .task-card:hover .solve-btn {
  background-color: #3b82f6;
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

/* ==================== AI BUTTON STYLES ==================== */
.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.ai-mode-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  color: white;
  border-radius: 9999px;
  font-weight: 700;
  font-size: 14px;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 10px rgba(124, 58, 237, 0.3);
}

.ai-mode-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(124, 58, 237, 0.4);
}

.ai-icon {
  font-size: 16px;
}

@media (min-width: 768px) {
  .header-actions {
    margin-left: auto;
  }
}

/* ==================== AI MENU STYLES ==================== */
.ai-menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(15, 23, 42, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  padding: 20px;
  animation: fadeIn 0.2s ease-out;
}

.ai-menu-card {
  background-color: white;
  border-radius: 24px;
  padding: 32px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 25px 50px -12px rgba(148, 163, 184, 0.3);
  border: 1px solid #f1f5f9;
  position: relative;
  animation: slideUp 0.3s ease-out;
  box-sizing: border-box;
}

.ai-menu-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.ai-icon-large {
  font-size: 28px;
}

.ai-menu-header h2 {
  font-size: 24px;
  font-weight: 800;
  color: #0f172a;
  flex: 1;
  margin: 0;
  letter-spacing: -0.025em;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #64748b;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  color: #ef4444;
  background-color: #fef2f2;
}

.ai-desc {
  color: #64748b;
  margin-bottom: 24px;
  line-height: 1.5;
  font-size: 15px;
  font-weight: 500;
}

.ai-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group label {
  display: block;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
  margin-bottom: 8px;
  letter-spacing: 0.05em;
}

.select-wrapper-ai {
  position: relative;
}

/* Вернули стрелочки к предметам в AI меню */
.ai-select {
  width: 100%;
  padding: 14px 40px 14px 16px;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
  background-color: #f8fafc;
  color: #0f172a;
  font-weight: 600;
  font-size: 15px;
  outline: none;
  appearance: none;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
}

.ai-select:focus {
  border-color: #4f46e5;
  background-color: white;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.select-arrow {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  font-size: 12px;
  color: #64748b;
}

.ai-generate-btn {
  width: 100%;
  padding: 16px;
  background-color: #4f46e5;
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
  transition: all 0.2s ease;
  box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.1);
  font-family: inherit;
}

.ai-generate-btn:hover:not(:disabled) {
  background-color: #4338ca;
  transform: translateY(-1px);
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.1);
}

.ai-generate-btn:active:not(:disabled) {
  transform: translateY(0);
}

.ai-generate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background-color: #6366f1;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* ==================== AI TASK VIEW ==================== */
.ai-task-view {
  min-height: 100vh;
  background-color: var(--bg-page);
  font-family: inherit;
  line-height: 1.5;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 0;
  position: static;
}

.task-content {
  width: 100%;
  max-width: 768px;
  margin: 0 auto;
  padding: 16px;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  text-decoration: none;
  padding: 16px 0;
  transition: color 0.2s ease;
  background: none;
  border: none;
  cursor: pointer;
  font-family: inherit;
  margin-bottom: 16px;
}

.back-link:hover {
  color: var(--accent-color);
}

.task-card-full {
  background-color: var(--bg-card);
  border-radius: 24px;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-light);
  overflow: hidden;
  margin-bottom: 24px;
}

.task-header-full {
  background-color: var(--bg-input);
  padding: 0;
  color: var(--text-primary);
  position: relative;
  overflow: hidden;
}

.task-header-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.1) 0%, rgba(124, 58, 237, 0.1) 100%);
  z-index: 1;
}

.task-header-content-full {
  position: relative;
  z-index: 10;
  padding: 24px;
}

.header-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
  align-items: center;
}

.subject-tag-full {
  padding: 6px 12px;
  background-color: var(--bg-subject-tag);
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-subject);
  border: 1px solid var(--border-light);
}

.difficulty-tag-full {
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border: 1px solid var(--border-light);
  background-color: var(--bg-tag);
  color: var(--text-secondary);
}

.ai-badge {
  padding: 6px 12px;
  background-color: rgba(245, 158, 11, 0.2);
  border: 1px solid rgba(245, 158, 11, 0.4);
  color: #f59e0b;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.task-title-full {
  font-size: 24px;
  font-weight: 900;
  letter-spacing: -0.025em;
  line-height: 1.3;
  margin: 0;
  color: var(--text-primary);
}

.task-body-full {
  padding: 24px;
}

.task-description-full {
  font-size: 16px;
  color: var(--text-secondary);
  font-weight: 500;
  line-height: 1.6;
  white-space: pre-wrap;
  margin-bottom: 24px;
}

.hint-section {
  margin-bottom: 24px;
}

.hint-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: none;
  border: 1px solid var(--border-light);
  padding: 8px 16px;
  border-radius: 12px;
  cursor: pointer;
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 13px;
  transition: all 0.2s ease;
  width: 100%;
  font-family: inherit;
}

.hint-btn:hover {
  background-color: var(--bg-input);
  color: var(--accent-color);
  border-color: var(--accent-color);
}

.hint-box {
  margin-top: 12px;
  background-color: #fffbeb;
  border: 1px solid #fcd34d;
  border-radius: 12px;
  padding: 16px;
  color: #92400e;
  font-size: 14px;
  font-weight: 500;
}

.answer-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.ai-textarea {
  width: 100%;
  background-color: var(--bg-input);
  border: 2px solid var(--border-light);
  border-radius: 12px;
  padding: 16px;
  font-size: 15px;
  color: var(--text-primary);
  font-weight: 500;
  outline: none;
  transition: all 0.2s ease;
  resize: vertical;
  min-height: 100px;
  font-family: inherit;
}

.ai-textarea:focus {
  border-color: var(--accent-color);
  background-color: var(--bg-card);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.ai-textarea:disabled {
  background-color: var(--bg-input);
  color: var(--text-tertiary);
  border-color: var(--border-light);
  cursor: not-allowed;
}

.ai-textarea.correct {
  border-color: #10b981;
  background-color: rgba(16, 185, 129, 0.05);
}

.ai-textarea.wrong {
  border-color: #f87171;
  background-color: rgba(248, 113, 113, 0.05);
}

.result-msg {
  padding: 16px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  display: flex;
  align-items: center;
  animation: fadeInUp 0.4s ease-out;
}

.result-msg.success {
  background-color: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.result-msg.error {
  background-color: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.ai-actions-footer {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-top: 8px;
}

.ai-submit-btn,
.ai-generate-btn {
  width: 100%;
  padding: 16px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 16px;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  font-family: inherit;
}

.ai-submit-btn,
.ai-generate-btn {
  background-color: var(--accent-color);
  color: white;
  box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.1);
}

.ai-submit-btn:hover:not(:disabled),
.ai-generate-btn:hover:not(:disabled) {
  background-color: var(--accent-hover);
  transform: translateY(-1px);
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.1);
}

.ai-submit-btn:active,
.ai-generate-btn:active {
  transform: translateY(0);
}

.ai-submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

.loading-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: var(--text-tertiary);
  animation: pulse 2s infinite;
}

.spinner-large {
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
  border: 4px solid var(--border-light);
  border-top-color: var(--accent-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* ==================== ANIMATIONS ==================== */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ==================== DARK THEME OVERRIDES (как в первом файле) ==================== */

:root.dark .ai-menu-card {
  background-color: #1e293b;
  border-color: #334155;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

:root.dark .ai-menu-header h2 {
  color: #f1f5f9;
}

:root.dark .close-btn {
  color: #94a3b8;
}

:root.dark .close-btn:hover {
  color: #fca5a5;
  background-color: #7f1d1d;
}

:root.dark .ai-desc {
  color: #cbd5e1;
}

:root.dark .form-group label {
  color: #94a3b8;
}

/* AI меню - тёмная тема с стрелочками */
:root.dark .ai-select {
  background-color: #334155;
  border-color: #475569;
  color: #f1f5f9;
}

:root.dark .ai-select:focus {
  border-color: #3b82f6;
  background-color: #334155;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

:root.dark .select-arrow {
  color: #94a3b8;
}

:root.dark .ai-generate-btn {
  background-color: #3b82f6;
}

:root.dark .ai-generate-btn:hover:not(:disabled) {
  background-color: #2563eb;
}

/* AI Task View Dark Theme */
:root.dark .ai-task-view {
  background-color: #0f172a;
  color: #f1f5f9;
}

:root.dark .task-card-full {
  background-color: #1e293b;
  border-color: #334155;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
}

:root.dark .task-header-full {
  background-color: #334155;
}

:root.dark .task-header-overlay {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(37, 99, 235, 0.15) 100%);
}

:root.dark .task-title-full {
  color: #f8fafc;
}

:root.dark .task-description-full {
  color: #cbd5e1;
}

:root.dark .subject-tag-full {
  background-color: rgba(255, 255, 255, 0.15);
  color: #93c5fd;
  border-color: rgba(255, 255, 255, 0.2);
}

:root.dark .difficulty-tag-full {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  color: #cbd5e1;
}

:root.dark .ai-badge {
  background-color: rgba(245, 158, 11, 0.15);
  border-color: rgba(245, 158, 11, 0.3);
  color: #fbbf24;
}

/* Подсказки Dark */
:root.dark .hint-btn {
  border-color: #475569;
  color: #94a3b8;
}

:root.dark .hint-btn:hover {
  background-color: #334155;
  color: #60a5fa;
  border-color: #3b82f6;
}

:root.dark .hint-box {
  background-color: #78350f;
  color: #fde68a;
  border-color: #92400e;
}

/* Инпуты Dark */
:root.dark .ai-textarea {
  background-color: #334155;
  border-color: #475569;
  color: #f1f5f9;
}

:root.dark .ai-textarea:focus {
  background-color: #334155;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

:root.dark .ai-textarea:disabled {
  background-color: #334155;
  color: #94a3b8;
  border-color: #475569;
}

:root.dark .ai-textarea.correct {
  border-color: #10b981;
  background-color: rgba(16, 185, 129, 0.15);
}

:root.dark .ai-textarea.wrong {
  border-color: #f87171;
  background-color: rgba(248, 113, 113, 0.15);
}

/* Результат Dark */
:root.dark .result-msg.success {
  background-color: #065f46;
  color: #a7f3d0;
  border-color: #047857;
}

:root.dark .result-msg.error {
  background-color: #7f1d1d;
  color: #fecaca;
  border-color: #991b1b;
}

/* Кнопки Dark */
:root.dark .ai-submit-btn,
:root.dark .ai-generate-btn {
  background-color: #3b82f6;
}

:root.dark .ai-submit-btn:hover:not(:disabled),
:root.dark .ai-generate-btn:hover:not(:disabled) {
  background-color: #2563eb;
}

/* Спиннер в темной теме */
:root.dark .spinner-large {
  border-color: rgba(255, 255, 255, 0.1);
  border-top-color: #60a5fa;
}

/* Dropdown Dark Theme */
:root.dark .dropdown-item.selected {
  background-color: #3b82f6;
}

/* Убрать синюю/красную рамку у всего окна в тёмной теме */
:root.dark *:focus {
  outline: none !important;
  box-shadow: none !important;
}

:root.dark .tasks-container button:focus,
:root.dark .tasks-container input:focus,
:root.dark .tasks-container select:focus,
:root.dark .tasks-container textarea:focus {
  outline: none !important;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2) !important;
}

/* ==================== RESPONSIVE ==================== */

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
    padding: 16px;
    gap: 12px;
  }
  
  .filter-dropdown-trigger {
    padding: 10px 12px;
    font-size: 13px;
  }
  
  .dropdown-item {
    padding: 10px 12px;
    font-size: 13px;
  }
  
  .reset-btn.compact {
    min-width: 56px;
    padding: 0 8px;
    font-size: 12px;
  }
  
  .task-content {
    padding: 12px;
  }
  
  .task-title-full {
    font-size: 20px;
  }
  
  .task-description-full {
    font-size: 14px;
  }
}

@media (min-width: 321px) and (max-width: 375px) {
  .tasks-content {
    padding: 14px;
  }
  
  .title {
    font-size: 23px;
  }
  
  .filter-dropdown-trigger {
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
  
  .filter-dropdown-trigger {
    font-size: 15px;
  }
  
  .task-content {
    padding: 24px;
  }
  
  .task-title-full {
    font-size: 28px;
  }
  
  .task-description-full {
    font-size: 17px;
  }
  
  .hint-btn {
    width: auto;
    display: inline-flex;
  }
  
  .ai-actions-footer {
    flex-direction: row;
    justify-content: flex-end;
  }
  
  .ai-submit-btn,
  .ai-generate-btn {
    width: auto;
    padding: 14px 32px;
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
  
  .tasks-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
  }
  
  .task-content {
    padding: 32px;
  }
  
  .task-card-full {
    border-radius: 32px;
  }
  
  .task-header-content-full {
    padding: 40px;
  }
  
  .task-body-full {
    padding: 40px;
  }
  
  .task-title-full {
    font-size: 32px;
  }
  
  .task-description-full {
    font-size: 18px;
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
  
  .task-content {
    max-width: 800px;
  }
  
  .task-card-full {
    border-radius: 40px;
    box-shadow: 0 25px 50px -12px rgba(148, 163, 184, 0.5);
  }
  
  .task-title-full {
    font-size: 36px;
  }
  
  .task-description-full {
    font-size: 19px;
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
  
  .task-content {
    max-width: 850px;
  }
  
  .task-card-full {
    border-radius: 48px;
  }
  
  .task-title-full {
    font-size: 40px;
  }
  
  .task-description-full {
    font-size: 20px;
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
  
  .task-content {
    max-width: 900px;
  }
  
  .task-title-full {
    font-size: 44px;
  }
  
  .task-description-full {
    font-size: 21px;
  }
}
</style>