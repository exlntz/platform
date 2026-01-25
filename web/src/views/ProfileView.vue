<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const loading = ref(true)
const profile = ref(null)
const error = ref(null)
const fileInput = ref(null)

// --- ЛОГИКА РАНГОВ ---
const getRankInfo = (elo) => {
  if (elo < 1200) return { name: 'Новичок', color: '#64748b', bg: '#f1f5f9', next: 1200 }
  if (elo < 1500) return { name: 'Ученик', color: '#10b981', bg: '#d1fae5', next: 1500 }
  if (elo < 1800) return { name: 'Специалист', color: '#3b82f6', bg: '#dbeafe', next: 1800 }
  if (elo < 2200) return { name: 'Мастер', color: '#8b5cf6', bg: '#ede9fe', next: 2200 }
  return { name: 'Легенда', color: '#f59e0b', bg: '#fef3c7', next: 3000 }
}

const rank = computed(() => {
  if (!profile.value) return {}
  return getRankInfo(profile.value.user.rating)
})

const rankStyle = computed(() => {
  return {
    backgroundColor: rank.value.bg,
    color: rank.value.color,
    borderColor: rank.value.color
  }
})

const progressToNextRank = computed(() => {
  if (!profile.value) return 0
  const currentElo = profile.value.user.rating
  const { next } = getRankInfo(currentElo)
  const percent = Math.min((currentElo / next) * 100, 100)
  return percent
})

// --- ЛОГИКА АВАТАРКИ ---
const triggerAvatarUpload = () => {
  fileInput.value.click()
}

const handleFileChange = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  const formData = new FormData()
  formData.append('file', file)

  try {
    const token = localStorage.getItem('user-token')
    const response = await axios.post('http://127.0.0.1:8000/profile/avatar', formData, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'multipart/form-data'
      }
    })

    profile.value.user.avatar_url = response.data.url
  } catch (err) {
    console.error('Ошибка загрузки аватара:', err)
    alert('Не удалось загрузить изображение')
  }
}

// --- API ---
const fetchProfile = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('user-token')
    if (!token) {
      router.push('/auth')
      return
    }

    const response = await axios.get('http://127.0.0.1:8000/profile/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    profile.value = response.data
  } catch (err) {
    console.error('Ошибка профиля:', err)
    error.value = 'Не удалось загрузить профиль'
  } finally {
    setTimeout(() => { loading.value = false }, 400)
  }
}

