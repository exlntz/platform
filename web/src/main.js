import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'

import App from './App.vue'
import router from './router'

import {
  Chart as ChartJS,
  BarElement,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(
  BarElement,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
)

axios.defaults.baseURL = '/api'
const app = createApp(App)

// --- ГЛОБАЛЬНАЯ НАСТРОЙКА AXIOS ---
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('user-token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('user-token')
      if (router.currentRoute.value.path !== '/auth') {
        alert('Время сессии истекло. Пожалуйста, войдите снова.')
        router.push('/auth')
      }
    }
    return Promise.reject(error)
  },
)

// --- БАЗОВЫЕ СТИЛИ ЧЕРЕЗ :root.dark ---
const darkThemeStyles = `
  :root.dark body {
    background-color: #0f172a;
    color: #f1f5f9;
  }

  :root.dark a {
    color: #60a5fa;
  }

  :root.dark a:hover {
    color: #93c5fd;
  }

  :root.dark button {
    transition: background-color 0.2s ease, color 0.2s ease;
  }

  * {
    transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
  }
`

const styleElement = document.createElement('style')
styleElement.textContent = darkThemeStyles
document.head.appendChild(styleElement)

// --- ЛОГИКА ЗАПОМИНАНИЯ ТЕМЫ ---
const initTheme = () => {
  const savedTheme = localStorage.getItem('dark-theme')

  if (savedTheme !== null) {
    // Если пользователь уже делал выбор — используем его
    if (savedTheme === 'true') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  } else {
    // Если выбора нет — берем системную тему
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      document.documentElement.classList.add('dark')
    }
  }
}

initTheme()

// Слушаем изменения системной темы ТОЛЬКО если пользователь еще не выбрал свою
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
  if (localStorage.getItem('dark-theme') === null) {
    document.documentElement.classList.toggle('dark', e.matches)
  }
})

app.use(createPinia())
app.use(router)
app.mount('#app')
