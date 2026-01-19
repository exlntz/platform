<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const loading = ref(true)
const profile = ref(null)
const error = ref(null)
const fileInput = ref(null) // Ссылка на скрытый инпут для выбора файла

// --- ЛОГИКА РАНГОВ ---
const getRankInfo = (elo) => {
  if (elo < 1200) return { name: 'Новичок', color: 'text-slate-500', bg: 'bg-slate-100', next: 1200 }
  if (elo < 1500) return { name: 'Ученик', color: 'text-green-600', bg: 'bg-green-50', next: 1500 }
  if (elo < 1800) return { name: 'Специалист', color: 'text-blue-600', bg: 'bg-blue-50', next: 1800 }
  if (elo < 2200) return { name: 'Мастер', color: 'text-purple-600', bg: 'bg-purple-50', next: 2200 }
  return { name: 'Легенда', color: 'text-amber-500', bg: 'bg-amber-50', next: 3000 }
}

const rank = computed(() => {
  if (!profile.value) return {}
  return getRankInfo(profile.value.user.rating)
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
  fileInput.value.click() // Симулируем клик по скрытому инпуту
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

    // Обновляем ссылку на аватар в текущем состоянии профиля
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
.profile-container {
  min-height: 100vh;
  background-color: #f8fafc;
  padding: 48px 24px;
  font-family: sans-serif;
}
.loading-state {
  max-width: 80rem;
  margin: 0 auto;
}
.loading-card {
  background-color: #e2e8f0;
  height: 256px;
  border-radius: 40px;
  margin-bottom: 32px;
  animation: pulse 2s infinite;
}
.loading-stats {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 24px;
}
@media (min-width: 768px) {
  .loading-stats {
    grid-template-columns: repeat(3, 1fr);
  }
}
.loading-stat {
  background-color: #e2e8f0;
  height: 160px;
  border-radius: 32px;
  animation: pulse 2s infinite;
}
.profile-content {
  max-width: 80rem;
  margin: 0 auto;
}
.profile-card {
  background-color: white;
  border-radius: 40px;
  padding: 32px;
  margin-bottom: 32px;
  box-shadow: 0 25px 50px -12px rgba(148, 163, 184, 0.5);
  border: 1px solid #f1f5f9;
  position: relative;
  overflow: hidden;
}
@media (min-width: 768px) {
  .profile-card {
    padding: 48px;
  }
}
.profile-background {
  position: absolute;
  top: 0;
  right: 0;
  width: 256px;
  height: 256px;
  background-color: #e0e7ff;
  border-radius: 50%;
  filter: blur(48px);
  transform: translate(50%, -50%);
  opacity: 0.5;
  transition: opacity 0.7s ease;
}
.profile-card:hover .profile-background {
  opacity: 1;
}
.profile-info {
  position: relative;
  z-index: 10;
  display: flex;
  flex-direction: column;
  gap: 32px;
}
@media (min-width: 768px) {
  .profile-info {
    flex-direction: row;
    align-items: center;
    gap: 48px;
    text-align: left;
  }
}
.avatar-section {
  position: relative;
  cursor: pointer;
  flex-shrink: 0;
}
.file-input {
  display: none;
}
.avatar {
  width: 128px;
  height: 128px;
  background-color: #4f46e5;
  border-radius: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 48px;
  font-weight: 900;
  box-shadow: 0 20px 25px -5px rgba(79, 70, 229, 0.2);
  transform: rotate(3deg);
  transition: all 0.5s ease;
  overflow: hidden;
  position: relative;
}
@media (min-width: 768px) {
  .avatar {
    width: 160px;
    height: 160px;
  }
}
.avatar:hover {
  transform: rotate(0deg);
}
.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.avatar-fallback {
  font-size: 48px;
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
  font-size: 32px;
  color: white;
}
.avatar-online {
  position: absolute;
  bottom: 8px;
  right: 8px;
  width: 32px;
  height: 32px;
  background-color: #10b981;
  border: 4px solid white;
  border-radius: 50%;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
.profile-details {
  flex: 1;
  text-align: center;
}
@media (min-width: 768px) {
  .profile-details {
    text-align: left;
  }
}
.name-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
@media (min-width: 768px) {
  .name-section {
    flex-direction: row;
    align-items: center;
    gap: 16px;
  }
}
.username {
  font-size: 30px;
  font-weight: 900;
  color: #0f172a;
  letter-spacing: -0.025em;
}
@media (min-width: 768px) {
  .username {
    font-size: 36px;
  }
}
.rank-badge {
  padding: 8px 16px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  border: 1px solid;
}
.profile-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #64748b;
  font-weight: 500;
  margin-bottom: 24px;
}
@media (min-width: 768px) {
  .profile-meta {
    justify-content: flex-start;
  }
}
.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
}
.meta-icon {
  font-size: 16px;
}
.meta-dot {
  width: 4px;
  height: 4px;
  background-color: #cbd5e1;
  border-radius: 50%;
}
.progress-section {
  max-width: 384px;
  margin: 0 auto;
}
@media (min-width: 768px) {
  .progress-section {
    margin: 0;
  }
}
.progress-header {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  font-weight: 700;
  color: #64748b;
  margin-bottom: 8px;
}
.progress-bar {
  height: 12px;
  width: 100%;
  background-color: #f1f5f9;
  border-radius: 9999px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background-color: #4f46e5;
  border-radius: 9999px;
  transition: width 1s ease-out;
}
.profile-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 140px;
}
.action-btn {
  padding: 12px 24px;
  font-weight: 700;
  border-radius: 16px;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}
.photo-btn {
  background-color: #0f172a;
  color: white;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}
.photo-btn:hover {
  background-color: #1e293b;
}
.logout-btn {
  background-color: white;
  color: #ef4444;
  border: 1px solid #fee2e2;
}
.logout-btn:hover {
  background-color: #fef2f2;
}
.action-btn:active {
  transform: scale(0.95);
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 24px;
}
@media (min-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
.stat-card {
  background-color: white;
  padding: 32px;
  border-radius: 40px;
  border: 1px solid #f1f5f9;
  box-shadow: 0 20px 25px -5px rgba(148, 163, 184, 0.4);
  transition: transform 0.3s ease;
}
.stat-card:hover {
  transform: translateY(-4px);
}
.stat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}
.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
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
  font-weight: 900;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}
.stat-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.stat-main {
  margin-bottom: 20px;
}
.stat-label {
  font-size: 10px;
  font-weight: 900;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 4px;
}
.stat-value {
  font-size: 36px;
  font-weight: 900;
  color: #0f172a;
  letter-spacing: -0.05em;
}
.accuracy-value {
  color: #10b981;
}
.mastery-value {
  color: #d97706;
}
.stat-description {
  font-size: 12px;
  font-weight: 700;
  color: #64748b;
  padding-top: 8px;
}
.stat-divider {
  height: 1px;
  background-color: #f1f5f9;
  margin: 20px 0;
}
.stat-secondary .stat-value {
  font-size: 24px;
  color: #334155;
}
.error-state {
  text-align: center;
  padding: 80px 24px;
}
.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}
.error-title {
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 16px;
}
.retry-btn {
  padding: 8px 24px;
  background-color: #4f46e5;
  color: white;
  border-radius: 12px;
  font-weight: 700;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}
.retry-btn:hover {
  background-color: #4338ca;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>