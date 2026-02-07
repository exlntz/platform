import axios from 'axios'
import router from '@/router'
import { useNotificationStore } from '@/pinia/NotificationStore'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
})

// --- 1. ПЕРЕХВАТЧИК ЗАПРОСОВ (Вставляем токен) ---
api.interceptors.request.use(
  (config) => {
    // 🔥 ФИКС: Ищем токен под тем именем, как ты сохранил его в AuthView ('user-token')
    const token = localStorage.getItem('user-token')
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Флаг защиты от спама редиректов
let isRedirecting = false

// --- 2. ПЕРЕХВАТЧИК ОТВЕТОВ (Обработка ошибок) ---
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (axios.isCancel(error)) {
      return Promise.reject(error)
    }

    const notify = useNotificationStore()
    const status = error.response ? error.response.status : null
    const url = error.config?.url || ''

    // Достаем текст ошибки
    let message = 'Произошла ошибка'
    if (error.response?.data?.detail) {
        const detail = error.response.data.detail
        message = Array.isArray(detail) ? detail.map(e => e.msg).join('; ') : detail
    } else if (error.message === 'Network Error') {
        message = 'Проблемы с интернетом'
    }

    // Обработка 401
    if (status === 401) {
      // Если ошибка при входе — это не протухшая сессия, а неверный пароль
      if (url.includes('/login') || url.includes('/auth/jwt/login') || url.includes('/token')) {
        notify.show('Неверный логин или пароль', 'warning')
        return Promise.reject(error)
      }

      // Если ошибка в другом месте — сессия истекла
      if (!isRedirecting) {
        isRedirecting = true
        notify.show('Сессия истекла. Войдите снова.', 'error')
        
        // 🔥 ФИКС: Удаляем правильный ключ при выходе
        localStorage.removeItem('user-token') 
        
        router.push('/auth').then(() => {
          setTimeout(() => { isRedirecting = false }, 1000)
        })
      }
    }
    else if (status === 403) notify.show('Доступ запрещен', 'warning')
    else if (status === 422) notify.show(`Ошибка данных: ${message}`, 'warning')
    else if (status >= 500) notify.show('Ошибка сервера', 'error')
    else if (!status) notify.show('Нет соединения с сервером', 'error')
    
    return Promise.reject(error)
  }
)

export default api