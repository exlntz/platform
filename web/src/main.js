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

// --- ГЛОБАЛЬНАЯ НАСТРОЙКА AXIOS ---

// 1. Перехватчик запросов: Автоматически цепляет токен
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('user-token')
  if (token) {
    // Если токен есть, добавляем его в заголовок Authorization
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 2. Перехватчик ответов: Обработка истекшей сессии
axios.interceptors.response.use(
  response => response, // Если запрос успешен, просто возвращаем ответ
  error => {
    // Если сервер вернул 401 (Unauthorized), значит токен протух или неверен
    if (error.response && error.response.status === 401) {

      // 1. Удаляем невалидный токен
      localStorage.removeItem('user-token')

      // 2. Проверяем, где мы сейчас находимся, чтобы не зациклить редирект
      if (router.currentRoute.value.path !== '/auth') {
        alert('Время сессии истекло. Пожалуйста, войдите снова.')
        router.push('/auth')
      }
    }
    // Пробрасываем ошибку дальше, чтобы компоненты могли её обработать (если нужно)
    return Promise.reject(error)
  }
)

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