const logout = () => {
  if(confirm('Вы уверены, что хотите выйти?')) {
    localStorage.removeItem('user-token')
    router.push('/')
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('ru-RU', {
    month: 'long', year: 'numeric'
  })
}

onMounted(() => {
  fetchProfile()
})
</script>

<template>
  <div class="profile-container">
    <div v-if="loading" class="loading-state">
      <div class="loading-card"></div>
      <div class="loading-stats">
        <div class="loading-stat"></div>
        <div class="loading-stat"></div>
        <div class="loading-stat"></div>
      </div>
    </div>

    <div v-else-if="profile" class="profile-content">
      <div class="profile-card">
        <div class="profile-background"></div>

        <div class="profile-info">
          <div class="avatar-section" @click="triggerAvatarUpload">
            <input
              type="file"
              ref="fileInput"
              class="file-input"
              accept="image/*"
              @change="handleFileChange"
            />
            <div class="avatar">
              <img
                v-if="profile.user.avatar_url"
                :src="`http://127.0.0.1:8000${profile.user.avatar_url}`"
                class="avatar-image"
                alt="Avatar"
              />
              <span v-else class="avatar-fallback">{{ profile.user.username.charAt(0).toUpperCase() }}</span>
              <div class="avatar-overlay">
                <span class="overlay-icon">📷</span>
              </div>
            </div>
            <div class="avatar-online"></div>
          </div>

          <div class="profile-details">
            <div class="name-section">
              <h1 class="username">{{ profile.user.username }}</h1>
              <span class="rank-badge" :style="rankStyle">
                {{ rank.name }}
              </span>
            </div>

            <div class="profile-meta">
              <span class="meta-item">
                <span class="meta-icon">📧</span> {{ profile.user.email }}
              </span>
              <span class="meta-dot">•</span>
              <span class="meta-item">
                В клубе с {{ formatDate(profile.user.created_at) }}
              </span>
            </div>

            <div class="progress-section">
              <div class="progress-header">
                <span class="progress-label">Рейтинг: {{ profile.user.rating }}</span>
                <span class="progress-next">Следующий ранг: {{ rank.next }}</span>
              </div>
              <div class="progress-bar">
                <div
                  class="progress-fill"
                  :style="{ width: `${progressToNextRank}%` }"
                ></div>
              </div>
            </div>
          </div>

          <div class="profile-actions">
            <button @click="triggerAvatarUpload" class="action-btn photo-btn">
              📷 Сменить фото
            </button>
            <button
              @click="logout"
              class="action-btn logout-btn"
            >
              🚪 Выйти
            </button>
          </div>
        </div>
      </div>

      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-header">
            <div class="stat-icon activity-icon">📈</div>
            <span class="stat-category">Активность</span>
          </div>
          <div class="stat-content">
            <div class="stat-main">
              <p class="stat-label">Задач решено</p>
              <p class="stat-value">{{ profile.stats.correct_solutions }}</p>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-secondary">
              <p class="stat-label">Всего попыток</p>
              <p class="stat-value">{{ profile.stats.total_attempts }}</p>
            </div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-header">
            <div class="stat-icon accuracy-icon">🎯</div>
            <span class="stat-category">Точность</span>
          </div>
          <div class="stat-content">
            <p class="stat-label">Процент успеха</p>
            <p class="stat-value accuracy-value">{{ profile.stats.success_rate }}%</p>
            <p class="stat-description">эффективность решений</p>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-header">
            <div class="stat-icon mastery-icon">🏆</div>
            <span class="stat-category">Мастерство</span>
          </div>
          <div class="stat-content">
            <p class="stat-label">Рейтинг ELO</p>
            <p class="stat-value mastery-value">{{ profile.user.rating }}</p>
            <p class="stat-description">сила твоего аккаунта</p>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="error" class="error-state">
      <div class="error-icon">😕</div>
      <h3 class="error-title">{{ error }}</h3>
      <button @click="fetchProfile" class="retry-btn">Попробовать снова</button>
    </div>
  </div>
</template>

<style scoped>
/* ==================== БАЗОВЫЕ СТИЛИ ==================== */

.profile-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #f0f9ff 100%);
  padding: 16px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  line-height: 1.5;
}

/* Загрузка */
.loading-state {
  max-width: 1000px;
  margin: 0 auto;
}

.loading-card {
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  height: 200px;
  border-radius: 20px;
  margin-bottom: 24px;
  animation: shimmer 1.5s infinite;
}

