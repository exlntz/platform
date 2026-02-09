<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/axios' 
import { Line, Radar, Bar } from 'vue-chartjs'

import { useConstantsStore } from '@/pinia/ConstantsStore.js' 



const router = useRouter()
const constants = useConstantsStore() 

const loading = ref(true)
const error = ref(null)

const subjectStats = ref([])
const eloHistory = ref([])
const profile = ref(null)


const fetchStats = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('user-token')
    if (!token) {
      router.push('/auth')
      return
    }

    const headers = { Authorization: `Bearer ${token}` }

    const [profileRes, statsRes, eloHistoryRes] = await Promise.all([
      api.get('/profile/', { headers }),
      api.get('/profile/stats', { headers }),
      api.get('/profile/elo_history', { headers })
    ])

    profile.value = profileRes.data
    subjectStats.value = statsRes.data.stats || []
    eloHistory.value = eloHistoryRes.data || []

  } catch (err) {
    console.error('Ошибка загрузки статистики:', err)

  } finally {
    loading.value = false
  }
}


const radarChartData = computed(() => {
  const currentStats = subjectStats.value || []
  const statsMap = {}
  currentStats.forEach(s => { statsMap[s.subject] = s })

  const subjectsList = constants.subjects 
  const labels = []
  const rawSolved = []
  const rawAccuracy = []

  subjectsList.forEach(subj => {
    labels.push(subj.label)

    const stat = statsMap[subj.key]

    if (stat) {
      rawSolved.push(stat.correct_count)
      rawAccuracy.push(stat.accuracy_percent)
    } else {
      rawSolved.push(0)
      rawAccuracy.push(0)
    }
  })

  const maxSolved = Math.max(...rawSolved) || 1

  return {
    labels: labels, 
    datasets: [
      {
        label: 'Решено задач по предмету',
        data: rawSolved.map(val => (val / maxSolved) * 100),
        originalData: rawSolved,
        backgroundColor: 'rgba(34, 197, 94, 0.2)',
        borderColor: '#22c55e',
        pointBackgroundColor: '#22c55e',
      },
      {
        label: '% Правильных',
        data: rawAccuracy,
        originalData: rawAccuracy,
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        borderColor: '#3b82f6',
        pointBackgroundColor: '#3b82f6',
      }
    ]
  }
})

const radarChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    r: {
      min: 0, max: 100,
      angleLines: { display: true, color: '#e2e8f0' },
      grid: { color: '#e2e8f0' },
      pointLabels: { font: { size: 12, weight: '600' }, color: '#64748b' },
      ticks: { display: false, backdropColor: 'transparent' }
    }
  },
  plugins: {
    legend: { position: 'top' },
    tooltip: {
      callbacks: {
        label: function(context) {
          const label = context.dataset.label || '';
          const rawValue = context.dataset.originalData[context.dataIndex];
          const suffix = label.includes('%') ? '%' : '';
          return `${label}: ${rawValue}${suffix}`;
        }
      }
    }
  }
}


const barChartData = computed(() => {
  if (!subjectStats.value || subjectStats.value.length === 0) return null

  const currentStats = subjectStats.value
  const statsMap = {}
  currentStats.forEach(s => { statsMap[s.subject] = s })

  const subjectsList = constants.subjects
  const labels = []
  const timeData = []

  subjectsList.forEach(subj => {
    labels.push(subj.label)
    const stat = statsMap[subj.key]
    timeData.push(stat ? Math.round(stat.average_time) : 0)
  })

  if (timeData.every(t => t === 0)) return null

  const bgColors = []
  const borderColors = []
  const baseColors = [
    ['rgba(255, 99, 132, 0.6)', 'rgba(255, 99, 132, 1)'],
    ['rgba(54, 162, 235, 0.6)', 'rgba(54, 162, 235, 1)'],
    ['rgba(255, 206, 86, 0.6)', 'rgba(255, 206, 86, 1)'],
    ['rgba(75, 192, 192, 0.6)', 'rgba(75, 192, 192, 1)'],
    ['rgba(153, 102, 255, 0.6)', 'rgba(153, 102, 255, 1)'],
    ['rgba(255, 159, 64, 0.6)', 'rgba(255, 159, 64, 1)']
  ]

  timeData.forEach((_, index) => {
    const colorPair = baseColors[index % baseColors.length]
    bgColors.push(colorPair[0])
    borderColors.push(colorPair[1])
  })

  return {
    labels: labels,
    datasets: [{
      label: 'Ср. время (сек)',
      data: timeData,
      backgroundColor: bgColors,
      borderColor: borderColors,
      borderWidth: 1,
      borderRadius: 6
    }]
  }
})

