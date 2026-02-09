<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/axios.js'
import { useNotificationStore } from '@/pinia/NotificationStore.js'

const notify = useNotificationStore()

const loading = ref(false)
const matches = ref([])
const page = ref(0)
const limit = 50
const hasMore = ref(true)

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

// Форматирование результата для отображения
const formatResult = (result, p1, p2) => {
  if (result === 'player1_win') return `Победа ${p1}`
  if (result === 'player2_win') return `Победа ${p2}`
  if (result === 'draw') return 'Ничья'
  return result
}

const getResultClass = (result) => {
  if (result === 'draw') return 'status-badge warning'
  return 'status-badge success'
}

const fetchMatches = async (reset = false) => {
  if (loading.value) return
  
  if (reset) {
    matches.value = []
    page.value = 0
    hasMore.value = true
  }

  loading.value = true
  try {
    const offset = page.value * limit
    const response = await api.get(`/admin/pvp_matches_history?limit=${limit}&offset=${offset}`)
    
    if (response.data.length < limit) {
      hasMore.value = false
    }
    
    matches.value = [...matches.value, ...response.data]
    page.value++
  } catch (err) {
    console.error('API Error:', err)
    notify.show('Ошибка загрузки матчей: ' + (err.response?.data?.detail || err.message))
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchMatches(true)
})
</script>

<template>
  <div class="pvp-tab">
    <div class="tab-header">
      <h1>История PvP Матчей</h1>
      <button @click="fetchMatches(true)" class="refresh-btn">🔄 Обновить</button>
    </div>

    <div class="table-wrapper">
      <div class="responsive-table">
        <table class="users-table">
          <thead>
            <tr class="table-head">
              <th>ID</th>
              <th class="user-column">Игроки</th>
              <th>Результат</th>
              <th>ELO (P1 / P2)</th>
              <th class="date-column">Дата</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="match in matches" :key="match.id" class="table-row">
              <td class="user-id">#{{ match.id }}</td>
              
              <td class="user-cell">
                <div class="user-avatar p1-avatar">{{ match.player1_username.charAt(0).toUpperCase() }}</div>
                <div class="user-details">
                  <p class="user-name">{{ match.player1_username }}</p>
                </div>
              </td>

              <td class="user-cell">
                <div class="user-avatar p2-avatar">{{ match.player2_username.charAt(0).toUpperCase() }}</div>
                <div class="user-details">
                  <p class="user-name">{{ match.player2_username }}</p>
                </div>
              </td>

              <td class="status-cell">
                <span :class="getResultClass(match.result)">
                  {{ formatResult(match.result, match.player1_username, match.player2_username) }}
                </span>
              </td>

              <td class="rating-cell">
                <div class="elo-changes">
                  <span :class="match.p1_elo_change >= 0 ? 'text-green' : 'text-red'">
                    {{ match.p1_elo_change > 0 ? '+' : '' }}{{ match.p1_elo_change }}
                  </span>
                  <span class="divider">/</span>
                  <span :class="match.p2_elo_change >= 0 ? 'text-green' : 'text-red'">
                    {{ match.p2_elo_change > 0 ? '+' : '' }}{{ match.p2_elo_change }}
                  </span>
                </div>
              </td>

              <td class="register-date">{{ formatDate(match.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        Загрузка истории...
      </div>
      
      <div v-else-if="matches.length === 0" class="empty-table">
        <div class="empty-icon">⚔️</div>
        <p class="empty-title">Матчей пока не было</p>
      </div>

      <div v-if="hasMore && !loading && matches.length > 0" class="load-more-container">
        <button @click="fetchMatches(false)" class="load-more-btn">Загрузить еще</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Стили полностью адаптированы из AdminUsers.vue для консистентности */

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
  overflow: hidden;
  max-width: 100%;
  padding-bottom: 16px;
}

/* Table Styles */
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
  vertical-align: middle;
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
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 900;
  color: white;
  flex-shrink: 0;
}
.p1-avatar {
  background-color: #6366f1; /* Indigo */
  box-shadow: 0 2px 5px rgba(99, 102, 241, 0.3);
}
.p2-avatar {
  background-color: #ec4899; /* Pink */
  box-shadow: 0 2px 5px rgba(236, 72, 153, 0.3);
}

.user-name {
  font-weight: 700;
  color: #0f172a;
  font-size: 13px;
  white-space: nowrap;
}
.register-date {
  font-size: 11px;
  color: #64748b;
  font-weight: 700;
  white-space: nowrap;
}
.status-badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}
.status-badge.success {
  background-color: #d1fae5;
  color: #059669;
  border: 1px solid #a7f3d0;
}
.status-badge.warning {
  background-color: #fef3c7;
  color: #d97706;
  border: 1px solid #fde68a;
}
.elo-changes {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 700;
}
.divider {
  color: #cbd5e1;
  margin: 0 4px;
}
.text-green { color: #10b981; }
.text-red { color: #ef4444; }

/* Empty & Loading States */
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
.loading-state {
  padding: 40px;
  text-align: center;
  color: #64748b;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #e2e8f0;
  border-top-color: #4f46e5;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Load More */
.load-more-container {
  display: flex;
  justify-content: center;
  padding: 16px;
}
.load-more-btn {
  padding: 8px 24px;
  background-color: #f1f5f9;
  color: #475569;
  font-size: 12px;
  font-weight: 700;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}
.load-more-btn:hover {
  background-color: #e2e8f0;
  color: #1e293b;
}

/* Dark Theme */
:root.dark .table-wrapper {
  background-color: #1e293b;
  border-color: #334155;
}
:root.dark .users-table { background-color: #1e293b; }
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
:root.dark .user-name { color: #f1f5f9; }
:root.dark .tab-header h1 { color: #f8fafc; }
:root.dark .refresh-btn {
  background-color: #334155;
  border-color: #475569;
  color: #cbd5e1;
}
:root.dark .refresh-btn:hover { background-color: #475569; }
:root.dark .load-more-btn {
  background-color: #334155;
  color: #cbd5e1;
}
:root.dark .load-more-btn:hover { background-color: #475569; }
:root.dark .status-badge.success {
  background-color: #064e3b;
  color: #a7f3d0;
  border-color: #065f46;
}
:root.dark .status-badge.warning {
  background-color: #78350f;
  color: #fcd34d;
  border-color: #92400e;
}
:root.dark .empty-title { color: #f1f5f9; }

/* Responsive */
@media (min-width: 1025px) {
  .tab-header h1 { font-size: 30px; }
  .table-wrapper { border-radius: 24px; }
}
</style>