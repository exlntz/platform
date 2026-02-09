<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/axios.js'
import { useNotificationStore } from '@/pinia/NotificationStore.js'

const notify = useNotificationStore()

const loading = ref(false)
const logs = ref([])

// --- МОДАЛЬНОЕ ОКНО ---
const showLogModal = ref(false)
const selectedLog = ref(null)

const openLogDetails = (log) => {
  selectedLog.value = log
  showLogModal.value = true
}

const closeLogModal = () => {
  showLogModal.value = false
  selectedLog.value = null
}

const getBadgeClass = (action) => {
  const act = action.toLowerCase()
  if (act.includes('delete') || act.includes('ban')) return 'hard'
  if (act.includes('update') || act.includes('edit')) return 'medium'
  if (act.includes('create') || act.includes('add')) return 'easy'
  return ''
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const dateValue = dateString.endsWith('Z') ? dateString : dateString + 'Z'
  try {
    return new Date(dateValue).toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch (e) {
    return dateString
  }
}

const fetchLogs = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/logs?limit=50')
    logs.value = response.data
  } catch (err) {
    console.error('API Error:', err)
    notify.show('Ошибка: ' + (err.response?.data?.detail || err.message))
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchLogs()
})
</script>

<template>
  <div class="logs-tab">
    <div class="tab-header">
      <h1>Аудит действий</h1>
      <button @click="fetchLogs" class="refresh-btn">🔄 Обновить</button>
    </div>
    <div class="table-wrapper">
      <div class="responsive-table">
        <table class="users-table">
          <thead>
            <tr class="table-head">
              <th>ID</th>
              <th>Время</th>
              <th>Администратор</th>
              <th>Действие</th>
              <th>Цель</th>
              <th style="width: 40%">Детали</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in logs" :key="log.id" class="table-row">
              <td class="user-id">#{{ log.id }}</td>
              <td class="register-date">{{ formatDate(log.created_at) }}</td>
              <td class="user-cell">
                <div class="user-avatar" :class="{ 'admin-badge-bg': true }">
                  {{ log.admin_username ? log.admin_username.charAt(0).toUpperCase() : '?' }}
                </div>
                <div class="user-details">
                  <p class="user-name">{{ log.admin_username || 'Неизвестно' }}</p>
                  <p class="user-email">Admin ID: {{ log.admin_id }}</p>
                </div>
              </td>
              <td>
                <span class="difficulty-badge" :class="getBadgeClass(log.action)">{{
                  log.action
                }}</span>
              </td>
              <td class="user-id">{{ log.target_id ? '#' + log.target_id : '-' }}</td>
              <td class="task-cell">
                <div class="log-details-wrapper">
                  <p class="task-description text-truncate">
                    {{
                      log.details
                        ? log.details.substring(0, 50) + (log.details.length > 50 ? '...' : '')
                        : '-'
                    }}
                  </p>
                  <button
                    v-if="log.details && log.details.length > 10"
                    @click="openLogDetails(log)"
                    class="action-btn secondary small-btn"
                  >
                    👁 Подробнее
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="!loading && logs.length === 0" class="empty-table">
        <div class="empty-icon">📝</div>
        <p class="empty-title">Логов пока нет</p>
      </div>
    </div>

    <div v-if="showLogModal && selectedLog" class="modal-overlay" @click.self="closeLogModal">
      <div class="log-modal">
        <div class="modal-header">
          <h2>Детали события #{{ selectedLog.id }}</h2>
          <button @click="closeLogModal" class="close-modal">✕</button>
        </div>

        <div class="log-info-grid">
          <div class="info-group">
            <label>Дата и время</label>
            <p>{{ formatDate(selectedLog.created_at) }}</p>
          </div>

          <div class="info-group">
            <label>Администратор</label>
            <div class="user-cell-mini">
              <div class="user-avatar small">
                {{ selectedLog.admin_username?.charAt(0).toUpperCase() }}
              </div>
              <span>{{ selectedLog.admin_username }} (ID: {{ selectedLog.admin_id }})</span>
            </div>
          </div>

          <div class="info-group">
            <label>Действие</label>
            <span class="difficulty-badge" :class="getBadgeClass(selectedLog.action)">
              {{ selectedLog.action }}
            </span>
          </div>

          <div class="info-group">
            <label>Целевой объект (ID)</label>
            <p class="user-id big">{{ selectedLog.target_id ? '#' + selectedLog.target_id : 'Нет' }}</p>
          </div>
        </div>

        <div class="info-group full-width">
          <label>Полные детали</label>
          <div class="code-block">
            {{ selectedLog.details || 'Нет дополнительных деталей' }}
          </div>
        </div>

        <div class="form-actions">
          <button @click="closeLogModal" class="cancel-btn full-width">Закрыть</button>
        </div>
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