.loading-stats {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

.loading-stat {
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  height: 120px;
  border-radius: 16px;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* Основной контент */
.profile-content {
  max-width: 1000px;
  margin: 0 auto;
}

/* Карточка профиля */
.profile-card {
  background-color: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
  border: 1px solid #f1f5f9;
  position: relative;
  overflow: hidden;
}

.profile-background {
  position: absolute;
  top: 0;
  right: 0;
  width: 200px;
  height: 200px;
  background-color: #e0e7ff;
  border-radius: 50%;
  filter: blur(40px);
  transform: translate(30%, -30%);
  opacity: 0.5;
  transition: opacity 0.5s ease;
}

.profile-card:hover .profile-background {
  opacity: 0.7;
}

.profile-info {
  position: relative;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

/* Аватар */
.avatar-section {
  position: relative;
  cursor: pointer;
  flex-shrink: 0;
}

.file-input {
  display: none;
}

.avatar {
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 36px;
  font-weight: 800;
  box-shadow: 0 8px 20px rgba(79, 70, 229, 0.2);
  transform: rotate(3deg);
  transition: all 0.3s ease;
  overflow: hidden;
  position: relative;
}

.avatar:hover {
  transform: rotate(0deg) scale(1.05);
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-fallback {
  font-size: 36px;
}

.avatar-overlay {
  position: absolute;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.avatar:hover .avatar-overlay {
  opacity: 1;
}

.overlay-icon {
  font-size: 24px;
  color: white;
}

.avatar-online {
  position: absolute;
  bottom: 6px;
  right: 6px;
  width: 20px;
  height: 20px;
  background-color: #10b981;
  border: 3px solid white;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Детали профиля */
.profile-details {
  flex: 1;
  text-align: center;
  width: 100%;
}

.name-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.username {
  font-size: 24px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.025em;
  line-height: 1.2;
}

.rank-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border: 2px solid;
}

.profile-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: #64748b;
  font-weight: 500;
  margin-bottom: 16px;
  font-size: 13px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.meta-icon {
  font-size: 14px;
}

.meta-dot {
  width: 3px;
  height: 3px;
  background-color: #cbd5e1;
  border-radius: 50%;
}

.progress-section {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  font-weight: 700;
  color: #64748b;
  margin-bottom: 6px;
}

.progress-bar {
  height: 10px;
  width: 100%;
  background-color: #f1f5f9;
  border-radius: 10px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4f46e5, #7c3aed);
  border-radius: 10px;
  transition: width 1s ease-out;
}

/* Кнопки действий */
.profile-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
  max-width: 200px;
}

.action-btn {
  padding: 10px 16px;
  font-weight: 700;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s ease;
}

.photo-btn {
  background-color: #0f172a;
  color: white;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.photo-btn:hover {
  background-color: #1e293b;
  transform: translateY(-1px);
}

.logout-btn {
  background-color: white;
  color: #ef4444;
  border: 2px solid #fee2e2;
}

.logout-btn:hover {
  background-color: #fef2f2;
  transform: translateY(-1px);
}

.action-btn:active {
  transform: scale(0.98);
}

/* Статистика */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

.stat-card {
  background-color: white;
  padding: 20px;
  border-radius: 16px;
  border: 1px solid #f1f5f9;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.stat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
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

.activity-icon {
  background-color: #e0e7ff;
  color: #4f46e5;
}

.accuracy-icon {
  background-color: #d1fae5;
  color: #10b981;
}

.mastery-icon {
  background-color: #fef3c7;
  color: #d97706;
}

.stat-category {
  font-size: 10px;
  font-weight: 800;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stat-main {
  margin-bottom: 16px;
}

.stat-label {
  font-size: 10px;
  font-weight: 800;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.05em;
  line-height: 1.2;
}

.accuracy-value {
  color: #10b981;
}

.mastery-value {
  color: #d97706;
}

.stat-description {
  font-size: 11px;
  font-weight: 700;
  color: #64748b;
  padding-top: 6px;
}

.stat-divider {
  height: 1px;
  background-color: #f1f5f9;
  margin: 16px 0;
}

.stat-secondary .stat-value {
  font-size: 20px;
  color: #334155;
}

/* Ошибка */
.error-state {
  text-align: center;
  padding: 40px 20px;
  max-width: 600px;
  margin: 0 auto;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.error-title {
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 16px;
}

.retry-btn {
  padding: 10px 20px;
  background: linear-gradient(90deg, #4f46e5, #7c3aed);
  color: white;
  border-radius: 12px;
  font-weight: 700;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.retry-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
}

/* ==================== АДАПТИВНЫЕ СТИЛИ ==================== */

@media (min-width: 321px) and (max-width: 375px) {
  .avatar {
    width: 110px;
    height: 110px;
  }
  
  .username {
    font-size: 26px;
  }
  
  .profile-actions {
    max-width: 220px;
  }
}


@media (min-width: 376px) and (max-width: 480px) {
  .profile-container {
    padding: 20px;
  }
  
  .avatar {
    width: 120px;
    height: 120px;
  }
  
  .username {
    font-size: 28px;
  }
  
  .stat-card {
    padding: 24px;
  }
}


@media (min-width: 481px) {
  .profile-container {
    padding: 24px;
  }
  
  .profile-card {
    padding: 24px;
    border-radius: 24px;
  }
  
  .avatar {
    width: 140px;
    height: 140px;
    font-size: 40px;
  }
  
  .avatar-fallback {
    font-size: 40px;
  }
  
  .overlay-icon {
    font-size: 28px;
  }
  
  .avatar-online {
    width: 24px;
    height: 24px;
    border: 4px solid white;
  }
  
  .username {
    font-size: 32px;
  }
  
  .rank-badge {
    font-size: 12px;
    padding: 8px 16px;
  }
  
  .profile-meta {
    font-size: 14px;
  }
  
  .progress-bar {
    height: 12px;
  }
  
  .action-btn {
    padding: 12px 20px;
    font-size: 14px;
  }
  
  .stats-grid {
    gap: 20px;
  }
  
  .stat-card {
    padding: 24px;
  }
  
  .stat-icon {
    width: 48px;
    height: 48px;
    font-size: 24px;
  }
  
  .stat-value {
    font-size: 32px;
  }
}


@media (min-width: 641px) {
  .profile-info {
    flex-direction: row;
    align-items: center;
    gap: 32px;
    text-align: left;
  }
  
  .profile-details {
    text-align: left;
  }
  
  .name-section {
    flex-direction: row;
    align-items: center;
    gap: 16px;
  }
  
  .profile-meta {
    justify-content: flex-start;
  }
  
  .progress-section {
    margin: 0;
  }
  
  .profile-actions {
    width: auto;
    min-width: 160px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}


@media (min-width: 769px) {
  .profile-container {
    padding: 32px;
  }
  
  .profile-card {
    padding: 32px;
    border-radius: 28px;
  }
  
  .profile-info {
    gap: 40px;
  }
  
  .avatar {
    width: 160px;
    height: 160px;
    border-radius: 32px;
  }
  
  .avatar-fallback {
    font-size: 48px;
  }
  
  .username {
    font-size: 36px;
  }
  
  .profile-meta {
    font-size: 15px;
  }
  
  .stats-grid {
    gap: 24px;
  }
  
  .stat-card {
    padding: 28px;
    border-radius: 20px;
  }
  
  .stat-value {
    font-size: 36px;
  }
}


@media (min-width: 1025px) {
  .profile-content {
    max-width: 1100px;
  }
  
  .profile-card {
    padding: 40px;
    border-radius: 32px;
  }
  
  .avatar {
    width: 180px;
    height: 180px;
    border-radius: 40px;
  }
  
  .username {
    font-size: 40px;
  }
  
  .progress-bar {
    height: 14px;
  }
  
  .stats-grid {
    gap: 28px;
  }
  
  .stat-card {
    padding: 32px;
  }
  
  .stat-value {
    font-size: 40px;
  }
}


@media (min-width: 1281px) {
  .profile-container {
    padding: 40px;
  }
  
  .profile-content {
    max-width: 1200px;
  }
  
  .profile-card {
    padding: 48px;
    border-radius: 40px;
  }
  
  .profile-info {
    gap: 48px;
  }
  
  .avatar {
    width: 200px;
    height: 200px;
  }
  
  .username {
    font-size: 44px;
  }
  
  .rank-badge {
    font-size: 14px;
    padding: 10px 20px;
  }
  
  .profile-meta {
    font-size: 16px;
  }
  
  .action-btn {
    padding: 14px 28px;
    font-size: 15px;
  }
  
  .stats-grid {
    gap: 32px;
  }
  
  .stat-card {
    padding: 36px;
  }
  
  .stat-icon {
    width: 56px;
    height: 56px;
    font-size: 28px;
  }
  
  .stat-value {
    font-size: 44px;
  }
}


@media (min-width: 1537px) {
  .profile-container {
    padding: 48px;
  }
  
  .profile-content {
    max-width: 1400px;
  }
  
  .profile-card {
    padding: 56px;
  }
  
  .avatar {
    width: 220px;
    height: 220px;
  }
  
  .username {
    font-size: 48px;
  }
  
  .progress-bar {
    height: 16px;
  }
  
  .stats-grid {
    gap: 36px;
  }
  
  .stat-card {
    padding: 40px;
    border-radius: 24px;
  }
  
  .stat-value {
    font-size: 48px;
  }
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

.profile-card {
  animation: fadeIn 0.6s ease-out;
}

.stats-grid {
  animation: fadeInUp 0.6s ease-out 0.2s both;
}
</style>