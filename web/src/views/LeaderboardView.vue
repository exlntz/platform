<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const topUsers = ref([])
const loading = ref(true)
const error = ref(null)

/**
 * Загрузка данных таблицы лидеров с бэкенда
 * URL: /leaderboard/
 */
const fetchLeaderboard = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await axios.get('/leaderboard/')
    // Бэкенд возвращает список моделей UserModel
    topUsers.value = response.data
  } catch (err) {
    console.error("Ошибка загрузки таблицы лидеров:", err)
    error.value = "Не удалось загрузить список лучших"
  } finally {
    // Искусственная задержка для плавности анимации
    setTimeout(() => { loading.value = false }, 500)
  }
}

// Вычисляемое свойство для обрезанных ников
const truncatedUsers = computed(() => {
  return topUsers.value.map(user => {
    const truncatedUsername = user.username.length > 6 
      ? user.username.substring(0, 4) + '...'
      : user.username;
    
    return {
      ...user,
      truncatedUsername,
      originalUsername: user.username // Сохраняем оригинальный ник для тултипа
    };
  });
});

onMounted(() => {
  fetchLeaderboard()
})
</script>

<template>
  <div class="leaderboard-container">
    <div class="leaderboard-content">
      <!-- Заголовок -->
      <div class="leaderboard-header">
        <div class="badge-hall">🏆 Топ игроков</div>
        <h1 class="title">Таблица лидеров</h1>
        <p class="description">
          Десятка лучших умов платформы. Решай задачи, побеждай в PvP и возглавь этот список!
        </p>
      </div>

      <!-- Таблица лидеров -->
      <div class="leaderboard-table">
        <!-- Шапка таблицы -->
        <div class="table-header">
          <div class="header-rank">Место</div>
          <div class="header-user">Игрок</div>
          <div class="header-rating">Рейтинг</div>
        </div>

        <!-- Загрузка -->
        <div v-if="loading" class="loading-skeleton">
          <div v-for="n in 5" :key="n" class="skeleton-row">
            <div class="skeleton-rank"></div>
            <div class="skeleton-user">
              <div class="skeleton-avatar"></div>
              <div class="skeleton-name"></div>
            </div>
            <div class="skeleton-rating"></div>
          </div>
        </div>

        <!-- Ошибка -->
        <div v-else-if="error" class="error-message">
          <div class="error-icon">⚠️</div>
          <p class="error-text">{{ error }}</p>
          <button @click="fetchLeaderboard" class="error-btn">Попробовать снова</button>
        </div>

        <!-- Данные -->
        <div v-else class="table-rows">
          <div
            v-for="(user, index) in truncatedUsers"
            :key="user.id"
            class="user-row"
            :class="{
              'first-place': index === 0,
              'second-place': index === 1,
              'third-place': index === 2,
              'other-place': index > 2
            }"
            :title="user.originalUsername"
          >
            <div class="rank-cell">
              <span v-if="index === 0" class="medal">🥇</span>
              <span v-else-if="index === 1" class="medal">🥈</span>
              <span v-else-if="index === 2" class="medal">🥉</span>
              <span v-else class="rank-number">#{{ index + 1 }}</span>
            </div>

            <div class="user-cell">
              <div
                class="user-avatar"
                :class="{
                  'avatar-gold': index === 0,
                  'avatar-silver': index === 1,
                  'avatar-bronze': index === 2,
                  'avatar-other': index > 2
                }"
              >
                {{ user.username.charAt(0).toUpperCase() }}
              </div>
              <div class="user-info">
                <span class="username" :class="{ 'top-three': index < 3 }">
                  {{ user.truncatedUsername }}
                </span>
                <span v-if="index === 0" class="user-tag">Лидер</span>
                <span v-if="index === 1" class="user-tag silver">2-е место</span>
                <span v-if="index === 2" class="user-tag bronze">3-е место</span>
              </div>
            </div>

            <div
              class="rating-cell"
              :class="{
                'rating-gold': index === 0,
                'rating-silver': index === 1,
                'rating-bronze': index === 2,
                'rating-other': index > 2
              }"
            >
              {{ user.rating }}
              <span class="rating-change" v-if="index < 3">↑</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Статистика -->
      <div v-if="!loading && !error" class="stats-section">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-info">
              <div class="stat-number">{{ topUsers.length }}</div>
              <div class="stat-label">игроков в топе</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">⚡</div>
            <div class="stat-info">
              <div class="stat-number">{{ topUsers[0]?.rating || 0 }}</div>
              <div class="stat-label">максимальный рейтинг</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🎯</div>
            <div class="stat-info">
              <div class="stat-number">{{ Math.round(topUsers.reduce((sum, user) => sum + user.rating, 0) / topUsers.length) || 0 }}</div>
              <div class="stat-label">средний рейтинг</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Призыв к действию -->
      <div v-if="!loading && !error" class="challenge-section">
        <p class="challenge-text">Доберись до вершины рейтинга!</p>
        <router-link to="/pvp" class="challenge-btn">
          <span class="btn-icon">⚔️</span>
          <span class="btn-text">Начать соревноваться</span>
          <span class="btn-arrow">→</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ==================== БАЗОВЫЕ СТИЛИ ==================== */

