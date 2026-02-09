<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/axios.js'
import { useConstantsStore } from '@/pinia/ConstantsStore.js'
import { useNotificationStore } from '@/pinia/NotificationStore.js'

const notify = useNotificationStore()
const constants = useConstantsStore()

const loading = ref(false)
const users = ref([])
const activeMenuId = ref(null)

// --- ДЕТАЛИ И РЕДАКТИРОВАНИЕ ПОЛЬЗОВАТЕЛЯ ---
const showUserDetailsModal = ref(false)
const userDetailsLoading = ref(false)
const isUserEditMode = ref(false)
const userForm = ref({
  id: null,
  username: '',
  email: '',
  rating: 0,
  rank: 'BRONZE',
  xp: 0,
  is_admin: false,
  is_banned: false,
  avatar_url: '',
  achievements: [],
})
const selectedUserStats = ref(null)
const selectedUserEloHistory = ref([])
const selectedUser = ref(null)

const RANKS_INFO = {
  BRONZE: 0,
  SILVER: 1200,
  GOLD: 1700,
  ELITE: 2300,
  SENSEI: 3000,
  LEGEND: 5000,
}
const ranksList = Object.keys(RANKS_INFO)

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

const fetchUsers = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/users?limit=100')
    users.value = response.data
  } catch (err) {
    console.error('API Error:', err)
    notify.show('Ошибка: ' + (err.response?.data?.detail || err.message))
  } finally {
    loading.value = false
  }
}

const toggleMenu = (event, id) => {
  event.stopPropagation()
  activeMenuId.value = activeMenuId.value === id ? null : id
}

const openUserDetails = async (user) => {
  activeMenuId.value = null
  selectedUser.value = user
  showUserDetailsModal.value = true
  userDetailsLoading.value = true
  isUserEditMode.value = false
  selectedUserStats.value = null
  selectedUserEloHistory.value = []

  userForm.value = { ...user, achievements: user.achievements || [] }

  try {
    try {
      const detailRes = await api.get(`/admin/users/${user.id}`)
      userForm.value = { ...userForm.value, ...detailRes.data }
    } catch (e) {
      console.warn('GET /admin/users/{id} not supported or failed, using list data', e)
    }

    const statsRes = await api.get(`/admin/users/${user.id}/full_details`)
    const data = statsRes.data

    if (data.profile) {
      userForm.value = { ...userForm.value, ...data.profile }
    }

    selectedUserStats.value = data.stats
    selectedUserEloHistory.value = data.elo_history
  } catch (err) {
    console.error('API Error:', err)
    notify.show('Ошибка: ' + (err.response?.data?.detail || err.message))
  } finally {
    userDetailsLoading.value = false
  }
}

const toggleUserEditMode = () => {
  isUserEditMode.value = !isUserEditMode.value
}

const onRankChange = () => {
  const minRating = RANKS_INFO[userForm.value.rank]
  if (minRating !== undefined) {
    userForm.value.rating = minRating
  }
}

const toggleAchievement = (achKey) => {
  const idx = userForm.value.achievements.indexOf(achKey)
  if (idx === -1) userForm.value.achievements.push(achKey)
  else userForm.value.achievements.splice(idx, 1)
}

const saveUserChanges = async () => {
  const payload = {
    username: userForm.value.username,
    email: userForm.value.email,
    rating: Number(userForm.value.rating),
    rank: userForm.value.rank,
    xp: Number(userForm.value.xp),
    is_admin: Boolean(userForm.value.is_admin),
    is_banned: Boolean(userForm.value.is_banned),
    avatar_url: userForm.value.avatar_url || '',
    achievements: userForm.value.achievements || [],
  }

  try {
    await api.patch(`/admin/users/${userForm.value.id}`, payload)
    notify.show('Пользователь обновлен!')
    isUserEditMode.value = false
    fetchUsers()
  } catch (err) {
    console.error('API Error:', err)
    notify.show('Ошибка: ' + (err.response?.data?.detail || err.message))
  }
}

const toggleUserStatus = async (field) => {
  if (!userForm.value.id) return

  const userId = userForm.value.id
  let url = ''
  let payload = {}

  if (field === 'is_banned') {
    url = `/admin/users/${userId}/ban`
    payload = { is_banned: !userForm.value.is_banned }
  } else if (field === 'is_admin') {
    url = `/admin/users/${userId}/promote`
    payload = { is_admin: !userForm.value.is_admin }
  } else {
    return
  }

  try {
    const response = await api.patch(url, payload)

    if (field === 'is_banned') userForm.value.is_banned = response.data.is_banned
    if (field === 'is_admin') userForm.value.is_admin = response.data.is_admin

    const userInList = users.value.find((u) => u.id === userId)
    if (userInList) {
      userInList[field] = response.data[field]
    }

    notify.show(response.data.message)
  } catch (err) {
    console.error('API Error:', err)
    notify.show('Ошибка: ' + (err.response?.data?.detail || err.message))
  }
}