const barChartOptions = {
  responsive: true, maintainAspectRatio: false,
  scales: {
    y: { beginAtZero: true, grid: { color: '#e2e8f0' }, ticks: { callback: (v) => `${v}с` } },
    x: { grid: { display: false } }
  },
  plugins: { legend: { display: false } }
}


const lineChartData = computed(() => {
  if (!eloHistory.value || eloHistory.value.length === 0) return null
  const sortedHistory = [...eloHistory.value].sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
  if (sortedHistory.length === 0) return null

  return {
    labels: sortedHistory.map(h => new Date(h.created_at).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })),
    datasets: [{
      label: 'Рейтинг',
      data: sortedHistory.map(h => h.rating),
      borderColor: '#4f46e5', backgroundColor: 'rgba(79,70,229,0.2)',
      pointBackgroundColor: '#4f46e5', borderWidth: 2, tension: 0.4, fill: true
    }]
  }
})

const lineChartOptions = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { display: false }, tooltip: { backgroundColor: '#1e293b', displayColors: false } },
  scales: {
    x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
    y: { grid: { borderDash: [5, 5], color: '#e2e8f0' }, ticks: { color: '#94a3b8', precision: 0 } }
  }
}

onMounted(() => {
  fetchStats()
  if (constants.subjects.length === 0) {
    constants.fetchConstants()
  }
})
</script>

<template>
  <div class="stats-container">
    <div class="stats-content">
      <h1 class="page-title">Детальная статистика</h1>

      <div v-if="loading" class="loading-state">
        Загрузка данных...
      </div>

      <div v-else-if="error" class="error-state">
        {{ error }}
        <button @click="fetchStats" class="retry-btn">Повторить</button>
      </div>

      <div v-else class="charts-grid">
        <template v-if="profile && profile.correct_solutions >= 1">

          <div class="chart-card">
            <h3 class="chart-title">Статистика решения задач</h3>
            <div class="chart-wrapper">
              <Radar v-if="radarChartData" :data="radarChartData" :options="radarChartOptions" />
              <div v-else class="no-data-label">Загрузка предметов...</div>
            </div>
          </div>

          <div class="chart-card">
            <h3 class="chart-title">Среднее время решения</h3>
            <div class="chart-wrapper">
              <Bar v-if="barChartData" :data="barChartData" :options="barChartOptions" />
              <div v-else class="no-data-label">Нет данных о времени</div>
            </div>
          </div>

          <div class="chart-card full-width">
            <h3 class="chart-title">История рейтинга</h3>
            <div class="chart-wrapper">
              <Line v-if="lineChartData" :data="lineChartData" :options="lineChartOptions" />
              <div v-else class="no-data-label">История рейтинга пуста</div>
            </div>
          </div>

        </template>

        <div v-else class="empty-state">
          <div class="empty-icon">📊</div>
          <h2>Статистика недоступна</h2>
          <p>Решите хотя бы одну задачу, чтобы открыть доступ к аналитике.</p>
          <router-link to="/tasks" class="solve-btn">Перейти к задачам</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stats-container {
  min-height: 100vh;
  padding: 24px;
  background-color: #f8fafc;
}

.stats-content {
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 28px;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 24px;
}

.charts-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

@media (min-width: 1024px) {
  .charts-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .full-width {
    grid-column: span 2;
  }
}

.chart-card {
  background: white;
  padding: 24px;
  border-radius: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  border: 1px solid #f1f5f9;
}

.chart-title {
  font-size: 16px;
  font-weight: 700;
  color: #64748b;
  margin-bottom: 20px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.chart-wrapper {
  position: relative;
  height: 300px;
  width: 100%;
}

.loading-state, .error-state {
  text-align: center;
  padding: 40px;
  color: #64748b;
  font-size: 18px;
}

.retry-btn {
  display: block;
  margin: 16px auto;
  padding: 8px 16px;
  background: #4f46e5;
  color: white;
  border-radius: 8px;
  border: none;
  cursor: pointer;
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px;
  background: white;
  border-radius: 24px;
  border: 2px dashed #e2e8f0;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.solve-btn {
  display: inline-block;
  margin-top: 20px;
  padding: 10px 24px;
  background-color: #4f46e5;
  color: white;
  font-weight: 700;
  border-radius: 10px;
  text-decoration: none;
}

.no-data-label {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #94a3b8;
  font-weight: 600;
  background: #f8fafc;
  border-radius: 12px;
}

/* Dark theme support */
:root.dark .stats-container { background-color: #0f172a; }
:root.dark .page-title { color: #f8fafc; }
:root.dark .chart-card { background-color: #1e293b; border-color: #334155; }
:root.dark .chart-title { color: #94a3b8; }
:root.dark .empty-state { background-color: #1e293b; border-color: #334155; color: #f1f5f9; }
:root.dark .no-data-label { background-color: #0f172a; color: #64748b; }
</style>
