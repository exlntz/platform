<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { Line, Radar, Bar } from 'vue-chartjs'

const router = useRouter()
const loading = ref(true)
const profile = ref(null)
const error = ref(null)
const fileInput = ref(null)

const showExtendedStats = ref(false)
const subjectStats = ref([])

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
    const response = await axios.post('/profile/avatar', formData, {
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

    const headers = { Authorization: `Bearer ${token}` }

    // Выполняем запросы параллельно для ускорения
    const [profileRes, statsRes] = await Promise.all([
      axios.get('http://127.0.0.1:8000/profile/', { headers }),
      axios.get('http://127.0.0.1:8000/profile/stats', { headers }) // Запрашиваем статистику по предметам
    ])

    profile.value = {
      user: profileRes.data,
      stats: profileRes.data // Общая статистика из профиля
    }

    // Сохраняем статистику по предметам (массив)
    subjectStats.value = statsRes.data.stats || []

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


// Список всех предметов, которые должны быть на графике ВСЕГДА
const ALL_SUBJECTS = ['Математика', 'Информатика', 'Физика', 'Алгоритмы']

// --- RADAR CHART (Количество + Точность) ---
const radarChartData = computed(() => {
  const currentStats = subjectStats.value || []

  // Создаем карту данных
  const statsMap = {}
  currentStats.forEach(s => { statsMap[s.subject] = s })

  const labels = ALL_SUBJECTS
  const rawSolved = []
  const rawAccuracy = []

  labels.forEach(subject => {
    const stat = statsMap[subject]
    if (stat) {
      rawSolved.push(stat.correct_count)
      rawAccuracy.push(stat.accuracy_percent)
    } else {
      rawSolved.push(0)
      rawAccuracy.push(0)
    }
  })

  // Нормализация для количества задач (чтобы график был красивым)
  const maxSolved = Math.max(...rawSolved) || 1

  return {
    labels: labels,
    datasets: [
      {
        label: 'Решено задач',
        // Нормализуем к 100% шкале
        data: rawSolved.map(val => (val / maxSolved) * 100),
        originalData: rawSolved, // Реальные данные для подсказки

        backgroundColor: 'rgba(34, 197, 94, 0.2)', // Green
        borderColor: '#22c55e',
        pointBackgroundColor: '#22c55e',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: '#22c55e',
      },
      {
        label: 'Точность (%)',
        // Точность уже в процентах (0-100), нормализация не нужна
        data: rawAccuracy,
        originalData: rawAccuracy,

        backgroundColor: 'rgba(59, 130, 246, 0.2)', // Blue
        borderColor: '#3b82f6',
        pointBackgroundColor: '#3b82f6',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: '#3b82f6',
      }
    ]
  }
})

const radarChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    r: {
      min: 0,
      max: 100, // Шкала всегда 0-100%
      angleLines: { display: true, color: '#e2e8f0' },
      grid: { color: '#e2e8f0' },
      pointLabels: {
        font: { size: 12, weight: '600' },
        color: '#64748b'
      },
      ticks: { display: false, backdropColor: 'transparent' }
    }
  },
  plugins: {
    legend: { position: 'top', labels: { font: { size: 11 } } },
    tooltip: {
      callbacks: {
        label: function(context) {
          const label = context.dataset.label || '';
          const rawValue = context.dataset.originalData[context.dataIndex];
          // Если это точность, добавляем %, иначе просто число
          const suffix = label.includes('Точность') ? '%' : '';
          return `${label}: ${rawValue}${suffix}`;
        }
      }
    }
  }
}


// --- BAR CHART (Среднее время) ---
const barChartData = computed(() => {
  const currentStats = subjectStats.value || []
  const statsMap = {}
  currentStats.forEach(s => { statsMap[s.subject] = s })

  const labels = ALL_SUBJECTS
  const timeData = []

  labels.forEach(subject => {
    const stat = statsMap[subject]
    // Округляем время до целых секунд
    timeData.push(stat ? Math.round(stat.average_time) : 0)
  })

  return {
    labels: labels,
    datasets: [
      {
        label: 'Ср. время (сек)',
        data: timeData,
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)',
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
        ],
        borderWidth: 1,
        borderRadius: 6,
      }
    ]
  }
})

const barChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      beginAtZero: true,
      // Убрали max: 100, так как время может быть любым (например, 300 сек)
      grid: { color: '#e2e8f0' },
      ticks: {
        callback: (value) => `${value}с` // Добавляем букву 'с' к оси Y
      }
    },
    x: { grid: { display: false } }
  },
  plugins: {
    legend: { display: false }, // Легенда не нужна, подписи есть снизу
    tooltip: {
      callbacks: {
        label: (context) => `Время: ${context.raw} сек`
      }
    }
  }
}

// LINE chart (динамика рейтинга — пример)
const lineChartData = computed(() => {
  if (!profile.value) return null


  const history =  [

  ]

  return {
    labels: history.map((_, i) => `#${i + 1}`),
    datasets: [
      {
        label: 'Рейтинг',
        data: history,
        borderColor: '#4f46e5',
        backgroundColor: 'rgba(79,70,229,0.2)',
        tension: 0.4
      }
    ]
  }
})

const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false // Скрываем легенду, если там всего одна линия
    },
    tooltip: {
      backgroundColor: '#1e293b',
      padding: 12,
      cornerRadius: 8,
      displayColors: false, // Убираем цветной квадрат в тултипе
    }
  },
  scales: {
    x: {
      grid: {
        display: false // Убираем вертикальные линии сетки
      },
      ticks: {
        color: '#94a3b8'
      }
    },
    y: {
      grid: {
        borderDash: [5, 5], // Пунктирная сетка
        color: '#e2e8f0'
      },
      ticks: {
        color: '#94a3b8',
        precision: 0 // Только целые числа
      }
    }
  }
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
                :src="`/api${profile.user.avatar_url}`"
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
                {{ profile.user.email }}
              </span>
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
              Сменить фото
            </button>
            <button
              @click="logout"
              class="action-btn logout-btn"
            >
              Выйти
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

        <button
          @click="showExtendedStats = !showExtendedStats"
          class="toggle-stats-btn"
          :class="{ 'active': showExtendedStats }"
        >
          <span>{{ showExtendedStats ? 'Скрыть статистику' : 'Расширенная статистика' }}</span>
          <span class="btn-icon">{{ showExtendedStats ? '▲' : '▼' }}</span>
        </button>

        <template v-if="showExtendedStats">

          <template v-if="profile.stats.correct_solutions >= 1">

            <div class="stat-card chart-container">
              <h3 class="chart-title">Баланс навыков</h3>
              <div class="chart-wrapper">
                <Radar
                  v-if="radarChartData"
                  :data="radarChartData"
                  :options="radarChartOptions"
                />
                <div v-else class="no-data-label">Нет данных</div>
              </div>
            </div>

            <div class="stat-card chart-container">
              <h3 class="chart-title">Среднее время решения</h3>
              <div class="chart-wrapper">
                <Bar
                  v-if="barChartData"
                  :data="barChartData"
                  :options="barChartOptions"
                />
              </div>
            </div>
          </template>

          <div v-else class="stat-card chart-container empty-state-full">
            <div class="empty-content">
              <div class="empty-icon">🔒</div>
              <p class="empty-title">Статистика недоступна</p>
              <p class="empty-desc">
                Необходимо решить хотя бы 1 задачу, чтобы алгоритмы могли построить ваши графики.
              </p>
              <router-link to="/tasks" class="solve-btn">Перейти к задачам</router-link>
            </div>
          </div>

        </template>
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

.chart-container {
  /* Графики часто занимают больше места, дадим им растянуться на 2 колонки на больших экранах, если нужно */
  grid-column: span 1;
  display: flex;
  flex-direction: column;
}

.chart-wrapper {
  position: relative;
  height: 250px; /* Важно: фиксированная высота для контейнера графика */
  width: 100%;
}

