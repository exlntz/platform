<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const topUsers = ref([])
const loading = ref(true)
const error = ref(null)

/**
 * Загрузка данных таблицы лидеров с бэкенда
 * URL: http://127.0.0.1:8000/leaderboard/
 */
const fetchLeaderboard = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await axios.get('http://127.0.0.1:8000/leaderboard/')
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

onMounted(() => {
  fetchLeaderboard()
})
</script>

<template>
  <div class="leaderboard-container">
    <div class="leaderboard-content">
      <div class="leaderboard-header">
        <div class="badge-hall">Hall of Fame</div>
        <h1 class="title">Зал славы</h1>
        <p class="description">
          Десятка лучших умов платформы. Решай задачи, побеждай в PvP и возглавь этот список!
        </p>
      </div>

      <div class="leaderboard-table">
        <div class="table-header">
          <div class="header-rank">Ранг</div>
          <div class="header-user">Пользователь</div>
          <div class="header-rating">Рейтинг ELO</div>
        </div>

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

        <div v-else class="table-rows">
          <div
            v-for="(user, index) in topUsers"
            :key="user.id"
            class="user-row"
            :class="{
              'first-place': index === 0,
              'second-place': index === 1,
              'third-place': index === 2,
              'other-place': index > 2
            }"
          >
            <div class="rank-cell">
              <span v-if="index === 0" class="medal gold">🥇</span>
              <span v-else-if="index === 1" class="medal silver">🥈</span>
              <span v-else-if="index === 2" class="medal bronze">🥉</span>
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
                  {{ user.username }}
                </span>
                <span v-if="index === 0" class="user-tag">Абсолютный лидер</span>
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
            </div>
          </div>
        </div>
      </div>

      <div v-if="!loading" class="challenge-section">
        <router-link to="/pvp" class="challenge-btn">
          <span class="btn-icon">⚔️</span>
          <span class="btn-text">Бросить вызов</span>
          <span class="btn-arrow">→</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.leaderboard-container {
  min-height: 100vh;
  background-color: #f8fafc;
  padding: 48px 24px;
  font-family: sans-serif;
}
.leaderboard-content {
  max-width: 896px;
  margin: 0 auto;
}
.leaderboard-header {
  text-align: center;
  margin-bottom: 40px;
  animation: fadeIn 0.8s ease-out;
}
.badge-hall {
  display: inline-block;
  padding: 4px 16px;
  background-color: #fef3c7;
  color: #d97706;
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  border-radius: 9999px;
  border: 1px solid #fbbf24;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  margin-bottom: 16px;
}
.title {
  font-size: 48px;
  font-weight: 900;
  color: #0f172a;
  letter-spacing: -0.025em;
  line-height: 1;
  margin-bottom: 16px;
}
@media (min-width: 768px) {
  .title {
    font-size: 60px;
  }
}
.description {
  color: #64748b;
  font-weight: 500;
  max-width: 512px;
  margin: 0 auto;
  font-size: 18px;
  line-height: 1.75;
}
.leaderboard-table {
  background-color: white;
  border-radius: 40px;
  box-shadow: 0 25px 50px -12px rgba(148, 163, 184, 0.6);
  border: 1px solid #f1f5f9;
  overflow: hidden;
  position: relative;
}
.table-header {
  display: grid;
  grid-template-columns: 96px 1fr 96px;
  gap: 16px;
  padding: 24px 40px;
  background-color: #0f172a;
  color: #94a3b8;
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.2em;
}
.header-rank {
  text-align: center;
}
.header-user {
  text-align: left;
}
.header-rating {
  text-align: right;
}
.loading-skeleton {
  padding: 0;
}
.skeleton-row {
  display: grid;
  grid-template-columns: 96px 1fr 96px;
  gap: 16px;
  padding: 32px 40px;
  border-bottom: 1px solid #f8fafc;
}
.skeleton-rank {
  width: 32px;
  height: 32px;
  background-color: #f1f5f9;
  border-radius: 50%;
  margin: 0 auto;
}
.skeleton-user {
  display: flex;
  align-items: center;
  gap: 20px;
}
.skeleton-avatar {
  width: 48px;
  height: 48px;
  background-color: #f1f5f9;
  border-radius: 16px;
}
.skeleton-name {
  height: 24px;
  width: 128px;
  background-color: #f1f5f9;
  border-radius: 9999px;
}
.skeleton-rating {
  height: 32px;
  width: 64px;
  background-color: #f1f5f9;
  border-radius: 9999px;
  margin-left: auto;
}
.table-rows {
  padding: 0;
}
.user-row {
  display: grid;
  grid-template-columns: 96px 1fr 96px;
  gap: 16px;
  padding: 28px 40px;
  align-items: center;
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
}
.user-row.first-place {
  background: linear-gradient(to right, #fef3c7, transparent);
  border-left-color: #f59e0b;
}
.user-row.second-place {
  background: linear-gradient(to right, #f1f5f9, transparent);
  border-left-color: #94a3b8;
}
.user-row.third-place {
  background: linear-gradient(to right, #ffedd5, transparent);
  border-left-color: #fb923c;
}
.user-row.other-place:hover {
  background-color: rgba(248, 250, 252, 0.8);
}
.rank-cell {
  text-align: center;
}
.medal {
  font-size: 32px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.medal.gold {
  color: #f59e0b;
}
.medal.silver {
  color: #94a3b8;
}
.medal.bronze {
  color: #fb923c;
}
.rank-number {
  font-size: 24px;
  font-weight: 900;
  color: #cbd5e1;
  font-variant-numeric: tabular-nums;
}
.user-cell {
  display: flex;
  align-items: center;
  gap: 20px;
}
.user-avatar {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 900;
  font-size: 20px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  transition: all 0.5s ease;
}
.avatar-gold {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  box-shadow: 0 10px 15px -3px rgba(245, 158, 11, 0.2);
}
.avatar-silver {
  background: linear-gradient(135deg, #94a3b8, #64748b);
  box-shadow: 0 10px 15px -3px rgba(148, 163, 184, 0.2);
}
.avatar-bronze {
  background: linear-gradient(135deg, #fb923c, #ea580c);
  box-shadow: 0 10px 15px -3px rgba(251, 146, 60, 0.2);
}
.avatar-other {
  background-color: #e2e8f0;
  color: #94a3b8;
}
.user-row:hover .user-avatar {
  transform: rotate(6deg) scale(1.1);
}
.user-info {
  display: flex;
  flex-direction: column;
}
.username {
  font-weight: 900;
  font-size: 18px;
  transition: color 0.2s ease;
}
.username.top-three {
  color: #0f172a;
}
.username:not(.top-three) {
  color: #334155;
}
.user-tag {
  font-size: 10px;
  font-weight: 700;
  color: #d97706;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-top: 4px;
}
.rating-cell {
  text-align: right;
  font-weight: 900;
  font-size: 24px;
  letter-spacing: -0.05em;
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
.challenge-section {
  text-align: center;
  padding-top: 32px;
  animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}
.challenge-btn {
  display: inline-flex;
  align-items: center;
  gap: 16px;
  padding: 24px 48px;
  background-color: #0f172a;
  color: white;
  font-weight: 900;
  border-radius: 32px;
  text-decoration: none;
  box-shadow: 0 25px 50px -12px rgba(148, 163, 184, 0.2);
  transition: all 0.2s ease;
}
.challenge-btn:hover {
  background-color: #4f46e5;
  transform: scale(1.05);
}
.challenge-btn:active {
  transform: scale(0.95);
}
.btn-icon {
  font-size: 24px;
  transition: transform 0.2s ease;
}
.challenge-btn:hover .btn-icon {
  transform: rotate(12deg);
}
.btn-text {
  font-size: 18px;
}
.btn-arrow {
  opacity: 0.4;
  transition: transform 0.2s ease;
}
.challenge-btn:hover .btn-arrow {
  transform: translateX(8px);
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>