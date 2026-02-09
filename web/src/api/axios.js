import axios from 'axios'
// УБРАЛИ: import router from '@/router' — это вызывало ошибку
import { useNotificationStore } from '@/pinia/NotificationStore'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 10000,
})

// --- НОВЫЕ ПЕРЕМЕННЫЕ ДЛЯ REFRESH TOKEN ---
let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

// --- 1. ПЕРЕХВАТЧИК ЗАПРОСОВ (Вставляем токен) ---
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('user-token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

// Флаг защиты от спама редиректов
let isRedirecting = false

// --- 2. ПЕРЕХВАТЧИК ОТВЕТОВ ---
api.interceptors.response.use(
  (response) => {
    const data = response.data

    // Логика ачивок
    if (data && Array.isArray(data.achievements) && data.achievements.length > 0) {
      const notify = useNotificationStore()
      data.achievements.forEach((achievementText) => {
        notify.show(achievementText, 'achievement')
      })
    }

    return response
  },
  async (error) => {
    if (axios.isCancel(error)) {
      return Promise.reject(error)
    }

    const notify = useNotificationStore()
    const status = error.response ? error.response.status : null
    const url = error.config?.url || ''
    const originalRequest = error.config

    let message = 'Произошла ошибка'
    if (error.response?.data?.detail) {
      const detail = error.response.data.detail
      message = Array.isArray(detail) ? detail.map((e) => e.msg).join('; ') : detail
    } else if (error.message === 'Network Error') {
      message = 'Проблемы с интернетом'
    }

    if (status === 401) {
      if (url.includes('/login') || url.includes('/auth/jwt/login') || url.includes('/token')) {
        notify.show('Неверный логин или пароль', 'warning')
        return Promise.reject(error)
      }

      if (originalRequest && !originalRequest._retry) {
        if (isRefreshing) {
          return new Promise(function (resolve, reject) {
            failedQueue.push({ resolve, reject })
          })
            .then((token) => {
              originalRequest.headers['Authorization'] = 'Bearer ' + token
              return api(originalRequest)
            })
            .catch((err) => {
              return Promise.reject(err)
            })
        }

        originalRequest._retry = true
        isRefreshing = true

        try {
          const refreshToken = localStorage.getItem('refresh-token')
          // ВАЖНО: Используем axios (чистый), чтобы не зациклить интерцепторы
          const response = await axios.post(`${api.defaults.baseURL}/auth/refresh`, {
            refresh_token: refreshToken,
          })

          if (response.status === 200 || response.status === 201) {
            const { access_token, refresh_token: newRefreshToken } = response.data
            localStorage.setItem('user-token', access_token)
            if (newRefreshToken) {
              localStorage.setItem('refresh-token', newRefreshToken)
            }
            processQueue(null, access_token)
            originalRequest.headers['Authorization'] = 'Bearer ' + access_token
            return api(originalRequest)
          }
        } catch (refreshError) {
          processQueue(refreshError, null)
        } finally {
          isRefreshing = false
        }
      }

      if (!isRedirecting) {
        isRedirecting = true
        notify.show('Сессия истекла. Войдите снова.', 'error')
        localStorage.removeItem('user-token')
        localStorage.removeItem('refresh-token')

        // ИЗМЕНЕНИЕ: Используем window.location вместо router.push для разрыва зависимости
        setTimeout(() => {
          window.location.href = '/auth'
        }, 500)
      }
    } else if (status === 403) notify.show('Доступ запрещен', 'warning')
    else if (status === 422) notify.show(`Ошибка данных: ${message}`, 'warning')
    else if (status == 429) notify.show('Слишком много запросов, попробуйте позже', 'error')
    else if (status >= 500) notify.show('Ошибка сервера', 'error')
    else if (!status) notify.show('Нет соединения с сервером', 'error')

    return Promise.reject(error)
  },
)

export default api
