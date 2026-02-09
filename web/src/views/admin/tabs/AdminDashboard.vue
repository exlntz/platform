<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/axios.js'
import { useNotificationStore } from '@/pinia/NotificationStore.js'

const notify = useNotificationStore()

const stats = ref({
  total_users: 0,
  total_tasks: 0,
  total_pvp_matches: 0, 
  new_users_24h: 0,
  most_popular_subject: 'Загрузка...',
})

const fetchStats = async () => {
  try {
    const response = await api.get('/admin/stats')
    stats.value = response.data
  } catch (err) {
    console.error('API Error:', err)
    notify.show('Ошибка: ' + (err.response?.data?.detail || err.message))
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<template>
  <div class="dashboard-tab">
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
          <div class="stat-icon pvp-icon">⚔️</div>
          <span class="stat-label">PvP Матчи</span>
        </div>
        <p class="stat-value">{{ stats.total_pvp_matches }}</p>
        <p class="stat-description">всего сыграно</p>
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
</template>

<style scoped>
/* Dashboard Tab */
.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
}

.dashboard-header h1 {
  font-size: 24px;
  font-weight: 900;
  color: #0f172a;
  letter-spacing: -0.025em;
  line-height: 1.2;
}

.live-badge {
  font-size: 12px;
  font-weight: 700;
  color: #64748b;
  background-color: white;
  padding: 4px 10px;
  border-radius: 20px;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  border: 1px solid #f1f5f9;
}

.stats-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.stat-card {
  background-color: white;
  padding: 20px;
  border-radius: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border: 1px solid #f1f5f9;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px -2px rgba(0, 0, 0, 0.15);
}

.stat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

/* Цвета иконок */
.users-icon {
  background-color: #dbeafe;
  color: #2563eb;
}

.growth-icon {
  background-color: #dcfce7;
  color: #16a34a;
}

.pvp-icon {
  background-color: #fee2e2;
  color: #dc2626;
}

.trends-icon {
  background-color: #f3e8ff;
  color: #9333ea;
}

.stat-label {
  font-size: 12px;
  font-weight: 900;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.stat-value {
  font-size: 14px;
  font-weight: 900;
  color: #0f172a;
  line-height: 1.2;
}

.stat-description {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
  margin-top: 4px;
}

/* ==================== DARK MODE ==================== */

:root.dark .stat-card {
  background-color: #1e293b;
  border-color: #334155;
  color: #f1f5f9;
}

:root.dark .stat-card:hover {
  box-shadow: 0 6px 12px -2px rgba(0, 0, 0, 0.4);
}

:root.dark .stat-label {
  color: #cbd5e1;
}

:root.dark .stat-value {
  color: #f8fafc;
}

:root.dark .stat-description {
  color: #94a3b8;
}

:root.dark .dashboard-header h1 {
  color: #f8fafc;
}

:root.dark .live-badge {
  background-color: #1e293b;
  color: #cbd5e1;
  border-color: #334155;
}

/* Адаптивность */
@media (max-width: 360px) {
  .dashboard-header h1 {
    font-size: 22px;
  }
  .stat-card {
    padding: 16px;
  }
  .stat-icon {
    width: 36px;
    height: 36px;
    font-size: 18px;
  }
  .stat-value {
    font-size: 18px;
  }
}

@media (max-width: 640px) {
  .stats-container {
    grid-template-columns: 1fr;
  }
  .stat-card {
    width: 100%;
  }
}

@media (min-width: 641px) and (max-width: 1024px) {
  .stats-container {
    grid-template-columns: repeat(2, 1fr);
  }
  .stat-card {
    width: 100%;
  }
}

@media (min-width: 481px) {
  .stat-icon {
    width: 44px;
    height: 44px;
    font-size: 22px;
  }
  .stat-value {
    font-size: 20px;
  }
}

@media (min-width: 641px) {
  .stats-container {
    grid-template-columns: repeat(2, 2fr);
  }
  .stat-card {
    width: 100%;
  }
  .dashboard-header h1 {
    font-size: 28px;
  }
}

@media (min-width: 769px) {
  .stat-card {
    padding: 28px;
    border-radius: 24px;
  }
  .stat-icon {
    width: 48px;
    height: 48px;
    font-size: 24px;
  }
  .stat-value {
    font-size: 22px;
  }
  .dashboard-header h1 {
    font-size: 32px;
  }
}

@media (min-width: 1025px) {
  .stats-container {
    gap: 24px;
  }
  .stat-card {
    padding: 32px;
    border-radius: 28px;
  }
  .stat-value {
    font-size: 28px;
  }
  .dashboard-header h1 {
    font-size: 36px;
  }
}

@media (min-width: 1281px) {
  .stats-container {
    gap: 28px;
  }
  .stat-card {
    padding: 36px;
    border-radius: 32px;
  }
  .stat-icon {
    width: 56px;
    height: 56px;
    font-size: 28px;
  }
  .stat-value {
    font-size: 36px;
  }
  .dashboard-header h1 {
    font-size: 40px;
  }
}

@media (min-width: 1537px) {
  .stats-container {
    gap: 32px;
  }
  .stat-card {
    padding: 40px;
  }
  .stat-value {
    font-size: 40px;
  }
  .dashboard-header h1 {
    font-size: 44px;
  }
}
</style>
