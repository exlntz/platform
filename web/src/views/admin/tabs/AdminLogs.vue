<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/axios.js'
import { useNotificationStore } from '@/pinia/NotificationStore.js'

const notify = useNotificationStore()

const loading = ref(false)
const logs = ref([])

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
              <td class="task-cell" style="max-width: 300px">
                <p class="task-description" :title="log.details">{{ log.details }}</p>
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

/* Adaptive */
@media (max-width: 360px) {
  .tab-header h1 {
    font-size: 20px;
  }
}
@media (min-width: 641px) {
  .logs-tab {
    padding: 32px;
    margin-left: 256px;
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