.chart-title {
  font-size: 14px;
  font-weight: 700;
  color: #64748b;
  margin-bottom: 16px;
  text-transform: uppercase;
}

@media (min-width: 1024px) {
  /* На широких экранах график рейтинга можно сделать широким */
  .chart-container:last-child {
    grid-column: span 2;
  }
}

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
  transition: all 0.3s ease;
  overflow: hidden;
  position: relative;
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

/* ==================== ТЁМНАЯ ТЕМА ==================== */

:root.dark .profile-container {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

:root.dark .profile-card {
  background-color: #1e293b;
  border-color: #334155;
  color: #f1f5f9;
}

:root.dark .username {
  color: #f8fafc;
}

:root.dark .profile-meta {
  color: #cbd5e1;
}

:root.dark .progress-bar {
  background-color: #334155;
}

:root.dark .stat-card {
  background-color: #1e293b;
  border-color: #334155;
  color: #f1f5f9;
}

:root.dark .stat-card:hover {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
}

:root.dark .stat-value {
  color: #f8fafc;
}

:root.dark .stat-label {
  color: #94a3b8;
}

:root.dark .stat-description {
  color: #64748b;
}

:root.dark .action-btn.photo-btn {
  background-color: #334155;
  color: #e2e8f0;
}

:root.dark .action-btn.photo-btn:hover {
  background-color: #475569;
}

:root.dark .action-btn.logout-btn {
  background-color: #1e293b;
  color: #f87171;
  border-color: #7f1d1d;
}

:root.dark .action-btn.logout-btn:hover {
  background-color: #7f1d1d;
}

:root.dark .file-input {
  color-scheme: dark;
}

:root.dark .chart-title {
  color: #94a3b8;
}

/* Loading skeleton */
:root.dark .loading-card,
:root.dark .loading-stat {
  background: linear-gradient(90deg, #334155 25%, #475569 50%, #334155 75%);
}

:root.dark .avatar {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}

:root.dark .avatar-overlay {
  background-color: rgba(0, 0, 0, 0.6);
}

:root.dark .avatar-online {
  border-color: #1e293b;
}

/* Error state */
:root.dark .error-state {
  background-color: #1e293b;
  color: #f1f5f9;
}

:root.dark .error-title {
  color: #f8fafc;
}

:root.dark .retry-btn {
  background: linear-gradient(90deg, #3b82f6, #2563eb);
  color: white;
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

/* Кнопка переключения */
.toggle-stats-btn {
  grid-column: 1 / -1; /* Растягиваем на всю ширину сетки */
  background-color: white;
  border: 1px solid #e2e8f0;
  padding: 16px;
  border-radius: 16px;
  color: #475569;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
  margin-top: 8px;
}

.toggle-stats-btn:hover {
  background-color: #f8fafc;
  color: #0f172a;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.toggle-stats-btn.active {
  background-color: #f1f5f9;
  border-color: #cbd5e1;
}

.btn-icon {
  font-size: 10px;
}

/* Заглушка на всю ширину */
.empty-state-full {
  grid-column: 1 / -1; /* Растягиваем на всю ширину */
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  background-color: #f8fafc;
  border: 2px dashed #cbd5e1;
  text-align: center;
}

.empty-content {
  max-width: 400px;
  padding: 20px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-title {
  font-size: 18px;
  font-weight: 700;
  color: #334155;
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 24px;
  line-height: 1.5;
}

.solve-btn {
  display: inline-block;
  padding: 10px 24px;
  background-color: #4f46e5;
  color: white;
  font-weight: 700;
  border-radius: 10px;
  text-decoration: none;
  transition: background-color 0.2s;
}

.solve-btn:hover {
  background-color: #4338ca;
}

/* Адаптив для графиков при раскрытии */
@media (min-width: 1024px) {
  /* Если графики открыты, они занимают по половине ширины (или как настроена ваша сетка) */
  /* Но саму заглушку мы всегда держим на всю ширину */
  .empty-state-full {
    grid-column: span 3;
  }
}
</style>
