import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'

import App from './App.vue'
import router from './router'

// Импортируем само ядро Chart.js и нужные модули
import {
  Chart as ChartJS,
  BarElement, // <--- Добавили для столбцов
  RadialLinearScale, // Нужен для Radar
  PointElement,      // Нужен для Radar и Line
  LineElement,       // Нужен для Radar и Line
  Filler,            // Нужен для заливки (Radar)
  CategoryScale,     // Нужен для оси X (Line)
  LinearScale,       // Нужен для оси Y (Line)
  Tooltip,
  Legend
} from 'chart.js'


// Регистрируем их глобально для этого компонента
ChartJS.register(
  BarElement, // <--- Не забудьте зарегистрировать
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
)

axios.defaults.baseURL = '/api';
const app = createApp(App)



// --- БАЗОВЫЕ СТИЛИ ДЛЯ ТЁМНОЙ ТЕМЫ ---
// Добавляем базовые стили для тёмной темы в head документа
const darkThemeStyles = `
  /* Базовые стили для тёмной темы */
  .dark body {
    background-color: #0f172a;
    color: #f1f5f9;
  }
  
  .dark a {
    color: #60a5fa;
  }
  
  .dark a:hover {
    color: #93c5fd;
  }
  
  .dark button {
    transition: background-color 0.2s ease, color 0.2s ease;
  }
  
  /* Плавный переход для всей страницы */
  * {
    transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
  }
`

// Создаём и добавляем стили в head
const styleElement = document.createElement('style')
styleElement.textContent = darkThemeStyles
document.head.appendChild(styleElement)

// Проверяем сохранённую тему при загрузке приложения
const savedTheme = localStorage.getItem('dark-theme')
if (savedTheme === 'true') {
  document.documentElement.classList.add('dark')
} else {
  // Проверяем предпочтения системы
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('dark-theme', 'true')
  }
}

// Слушаем изменения системной темы
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
  if (localStorage.getItem('dark-theme') === null) {
    if (e.matches) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }
})

app.use(createPinia())
app.use(router)

app.mount('#app')