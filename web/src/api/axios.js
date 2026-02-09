import axios from 'axios'
import { useNotificationStore } from '@/pinia/NotificationStore'

// Базовый URL. В Vite/Docker используем относительный путь /api
const BASE_URL = '/api'

// 1. Основной инстанс (для всех запросов приложения)
const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  // Не задаем Content-Type жестко, чтобы он сам определялся (json или form-data)
})

// 2. Инстанс для обновления токена (БЕЗ интерцепторов, чтобы не зациклиться)
const authApi = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
})

// Переменные для очереди запросов (пока токен обновляется)
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

// --- ИНТЕРЦЕПТОР ЗАПРОСА ---
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('user-token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// --- ИНТЕРЦЕПТОР ОТВЕТА ---
api.interceptors.response.use(
  (response) => {
    // Если бэкенд прислал ачивки, показываем уведомление
    const data = response.data
    if (data && Array.isArray(data.achievements) && data.achievements.length > 0) {
      const notify = useNotificationStore()
      data.achievements.forEach((achievementText) => {
        notify.show(achievementText, 'achievement')
      })
    }
    return response
  },
  async (error) => {
    const originalRequest = error.config

    // Если запрос отменен, ничего не делаем
    if (axios.isCancel(error)) return Promise.reject(error)

    const notify = useNotificationStore()
    const status = error.response ? error.response.status : null

    // 1. Игнорируем 401 при ЛОГИНЕ (это просто неверный пароль, рефреш не нужен)
    if (
      status === 401 &&
      (originalRequest.url.includes('/login') || originalRequest.url.includes('/auth/login'))
    ) {
      notify.show('Неверный логин или пароль', 'warning')
      return Promise.reject(error)
    }

    // 2. Обработка истекшего токена (401)
    if (status === 401 && !originalRequest._retry) {
      // Если уже идет обновление, ставим запрос в очередь
      if (isRefreshing) {
        return new Promise(function (resolve, reject) {
          failedQueue.push({ resolve, reject })
        })
          .then((token) => {
            originalRequest.headers['Authorization'] = 'Bearer ' + token
            return api(originalRequest)
          })
          .catch((err) => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const refreshToken = localStorage.getItem('refresh-token')

        if (!refreshToken) {
          throw new Error('Нет refresh токена')
        }

        // ВАЖНО: Делаем запрос через authApi (чистый инстанс)
        const response = await authApi.post('/auth/refresh', {
          refresh_token: refreshToken,
        })

        if (response.status === 200 || response.status === 201) {
          const { access_token, refresh_token: newRefreshToken } = response.data

          localStorage.setItem('user-token', access_token)
          if (newRefreshToken) {
            localStorage.setItem('refresh-token', newRefreshToken)
          }

          // Обновляем токен в заголовках
          api.defaults.headers.common['Authorization'] = 'Bearer ' + access_token

          // Выполняем все запросы из очереди
          processQueue(null, access_token)

          // Повторяем текущий запрос
          originalRequest.headers['Authorization'] = 'Bearer ' + access_token
          return api(originalRequest)
        }
      } catch (refreshError) {
        processQueue(refreshError, null)

        // Если рефреш не удался — полный выход
        localStorage.removeItem('user-token')
        localStorage.removeItem('refresh-token')

        notify.show('Сессия истекла. Войдите снова.', 'error')

        // Используем window.location для жесткого редиректа без импорта роутера
        setTimeout(() => {
          window.location.href = '/auth'
        }, 1000)

        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    // Обработка остальных ошибок (не 401)
    let message = 'Произошла ошибка'
    if (error.response?.data?.detail) {
      const detail = error.response.data.detail
      message = Array.isArray(detail) ? detail.map((e) => e.msg).join('; ') : detail
    } else if (error.message === 'Network Error') {
      message = 'Нет связи с сервером'
    }

    // Показываем уведомление, если это не 401 (401 обрабатывается выше)
    if (status !== 401) {
      if (status === 403) notify.show('Доступ запрещен', 'warning')
      else if (status === 422) notify.show(`Ошибка данных: ${message}`, 'warning')
      else if (status >= 500) notify.show('Ошибка сервера', 'error')
      else if (!status) notify.show(message, 'error')
    }

    return Promise.reject(error)
  },
)

export default api