.leaderboard-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #f0f9ff 100%);
  padding: 16px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  line-height: 1.5;
}

.leaderboard-content {
  max-width: 1000px;
  margin: 0 auto;
}

/* Заголовок */
.leaderboard-header {
  text-align: center;
  margin-bottom: 32px;
  animation: fadeIn 0.6s ease-out;
}

.badge-hall {
  display: inline-block;
  padding: 8px 16px;
  background-color: #fef3c7;
  color: #d97706;
  font-size: 14px;
  font-weight: 700;
  border-radius: 20px;
  border: 2px solid #fbbf24;
  margin-bottom: 16px;
}

.title {
  font-size: 32px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.025em;
  margin-bottom: 12px;
  line-height: 1.2;
}

.description {
  color: #64748b;
  font-weight: 500;
  max-width: 600px;
  margin: 0 auto;
  font-size: 16px;
  line-height: 1.6;
}

/* Таблица */
.leaderboard-table {
  background-color: white;
  border-radius: 20px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
  border: 1px solid #f1f5f9;
  overflow: hidden;
  margin-bottom: 32px;
}

.table-header {
  display: grid;
  grid-template-columns: 80px 1fr 100px;
  gap: 12px;
  padding: 16px 20px;
  background-color: #0f172a;
  color: #e2e8f0;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
}

.header-rank,
.header-rating {
  text-align: center;
}

.header-user {
  text-align: left;
}

/* Загрузка */
.loading-skeleton {
  padding: 20px;
}

.skeleton-row {
  display: grid;
  grid-template-columns: 80px 1fr 100px;
  gap: 12px;
  padding: 16px 0;
  align-items: center;
  border-bottom: 1px solid #f8fafc;
}

.skeleton-rank {
  width: 40px;
  height: 40px;
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  border-radius: 12px;
  margin: 0 auto;
  animation: shimmer 1.5s infinite;
}

.skeleton-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.skeleton-avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  border-radius: 12px;
  animation: shimmer 1.5s infinite;
}

.skeleton-name {
  height: 20px;
  width: 120px;
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  border-radius: 10px;
  animation: shimmer 1.5s infinite;
}

