import { createApp } from 'vue'
import { createPinia } from 'pinia'
// УБРАЛИ импорт axios, чтобы не было конфликтов с api/axios.js

import App from './App.vue'
import router from './router'

// Chart.js
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

const app = createApp(App)

// --- БАЗОВЫЕ СТИЛИ (ТЕМНАЯ ТЕМА) ---
const darkThemeStyles = `
  :root.dark body {
    background-color: #0f172a;
    color: #f1f5f9;
  }
  :root.dark a { color: #f1f5f9; }
  :root.dark a:hover { color: #93c5fd; }
  :root.dark button { transition: background-color 0.2s ease, color 0.2s ease; }
  * { transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease; }
`
const styleElement = document.createElement('style')
styleElement.textContent = darkThemeStyles
document.head.appendChild(styleElement)

// --- ИНИЦИАЛИЗАЦИЯ ТЕМЫ ---
const initTheme = () => {
  const savedTheme = localStorage.getItem('dark-theme')
  if (savedTheme !== null) {
    if (savedTheme === 'true') document.documentElement.classList.add('dark')
    else document.documentElement.classList.remove('dark')
  } else {
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      document.documentElement.classList.add('dark')
    }
  }
}
initTheme()

window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
  if (localStorage.getItem('dark-theme') === null) {
    document.documentElement.classList.toggle('dark', e.matches)
  }
})

app.use(createPinia())
app.use(router)
app.mount('#app')