/* Logs Table */
.logs-tab {
  padding: 20px;
}
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
.register-date {
  font-size: 11px;
  color: #64748b;
  font-weight: 700;
  white-space: nowrap;
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
.task-cell {
  max-width: 200px;
}
.task-description {
  font-size: 11px;
  color: #64748b;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

/* ================== НОВЫЕ СТИЛИ ДЛЯ КНОПКИ И МОДАЛКИ ================== */

.log-details-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.text-truncate {
  max-width: 180px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.action-btn {
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
.action-btn:hover {
  background-color: #e2e8f0;
}
.small-btn {
  padding: 4px 8px;
  font-size: 10px;
}

/* Modal Styles */
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
.log-modal {
  background-color: white;
  border-radius: 20px;
  width: 100%;
  max-width: 550px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.25);
  padding: 24px;
  border: 1px solid #f1f5f9;
  max-height: 90vh;
  overflow-y: auto;
  animation: fadeInUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
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
  font-size: 18px;
  font-weight: 900;
  color: #0f172a;
  line-height: 1.2;
}
.close-modal {
  width: 32px;
  height: 32px;
  border-radius: 8px;
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

.log-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 20px;
}
.info-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.info-group label {
  font-size: 10px;
  text-transform: uppercase;
  color: #94a3b8;
  font-weight: 700;
  letter-spacing: 0.05em;
}
.info-group p {
  font-size: 14px;
  color: #334155;
  font-weight: 500;
}
.user-cell-mini {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #334155;
}
.user-avatar.small {
  width: 24px;
  height: 24px;
  font-size: 10px;
  border-radius: 6px;
}
.full-width {
  grid-column: 1 / -1;
  width: 100%;
}
.code-block {
  background-color: #f8fafc;
  padding: 12px;
  border-radius: 8px;
  font-family: monospace;
  font-size: 12px;
  color: #475569;
  border: 1px solid #e2e8f0;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 300px;
  overflow-y: auto;
  line-height: 1.5;
}
.form-actions {
  padding-top: 16px;
}
.cancel-btn {
  padding: 12px;
  background-color: #f1f5f9;
  color: #64748b;
  font-weight: 900;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease;
  font-size: 13px;
}
.cancel-btn:hover {
  background-color: #e2e8f0;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Dark Mode */
:root.dark .table-wrapper {
  background-color: #1e293b;
  border-color: #334155;
}
:root.dark .users-table {
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
:root.dark .user-name {
  color: #f1f5f9;
}
:root.dark .user-email,
:root.dark .task-description {
  color: #94a3b8;
}
:root.dark .tab-header h1 {
  color: #f8fafc;
}
:root.dark .refresh-btn {
  background-color: #334155;
  border-color: #475569;
  color: #cbd5e1;
}
:root.dark .refresh-btn:hover {
  background-color: #475569;
}

/* Dark Mode - Modal specific */
:root.dark .log-modal {
  background-color: #1e293b;
  border-color: #334155;
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
:root.dark .info-group p,
:root.dark .user-cell-mini {
  color: #f1f5f9;
}
:root.dark .code-block {
  background-color: #0f172a;
  border-color: #334155;
  color: #cbd5e1;
}
:root.dark .action-btn,
:root.dark .cancel-btn {
  background-color: #334155;
  color: #cbd5e1;
}
:root.dark .action-btn:hover,
:root.dark .cancel-btn:hover {
  background-color: #475569;
}

/* Adaptive */
@media (max-width: 360px) {
  .tab-header h1 {
    font-size: 20px;
  }
}
@media (min-width: 641px) {
  .logs-tab {
    padding: 32px;
  }
  .users-table {
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
}
@media (min-width: 1025px) {
  .tab-header h1 {
    font-size: 30px;
  }
  .table-wrapper {
    border-radius: 24px;
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
}
@media (min-width: 1537px) {
  .tab-header h1 {
    font-size: 38px;
  }
}
</style>