const deleteUser = async (user) => {
  if (!confirm(`Вы уверены, что хотите безвозвратно удалить пользователя ${user.username}?`)) return
  try {
    await api.delete(`/admin/users/${user.id}`)
    users.value = users.value.filter((u) => u.id !== user.id)
    showUserDetailsModal.value = false
  } catch (err) {
    console.error('API Error:', err)
    notify.show('Ошибка: ' + (err.response?.data?.detail || err.message))
  }
}

onMounted(() => {
  window.addEventListener('click', () => {
    activeMenuId.value = null
  })
  fetchUsers()
  if (constants.subjects.length === 0) constants.fetchConstants()
})
</script>

<template>
  <div class="users-tab">
    <div class="tab-header">
      <h1>Управление пользователями</h1>
      <button @click="fetchUsers" class="refresh-btn">🔄 Обновить</button>
    </div>
    <div class="table-wrapper">
      <div class="responsive-table">
        <table class="users-table">
          <thead>
            <tr class="table-head">
              <th>ID</th>
              <th class="user-column">Пользователь</th>
              <th>Рейтинг</th>
              <th class="date-column">Дата регистрации</th>
              <th class="status-column">Роль / Статус</th>
              <th class="actions-header">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id" class="table-row">
              <td class="user-id">#{{ user.id }}</td>
              <td class="user-cell">
                <div class="user-avatar">{{ user.username.charAt(0).toUpperCase() }}</div>
                <div class="user-details">
                  <p class="user-name">{{ user.username }}</p>
                  <p class="user-email">{{ user.email }}</p>
                </div>
              </td>
              <td class="rating-cell">
                <span class="rating-badge">{{ user.rating }}</span>
              </td>
              <td class="register-date">{{ formatDate(user.created_at) }}</td>
              <td class="status-cell">
                <div class="status-container">
                  <span class="status-badge" :class="{ banned: user.is_banned }">{{
                    user.is_banned ? 'Banned' : 'Active'
                  }}</span>
                  <span v-if="user.is_admin" class="admin-badge">Admin</span>
                </div>
              </td>
              <td class="actions-cell">
                <button @click="toggleMenu($event, user.id)" class="actions-btn">Действия ▾</button>
                <div v-if="activeMenuId === user.id" class="actions-dropdown">
                  <button @click="openUserDetails(user)" class="dropdown-item">
                    <span class="item-icon">ℹ️</span> <span>Подробнее...</span>
                  </button>
                  <div class="dropdown-divider"></div>
                  <button @click="deleteUser(user)" class="dropdown-item delete-item">
                    <span class="item-icon">🗑️</span> <span>Удалить</span>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="!loading && users.length === 0" class="empty-table">
        <div class="empty-icon">🔍</div>
        <p class="empty-title">Пользователи не найдены</p>
      </div>
    </div>

    <div v-if="showUserDetailsModal" class="modal-overlay">
      <div class="task-modal user-details-modal" :class="{ extended: isUserEditMode }">
        <div class="modal-header">
          <h2>{{ isUserEditMode ? 'Редактирование профиля' : 'Досье пользователя' }}</h2>
          <button @click="showUserDetailsModal = false" class="close-modal">✕</button>
        </div>

        <div v-if="userDetailsLoading" class="loading-state">
          <div class="spinner"></div>
          Загрузка данных...
        </div>

        <div v-else class="user-dossier-content">
          <div v-if="!isUserEditMode && userForm">
            <div class="dossier-header">
              <div class="dossier-avatar">
                <img v-if="userForm.avatar_url" :src="userForm.avatar_url" class="avatar-img" />
                <span v-else>{{ userForm.username.charAt(0).toUpperCase() }}</span>
              </div>
              <div class="dossier-main-info">
                <h3>
                  {{ userForm.username }} <span class="id-hint">#{{ userForm.id }}</span>
                </h3>
                <p class="dossier-email">{{ userForm.email }}</p>
                <div class="dossier-badges">
                  <span class="rating-badge">ELO: {{ userForm.rating }}</span>
                  <span class="rating-badge" v-if="userForm.rank">{{ userForm.rank }}</span>
                  <span class="status-badge" :class="{ banned: userForm.is_banned }">{{
                    userForm.is_banned ? 'Заблокирован' : 'Активен'
                  }}</span>
                  <span v-if="userForm.is_admin" class="admin-badge">Администратор</span>
                </div>
              </div>
              <div class="dossier-actions">
                <button @click="toggleUserEditMode" class="action-btn secondary">
                  ✎ Редактировать
                </button>
                <button
                  @click="toggleUserStatus('is_banned')"
                  class="action-btn"
                  :class="userForm.is_banned ? 'success' : 'danger'"
                >
                  {{ userForm.is_banned ? 'Разблокировать' : 'Заблокировать' }}
                </button>
                <button
                  @click="toggleUserStatus('is_admin')"
                  class="action-btn"
                  :class="userForm.is_admin ? 'danger' : 'success'"
                >
                  {{ userForm.is_admin ? 'Снять админа' : 'Назначить админом' }}
                </button>
              </div>
            </div>

            <div class="dossier-section" v-if="selectedUserStats">
              <h4>Статистика</h4>
              <div class="stats-grid-mini">
                <div
                  v-for="(stat, subject) in selectedUserStats.subjects"
                  :key="subject"
                  class="mini-stat-card"
                >
                  <div class="mini-stat-title">{{ constants.getSubjectLabel(subject) }}</div>
                  <div class="mini-stat-row">
                    <span>{{ stat.solved }}/{{ stat.total_attempts }}</span>
                    <span class="winrate"
                      >{{
                        stat.total_attempts
                          ? Math.round((stat.solved / stat.total_attempts) * 100)
                          : 0
                      }}%</span
                    >
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-else-if="isUserEditMode">
            <form @submit.prevent="saveUserChanges" class="modal-form">
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">ID</label>
                  <input :value="userForm.id" disabled class="form-input disabled-input" />
                </div>
                <div class="form-group">
                  <label class="form-label">Рейтинг ELO</label>
                  <input v-model.number="userForm.rating" type="number" class="form-input" />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Ранг</label>
                <select v-model="userForm.rank" class="form-select" @change="onRankChange">
                  <option v-for="r in ranksList" :key="r" :value="r">{{ r }}</option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">Имя пользователя</label>
                <input v-model="userForm.username" class="form-input" />
              </div>

              <div class="form-group">
                <label class="form-label">Email</label>
                <input v-model="userForm.email" class="form-input" />
              </div>

              <div class="form-group">
                <label class="form-label">Avatar URL</label>
                <input v-model="userForm.avatar_url" class="form-input" />
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">Опыт (XP)</label>
                  <input v-model.number="userForm.xp" type="number" class="form-input" />
                </div>
              </div>

              <div class="form-group checkboxes-group">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="userForm.is_admin" /> Администратор
                </label>
                <label class="checkbox-label">
                  <input type="checkbox" v-model="userForm.is_banned" /> Заблокирован
                </label>
              </div>

              <div class="form-group">
                <label class="form-label">Достижения</label>
                <div class="tags-selector">
                  <button
                    type="button"
                    v-for="ach in constants.achievements"
                    :key="ach.key"
                    @click="toggleAchievement(ach.key)"
                    class="tag-choice-btn"
                    :class="{ active: userForm.achievements.includes(ach.key) }"
                  >
                    {{ ach.label }}
                    <span v-if="userForm.achievements.includes(ach.key)" class="tag-check">✓</span>
                  </button>
                </div>
              </div>

              <div class="form-actions">
                <button type="submit" class="save-btn">Сохранить</button>
                <button @click="isUserEditMode = false" type="button" class="cancel-btn">
                  Отмена
                </button>
              </div>
            </form>
          </div>
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
.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: inherit;
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
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
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
.user-modal.extended {
  max-width: 600px;
}
.user-details-modal {
  max-width: 500px;
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
.form-input {
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
.disabled-input {
  opacity: 0.6;
  background-color: #e2e8f0;
  cursor: not-allowed;
}
.form-select:focus,
.form-input:focus {
  background-color: white;
  border-color: #4f46e5;
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.1);
}
.form-submit {
  padding-top: 16px;
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

/* --- TAGS SELECTOR --- */
.tags-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 4px;
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
.tag-choice-btn:hover {
  background-color: #f8fafc;
  border-color: #cbd5e1;
}
.tag-choice-btn.active {
  background-color: #e0e7ff;
  color: #4f46e5;
  border-color: #4f46e5;
}
.tag-check {
  font-weight: 900;
}
.form-hint {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 6px;
}

/* --- Checkboxes Group --- */
.checkboxes-group {
  flex-direction: row;
  gap: 20px;
  margin-top: 8px;
}
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #334155;
  cursor: pointer;
}

/* --- USER DOSSIER --- */
.user-dossier {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.dossier-header {
  display: flex;
  gap: 20px;
  align-items: flex-start;
  padding-bottom: 20px;
  border-bottom: 1px solid #f1f5f9;
}
.dossier-avatar {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  background-color: #4f46e5;
  color: white;
  font-size: 32px;
  font-weight: 900;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3);
  overflow: hidden;
}
.dossier-main-info {
  flex: 1;
}
.dossier-main-info h3 {
  font-size: 24px;
  font-weight: 900;
  color: #0f172a;
  margin-bottom: 4px;
}
.id-hint {
  color: #94a3b8;
  font-size: 14px;
  font-weight: 500;
  margin-left: 6px;
}
.dossier-email {
  color: #64748b;
  font-size: 14px;
  margin-bottom: 12px;
}
.dossier-badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.dossier-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.action-btn {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  border: none;
  transition: all 0.2s ease;
  white-space: nowrap;
}
.action-btn.success {
  background-color: #dcfce7;
  color: #16a34a;
}
.action-btn.danger {
  background-color: #fee2e2;
  color: #dc2626;
}
.action-btn.secondary {
  background-color: #f1f5f9;
  color: #475569;
}
.dossier-section h4 {
  font-size: 16px;
  font-weight: 800;
  color: #334155;
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.stats-grid-mini {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}
.mini-stat-card {
  background-color: #f8fafc;
  padding: 12px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}
.mini-stat-title {
  font-size: 11px;
  font-weight: 700;
  color: #64748b;
  margin-bottom: 8px;
}
.mini-stat-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 6px;
}
.winrate {
  color: #f59e0b;
}
.winrate.high {
  color: #10b981;
}
.progress-bar-bg {
  height: 4px;
  background-color: #e2e8f0;
  border-radius: 2px;
  overflow: hidden;
}
.progress-bar-fill {
  height: 100%;
  background-color: #4f46e5;
  border-radius: 2px;
}
.mini-table {
  width: 100%;
  font-size: 13px;
  border-collapse: collapse;
}
.mini-table th {
  text-align: left;
  color: #94a3b8;
  font-size: 11px;
  text-transform: uppercase;
  padding-bottom: 8px;
  border-bottom: 1px solid #f1f5f9;
}
.mini-table td {
  padding: 8px 0;
  border-bottom: 1px solid #f8fafc;
  color: #334155;
  font-weight: 500;
}
.text-green {
  color: #10b981;
  font-weight: 700;
}
.text-red {
  color: #ef4444;
  font-weight: 700;
}

/* Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
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

/* ==================== ТЁМНАЯ ТЕМА (Strict :root.dark) ==================== */

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

:root.dark .user-email {
  color: #94a3b8;
}

:root.dark .rating-badge {
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

:root.dark .disabled-input {
  background-color: #475569;
  color: #94a3b8;
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

:root.dark .refresh-btn {
  background-color: #334155;
  border-color: #475569;
  color: #cbd5e1;
}

:root.dark .refresh-btn:hover {
  background-color: #475569;
}

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

:root.dark .tag-choice-btn {
  background-color: #334155;
  border-color: #475569;
  color: #cbd5e1;
}

:root.dark .tag-choice-btn:hover {
  background-color: #475569;
}

:root.dark .tag-choice-btn.active {
  background-color: #1e3a8a;
  border-color: #3b82f6;
  color: #93c5fd;
}

:root.dark .dossier-header {
  border-bottom-color: #334155;
}

:root.dark .dossier-main-info h3 {
  color: #f1f5f9;
}

:root.dark .dossier-section h4 {
  color: #cbd5e1;
}

:root.dark .mini-stat-card {
  background-color: #334155;
  border-color: #475569;
}

:root.dark .mini-stat-title {
  color: #94a3b8;
}

:root.dark .mini-stat-row {
  color: #e2e8f0;
}

:root.dark .mini-table th {
  color: #94a3b8;
  border-bottom-color: #475569;
}

:root.dark .mini-table td {
  color: #e2e8f0;
  border-bottom-color: #334155;
}

:root.dark .progress-bar-bg {
  background-color: #475569;
}

:root.dark .checkbox-label {
  color: #cbd5e1;
}

:root.dark .tab-header h1 {
  color: #f8fafc;
}

:root.dark .action-btn.secondary {
  background-color: #334155;
  color: #e2e8f0;
}

:root.dark .action-btn.success {
  background-color: #064e3b;
  color: #a7f3d0;
}

:root.dark .action-btn.danger {
  background-color: #7f1d1d;
  color: #fecaca;
}

/* Adaptive */
@media (max-width: 360px) {
  .tab-header h1 {
    font-size: 20px;
  }
  .task-modal,
  .user-modal {
    padding: 20px;
  }
  .modal-header h2 {
    font-size: 18px;
  }
}
@media (min-width: 481px) {
}
@media (min-width: 641px) {
  .form-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .task-modal {
    max-width: 600px;
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
  .task-modal,
  .user-modal {
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
