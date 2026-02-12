<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import api from '@/api/axios.js'
import { useConstantsStore } from '@/pinia/ConstantsStore.js'
import { useNotificationStore } from '@/pinia/NotificationStore.js'
import { useConfirm } from '@/composables/useConfirm'

const { confirm } = useConfirm()
const notify = useNotificationStore()
const constants = useConstantsStore()

const loading = ref(false)
const tasks = ref([])
const showTaskModal = ref(false)
const isEditMode = ref(false)
const showExportMenu = ref(false)

const availableTags = ref([])

const taskForm = ref({
  title: '',
  description: '',
  subject: '',
  tags: [],
  difficulty: 'EASY',
  correct_answer: '',
  hint: '',
})
const currentEditId = ref(null)
const fileInput = ref(null)

const sortKey = ref('id')
const sortOrder = ref('asc')

const sortedTasks = computed(() => {
  return [...tasks.value].sort((a, b) => {
    let modifier = sortOrder.value === 'asc' ? 1 : -1
    let valA = a[sortKey.value]
    let valB = b[sortKey.value]

    if (sortKey.value === 'difficulty') {
      const weights = { EASY: 1, MEDIUM: 2, HARD: 3 }
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


const fetchTasks = async () => {
  loading.value = true
  try {
    const response = await api.get('/tasks/')
    tasks.value = response.data
  } catch (err) {
    notify.show('Ошибка загрузки задач')
  } finally {
    loading.value = false
  }
}

const fetchTagsForSubject = async (subject) => {
  if (!subject) {
    availableTags.value = []
    return
  }
  try {
    const response = await api.get('/constants/tags_for_subject', { params: { subject } })
    availableTags.value = response.data
  } catch (err) {
    console.error('Не удалось загрузить теги:', err)
    availableTags.value = []
  }
}


const openCreateModal = () => {
  isEditMode.value = false
  currentEditId.value = null
  taskForm.value = {
    title: '',
    description: '',
    subject: '',
    tags: [],
    difficulty: 'EASY',
    correct_answer: '',
    hint: '',
  }
  availableTags.value = []
  showTaskModal.value = true
}

const openEditModal = async (task) => {
  isEditMode.value = true
  currentEditId.value = task.id

  taskForm.value = { ...task, tags: task.tags || [] }

  if (task.subject) {
    await fetchTagsForSubject(task.subject)
  }

  showTaskModal.value = true

  try {
    const { data } = await api.get(`/admin/tasks/${task.id}/get`)
    taskForm.value = { ...data, tags: data.tags || [] }
  } catch (e) {
    console.error('API Error:', e)
    notify.show('Ошибка загрузки деталей задачи')
  }
}

const saveTask = async () => {
  try {
    const url = isEditMode.value
      ? `/admin/tasks/${currentEditId.value}/change`
      : '/admin/tasks/create'
    const method = isEditMode.value ? 'patch' : 'post'

    await api[method](url, taskForm.value)

    notify.show(isEditMode.value ? 'Задача обновлена!' : 'Задача создана!')
    showTaskModal.value = false
    fetchTasks()
  } catch (err) {
    console.error(err)
    notify.show('Ошибка сохранения: ' + (err.response?.data?.detail || err.message))
  }
}

const deleteTask = async (taskId) => {
  const isConfirmed = await confirm({
    title: 'Удалить задачу?',
    message: `Вы уверены, что хотите удалить задачу #${taskId}? Это действие нельзя будет отменить.`,
    confirmText: 'Удалить',
    cancelText: 'Отмена',
    isDanger: true,
  })

  if (!isConfirmed) return

  try {
    await api.delete(`/admin/tasks/${taskId}/delete`)
    tasks.value = tasks.value.filter((t) => t.id !== taskId)
    notify.show('Задача удалена')
  } catch (err) {
    console.error(err)
    notify.show('Ошибка удаления: ' + (err.response?.data?.detail || err.message))
  }
}


const triggerImport = () => fileInput.value.click()

const handleImport = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  const formData = new FormData()
  formData.append('file', file)

  try {
    loading.value = true
    const response = await api.post('/admin/tasks/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    notify.show(
      `Импорт завершен!\nСоздано: ${response.data.created}\nОбновлено: ${response.data.updated}`,
    )
    fetchTasks()
  } catch (err) {
    console.error('API Error:', err)
    notify.show('Ошибка импорта: ' + (err.response?.data?.detail || err.message))
  } finally {
    loading.value = false
    event.target.value = ''
  }
}

const toggleExportMenu = () => {
  showExportMenu.value = !showExportMenu.value
}

const exportTasks = async (format) => {
  showExportMenu.value = false
  try {
    const response = await api.get('/admin/tasks/export', {
      params: { format: format },
      responseType: 'blob',
    })

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    const extension = format === 'csv' ? 'csv' : 'json'
    link.setAttribute(
      'download',
      `tasks_export_${new Date().toISOString().slice(0, 10)}.${extension}`,
    )
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (err) {
    console.error('API Error:', err)
    notify.show('Ошибка экспорта')
  }
}


const toggleTag = (tagKey) => {
  const index = taskForm.value.tags.indexOf(tagKey)
  if (index === -1) taskForm.value.tags.push(tagKey)
  else taskForm.value.tags.splice(index, 1)
}

const onSubjectChange = () => {
  taskForm.value.tags = []
}

watch(
  () => taskForm.value.subject,
  (newSubject) => {
    if (newSubject) {
      fetchTagsForSubject(newSubject)
    } else {
      availableTags.value = []
    }
  },
)

onMounted(() => {
  fetchTasks()
  if (constants.subjects.length === 0) constants.fetchConstants()

  window.addEventListener('click', (e) => {
    if (!e.target.closest('.export-wrapper')) {
      showExportMenu.value = false
    }
  })
})
</script>

<template>
  <div class="tasks-tab">
    <div class="tab-header tasks-tab-header">
      <h1>Управление задачами</h1>
      <div class="tasks-actions">
        <input
          type="file"
          ref="fileInput"
          class="file-upload"
          accept=".json,.csv"
          @change="handleImport"
        />

        <button @click="triggerImport" class="action-text-btn import-btn">📥 Импорт</button>

        <div class="export-wrapper">
          <button @click="toggleExportMenu" class="action-text-btn export-btn">📤 Экспорт</button>
          <div v-if="showExportMenu" class="export-menu">
            <button @click="exportTasks('json')" class="export-item">JSON</button>
            <button @click="exportTasks('csv')" class="export-item">CSV</button>
          </div>
        </div>

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
              ID
              <span v-if="sortKey === 'id'" class="sort-indicator">{{
                sortOrder === 'asc' ? '↑' : '↓'
              }}</span>
            </th>
            <th @click="sortBy('title')" class="sortable-column task-column">
              Задача
              <span v-if="sortKey === 'title'" class="sort-indicator">{{
                sortOrder === 'asc' ? '↑' : '↓'
              }}</span>
            </th>
            <th @click="sortBy('subject')" class="sortable-column">
              Предмет
              <span v-if="sortKey === 'subject'" class="sort-indicator">{{
                sortOrder === 'asc' ? '↑' : '↓'
              }}</span>
            </th>
            <th @click="sortBy('difficulty')" class="sortable-column">
              Сложность
              <span v-if="sortKey === 'difficulty'" class="sort-indicator">{{
                sortOrder === 'asc' ? '↑' : '↓'
              }}</span>
            </th>
            <th class="answer-column">Ответ</th>
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
              <span class="subject-badge">{{ constants.getSubjectLabel(task.subject) }}</span>
            </td>
            <td>
              <span class="difficulty-badge" :class="task.difficulty.toLowerCase()">{{
                constants.getDifficultyLabel(task.difficulty)
              }}</span>
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
    </div>

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
              <select
                v-model="taskForm.subject"
                required
                class="form-select"
                @change="onSubjectChange"
              >
                <option value="" disabled>Выберите предмет</option>
                <option v-for="s in constants.subjects" :key="s.key" :value="s.key">
                  {{ s.label }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Сложность</label>
              <select v-model="taskForm.difficulty" required class="form-select">
                <option v-for="d in constants.difficulties" :key="d.key" :value="d.key">
                  {{ d.label }}
                </option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Название</label>
            <input v-model="taskForm.title" required class="form-input" />
          </div>

          <div class="form-group">
            <label class="form-label">Теги</label>
            <div class="tags-selector" v-if="availableTags.length > 0">
              <button
                type="button"
                v-for="tag in availableTags"
                :key="tag.key"
                @click="toggleTag(tag.key)"
                class="tag-choice-btn"
                :class="{ active: taskForm.tags.includes(tag.key) }"
              >
                {{ tag.label }}
                <span v-if="taskForm.tags.includes(tag.key)" class="tag-check">✓</span>
              </button>
            </div>
            <div v-else class="no-tags-hint">
              {{ taskForm.subject ? 'Нет тегов для этого предмета' : 'Сначала выберите предмет' }}
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Подсказка</label>
            <textarea v-model="taskForm.hint" rows="2" class="form-textarea"></textarea>
          </div>
          <div class="form-group">
            <label class="form-label">Условие</label>
            <textarea
              v-model="taskForm.description"
              required
              rows="4"
              class="form-textarea"
            ></textarea>
          </div>
          <div class="form-group">
            <label class="form-label">Ответ</label>
            <input v-model="taskForm.correct_answer" required class="form-input answer-field" />
          </div>
          <div class="form-submit">
            <button type="submit" class="submit-btn">
              {{ isEditMode ? 'Сохранить изменения' : 'Создать задачу' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
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
:root.dark .tab-header h1 {
  color: #f8fafc;
}

.table-wrapper {
  background-color: white;
  border-radius: 20px;
  box-shadow: 0 10px 15px -3px rgba(148, 163, 184, 0.2);
  border: 1px solid #f1f5f9;
  overflow: auto;
  max-width: 100%;
}
:root.dark .table-wrapper {
  background-color: #1e293b;
  border-color: #334155;
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
  align-items: center;
}
.file-upload {
  display: none;
}

/* Action Text Buttons (Import/Export) */
.action-text-btn {
  padding: 8px 16px;
  background-color: white;
  border: 1px solid #e2e8f0;
  color: #475569;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}
.action-text-btn:hover {
  background-color: #f8fafc;
  color: #0f172a;
}
:root.dark .action-text-btn {
  background-color: #334155;
  border-color: #475569;
  color: #cbd5e1;
}
:root.dark .action-text-btn:hover {
  background-color: #475569;
  color: white;
}

/* Export Menu Wrapper */
.export-wrapper {
  position: relative;
}
.export-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 4px;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  z-index: 50;
  min-width: 100px;
}
:root.dark .export-menu {
  background-color: #1e293b;
  border-color: #475569;
}
.export-item {
  display: block;
  width: 100%;
  text-align: left;
  padding: 8px 16px;
  background: none;
  border: none;
  font-size: 13px;
  font-weight: 600;
  color: #334155;
  cursor: pointer;
}
.export-item:hover {
  background-color: #f1f5f9;
}
:root.dark .export-item {
  color: #cbd5e1;
}
:root.dark .export-item:hover {
  background-color: #334155;
}

.create-btn {
  padding: 8px 16px;
  background-color: #4f46e5;
  color: white;
  border-radius: 8px;
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
:root.dark .create-btn {
  background-color: #3b82f6;
  color: white;
}
.create-btn:hover {
  background-color: #4338ca;
}
:root.dark .create-btn:hover {
  background-color: #2563eb;
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
:root.dark .tasks-table {
  background-color: #1e293b;
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
:root.dark .table-head {
  background-color: #334155;
  color: #cbd5e1;
  border-bottom-color: #475569;
}

.table-head th {
  padding: 16px;
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
.table-row {
  transition: background-color 0.2s ease;
  border-bottom: 1px solid #f8fafc;
}
:root.dark .table-row {
  border-bottom-color: #334155;
}
.task-row:hover {
  background-color: #f8fafc;
}
:root.dark .task-row:hover {
  background-color: #334155;
}

.table-row td {
  padding: 16px;
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
:root.dark .task-title {
  color: #f1f5f9;
}

.task-description {
  font-size: 11px;
  color: #64748b;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
:root.dark .task-description {
  color: #94a3b8;
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
:root.dark .subject-badge {
  background-color: #334155;
  color: #cbd5e1;
  border-color: #475569;
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
:root.dark .difficulty-badge.easy {
  background-color: #064e3b;
  color: #a7f3d0;
  border-color: #065f46;
}

.difficulty-badge.medium {
  color: #d97706;
  background-color: #fef3c7;
  border-color: #fde68a;
}
:root.dark .difficulty-badge.medium {
  background-color: #78350f;
  color: #fcd34d;
  border-color: #92400e;
}

.difficulty-badge.hard {
  color: #dc2626;
  background-color: #fee2e2;
  border-color: #fecaca;
}
:root.dark .difficulty-badge.hard {
  background-color: #7f1d1d;
  color: #fecaca;
  border-color: #991b1b;
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
.actions-header {
  text-align: right;
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
:root.dark .action-icon {
  background-color: #334155;
  border-color: #475569;
  color: #94a3b8;
}

.action-icon:hover {
  transform: scale(0.9);
}
:root.dark .action-icon:hover {
  background-color: #475569;
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
:root.dark .modal-overlay {
  background-color: rgba(0, 0, 0, 0.7);
}

.task-modal {
  background-color: white;
  border-radius: 20px;
  width: 100%;
  max-width: 600px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.25);
  padding: 24px;
  border: 1px solid #f1f5f9;
  max-height: 90vh;
  overflow-y: auto;
  animation: fadeInUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
:root.dark .task-modal {
  background-color: #1e293b;
  border-color: #334155;
  color: #f1f5f9;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f8fafc;
}
:root.dark .modal-header {
  border-bottom-color: #334155;
}
.modal-header h2 {
  font-size: 20px;
  font-weight: 900;
  color: #0f172a;
  line-height: 1.2;
}
:root.dark .modal-header h2 {
  color: #f8fafc;
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
:root.dark .close-modal {
  background-color: #334155;
  color: #94a3b8;
}
.close-modal:hover {
  background-color: #e2e8f0;
  color: #475569;
}
:root.dark .close-modal:hover {
  background-color: #475569;
  color: #cbd5e1;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
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
:root.dark .form-label {
  color: #cbd5e1;
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
:root.dark .form-select,
:root.dark .form-input,
:root.dark .form-textarea {
  background-color: #334155;
  border-color: #475569;
  color: #f1f5f9;
}

.disabled-input {
  opacity: 0.6;
  background-color: #e2e8f0;
  cursor: not-allowed;
}
:root.dark .disabled-input {
  background-color: #475569;
  color: #94a3b8;
}

.form-select:focus,
.form-input:focus,
.form-textarea:focus {
  background-color: white;
  border-color: #4f46e5;
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.1);
}
:root.dark .form-select:focus,
:root.dark .form-input:focus,
:root.dark .form-textarea:focus {
  background-color: #334155;
  border-color: #3b82f6;
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
:root.dark .submit-btn {
  background-color: #3b82f6;
}
.submit-btn:hover {
  background-color: #4338ca;
}
:root.dark .submit-btn:hover {
  background-color: #2563eb;
}
.submit-btn:active {
  transform: scale(0.98);
}

/* --- TAGS SELECTOR --- */
.tags-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.tag-choice-btn {
  padding: 6px 12px;
  border-radius: 20px;
  border: 1px solid #e2e8f0;
  background-color: white;
  color: #64748b;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 4px;
}
:root.dark .tag-choice-btn {
  background-color: #334155;
  border-color: #475569;
  color: #cbd5e1;
}

.tag-choice-btn:hover {
  background-color: #f8fafc;
  border-color: #cbd5e1;
}
:root.dark .tag-choice-btn:hover {
  background-color: #475569;
}

.tag-choice-btn.active {
  background-color: #e0e7ff;
  color: #4f46e5;
  border-color: #4f46e5;
}
:root.dark .tag-choice-btn.active {
  background-color: #1e3a8a;
  border-color: #3b82f6;
  color: #93c5fd;
}

.tag-check {
  font-weight: 900;
}
.no-tags-hint {
  font-size: 12px;
  color: #94a3b8;
  font-style: italic;
}

/* Animations */
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

/* Adaptive */
@media (max-width: 360px) {
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
  .task-modal {
    padding: 20px;
  }
  .modal-header h2 {
    font-size: 18px;
  }
}
@media (min-width: 481px) {
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
  .form-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .task-modal {
    max-width: 600px;
  }
  .tasks-table {
    min-width: auto;
  }
}
@media (min-width: 769px) {
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
  .tab-header h1 {
    font-size: 38px;
  }
  .task-modal {
    max-width: 1000px;
  }
}
</style>
