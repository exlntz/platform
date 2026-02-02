//import './assets/main.css'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios' // Импортируем axios

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

app.use(createPinia())
app.use(router)

app.mount('#app')