.skeleton-rating {
  height: 24px;
  width: 60px;
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  border-radius: 12px;
  margin-left: auto;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* Ошибка */
.error-message {
  padding: 40px 20px;
  text-align: center;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.error-text {
  color: #dc2626;
  font-size: 16px;
  margin-bottom: 20px;
  font-weight: 500;
}

.error-btn {
  padding: 12px 24px;
  background-color: #4f46e5;
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.error-btn:hover {
  background-color: #4338ca;
  transform: translateY(-2px);
}

/* Строки таблицы */
.table-rows {
  padding: 0;
}

.user-row {
  display: grid;
  grid-template-columns: 80px 1fr 100px;
  gap: 12px;
  padding: 16px 20px;
  align-items: center;
  transition: all 0.2s ease;
  border-bottom: 1px solid #f8fafc;
}

.user-row:last-child {
  border-bottom: none;
}

.user-row.first-place {
  background: linear-gradient(to right, #fef3c7 0%, transparent 100%);
  border-left: 4px solid #f59e0b;
}

.user-row.second-place {
  background: linear-gradient(to right, #f1f5f9 0%, transparent 100%);
  border-left: 4px solid #94a3b8;
}

.user-row.third-place {
  background: linear-gradient(to right, #ffedd5 0%, transparent 100%);
  border-left: 4px solid #fb923c;
}

.user-row.other-place:hover {
  background-color: #f8fafc;
}

/* Ранг */
.rank-cell {
  text-align: center;
}

.medal {
  font-size: 32px;
  display: block;
}

.rank-number {
  font-size: 20px;
  font-weight: 800;
  color: #94a3b8;
  font-variant-numeric: tabular-nums;
}

/* Пользователь */
.user-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 800;
  font-size: 18px;
  flex-shrink: 0;
}

.avatar-gold {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.2);
}

.avatar-silver {
  background: linear-gradient(135deg, #94a3b8, #64748b);
  box-shadow: 0 4px 12px rgba(148, 163, 184, 0.2);
}

.avatar-bronze {
  background: linear-gradient(135deg, #fb923c, #ea580c);
  box-shadow: 0 4px 12px rgba(251, 146, 60, 0.2);
}

.avatar-other {
  background-color: #e2e8f0;
  color: #64748b;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow: hidden;
}

.username {
  font-weight: 700;
  font-size: 16px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.username.top-three {
  color: #0f172a;
}

.username:not(.top-three) {
  color: #334155;
}

.user-tag {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 8px;
  display: inline-block;
  width: fit-content;
}

.user-tag:not(.silver):not(.bronze) {
  background-color: #fef3c7;
  color: #d97706;
}

.user-tag.silver {
  background-color: #f1f5f9;
  color: #64748b;
}

.user-tag.bronze {
  background-color: #ffedd5;
  color: #ea580c;
}

/* Рейтинг */
.rating-cell {
  text-align: center;
  font-weight: 800;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.rating-gold {
  color: #d97706;
}

.rating-silver {
  color: #64748b;
}

.rating-bronze {
  color: #ea580c;
}

.rating-other {
  color: #4f46e5;
}

.rating-change {
  font-size: 14px;
  color: #22c55e;
}

/* Статистика */
.stats-section {
  margin: 32px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #f1f5f9;
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 32px;
  width: 56px;
  height: 56px;
  background: #f8fafc;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
}

/* Призыв к действию */
.challenge-section {
  text-align: center;
  padding: 32px 0;
  animation: fadeInUp 0.6s ease-out;
}

.challenge-text {
  font-size: 18px;
  color: #64748b;
  margin-bottom: 20px;
  font-weight: 500;
}

.challenge-btn {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 16px 32px;
  background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
  color: white;
  font-weight: 700;
  border-radius: 16px;
  text-decoration: none;
  box-shadow: 0 8px 20px -4px rgba(79, 70, 229, 0.3);
  transition: all 0.2s ease;
}

.challenge-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 15px 30px -8px rgba(79, 70, 229, 0.4);
  background: linear-gradient(90deg, #4338ca 0%, #6d28d9 100%);
}

.challenge-btn:active {
  transform: translateY(0);
}

.btn-icon {
  font-size: 20px;
}

.btn-text {
  font-size: 16px;
}

.btn-arrow {
  font-size: 18px;
  opacity: 0.8;
}

/* Анимации */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ==================== ТЁМНАЯ ТЕМА ==================== */

:root.dark .leaderboard-container {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

:root.dark .title {
  color: #f8fafc;
}

:root.dark .description {
  color: #cbd5e1;
}

:root.dark .badge-hall {
  background-color: #334155;
  color: #fbbf24;
  border-color: #f59e0b;
}

:root.dark .leaderboard-table {
  background-color: #1e293b;
  border-color: #334155;
}

:root.dark .table-header {
  background-color: #334155;
  color: #e2e8f0;
}

:root.dark .user-row {
  border-bottom-color: #334155;
}

:root.dark .user-row:hover {
  background-color: #334155;
}

:root.dark .rank-number {
  color: #94a3b8;
}

:root.dark .avatar-other {
  background-color: #334155;
  color: #94a3b8;
}

:root.dark .username:not(.top-three) {
  color: #e2e8f0;
}

:root.dark .stat-card {
  background-color: #1e293b;
  border-color: #334155;
  color: #f1f5f9;
}

:root.dark .stat-card:hover {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
}

:root.dark .stat-icon {
  background-color: #334155;
}

:root.dark .stat-number {
  color: #f8fafc;
}

:root.dark .stat-label {
  color: #94a3b8;
}

:root.dark .challenge-text {
  color: #cbd5e1;
}

/* Skeleton loading */
:root.dark .skeleton-rank,
:root.dark .skeleton-avatar,
:root.dark .skeleton-name,
:root.dark .skeleton-rating {
  background: linear-gradient(90deg, #334155 25%, #475569 50%, #334155 75%);
}

/* ==================== АДАПТИВНЫЕ СТИЛИ ==================== */

@media (max-width: 320px) {
  .leaderboard-container {
    padding: 12px;
  }

  .title {
    font-size: 26px;
  }

  .description {
    font-size: 14px;
  }

  .table-header {
    grid-template-columns: 60px 1fr 80px;
    padding: 12px 16px;
    font-size: 11px;
  }

  .user-row {
    grid-template-columns: 60px 1fr 80px;
    padding: 12px 16px;
    gap: 8px;
  }

  .user-avatar {
    width: 36px;
    height: 36px;
    font-size: 16px;
  }

  .username {
    font-size: 14px;
  }

  .rating-cell {
    font-size: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .challenge-btn {
    padding: 14px 24px;
    font-size: 14px;
  }
}


@media (min-width: 321px) and (max-width: 375px) {
  .table-header {
    grid-template-columns: 70px 1fr 90px;
  }

  .user-row {
    grid-template-columns: 70px 1fr 90px;
  }
}


@media (min-width: 376px) and (max-width: 480px) {
  .leaderboard-content {
    padding: 0 8px;
  }

  .title {
    font-size: 28px;
  }
}


@media (min-width: 481px) {
  .leaderboard-container {
    padding: 24px;
  }

  .title {
    font-size: 36px;
  }

  .description {
    font-size: 17px;
  }

  .table-header {
    padding: 18px 24px;
  }

  .user-row {
    padding: 18px 24px;
  }

  .user-avatar {
    width: 48px;
    height: 48px;
    font-size: 20px;
  }

  .username {
    font-size: 17px;
  }
}


@media (min-width: 641px) {
  .title {
    font-size: 40px;
  }

  .badge-hall {
    font-size: 15px;
    padding: 10px 20px;
  }
}


@media (min-width: 769px) {
  .title {
    font-size: 44px;
  }

  .description {
    font-size: 18px;
  }

  .leaderboard-table {
    border-radius: 24px;
  }

  .table-header {
    padding: 20px 32px;
    font-size: 13px;
  }

  .user-row {
    padding: 20px 32px;
  }

  .stats-grid {
    gap: 20px;
  }

  .stat-card {
    padding: 24px;
  }
}


@media (min-width: 1025px) {
  .leaderboard-container {
    padding: 32px;
  }

  .title {
    font-size: 48px;
  }

  .badge-hall {
    font-size: 16px;
  }

  .table-header {
    grid-template-columns: 100px 1fr 120px;
    padding: 24px 40px;
  }

  .user-row {
    grid-template-columns: 100px 1fr 120px;
    padding: 24px 40px;
  }

  .user-avatar {
    width: 52px;
    height: 52px;
  }

  .username {
    font-size: 18px;
  }

  .rating-cell {
    font-size: 20px;
  }
}


@media (min-width: 1281px) {
  .title {
    font-size: 52px;
  }

  .leaderboard-content {
    max-width: 1100px;
  }

  .description {
    font-size: 20px;
  }

  .stats-grid {
    gap: 24px;
  }

  .stat-card {
    padding: 28px;
  }

  .stat-number {
    font-size: 28px;
  }

  .stat-icon {
    font-size: 36px;
    width: 64px;
    height: 64px;
  }
}


@media (min-width: 1536px) {
  .leaderboard-container {
    padding: 48px;
  }

  .leaderboard-content {
    max-width: 1200px;
  }

  .title {
    font-size: 56px;
  }

  .table-header {
    padding: 28px 48px;
  }

  .user-row {
    padding: 28px 48px;
  }
}
</style>
