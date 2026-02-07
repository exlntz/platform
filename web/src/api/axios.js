import axios from 'axios'
import router from '@/router'
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
  }
)

// Флаг защиты от спама редиректов (твой код)
let isRedirecting = false

// --- 2. ПЕРЕХВАТЧИК ОТВЕТОВ (Обработка ошибок + Refresh) ---
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (axios.isCancel(error)) {
      return Promise.reject(error)
    }

    const notify = useNotificationStore()
    const status = error.response ? error.response.status : null
    const url = error.config?.url || ''
    const originalRequest = error.config

    // Достаем текст ошибки (твоя логика)
    let message = 'Произошла ошибка'
    if (error.response?.data?.detail) {
      const detail = error.response.data.detail
      message = Array.isArray(detail) ? detail.map((e) => e.msg).join('; ') : detail
    } else if (error.message === 'Network Error') {
      message = 'Проблемы с интернетом'
    }

    // Обработка 401
    if (status === 401) {
      // 1. Игнорируем ошибки при самом логине (неверный пароль) - твой код
      if (url.includes('/login') || url.includes('/auth/jwt/login') || url.includes('/token')) {
        notify.show('Неверный логин или пароль', 'warning')
        return Promise.reject(error)
      }

      // 2. 🔥 НОВАЯ ЛОГИКА: Попытка обновить токен перед выходом
      // Если это не повторная попытка запроса (_retry)
      if (originalRequest && !originalRequest._retry) {

        if (isRefreshing) {
          // Если обновление уже идет, ставим запрос в очередь
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
          const refreshToken = localStorage.getItem('refresh-token') // Убедись, что сохраняешь его при логине!

          // Делаем запрос через чистый axios, чтобы не зациклить интерсепторы
          // URL должен совпадать с твоим бэкендом (/auth/refresh)
          const response = await axios.post(`/auth/refresh`, {
             refresh_token: refreshToken
          })

          if (response.status === 200 || response.status === 201) {
            // Сохраняем новые токены
            const { access_token, refresh_token: newRefreshToken } = response.data

            localStorage.setItem('user-token', access_token)
            // Если бэкенд возвращает новый refresh (ротация), сохраняем и его
            if (newRefreshToken) {
                localStorage.setItem('refresh-token', newRefreshToken)
            }

            // Обрабатываем очередь ждущих запросов
            processQueue(null, access_token)

            // Повторяем текущий упавший запрос
            originalRequest.headers['Authorization'] = 'Bearer ' + access_token
            return api(originalRequest)
          }
        } catch (refreshError) {
          // Если обновить не вышло (Refresh протух) — очищаем очередь ошибок
          processQueue(refreshError, null)
          // И идем дальше вниз к твоему коду выхода (Logout)
        } finally {
          isRefreshing = false
        }
      }

      // 3. Если обновить не удалось (или токена нет) — ВЫПОЛНЯЕМ ТВОЙ СТАРЫЙ КОД (Logout)
      if (!isRedirecting) {
        isRedirecting = true
        notify.show('Сессия истекла. Войдите снова.', 'error')

        localStorage.removeItem('user-token')
        localStorage.removeItem('refresh-token') // Не забываем удалить и refresh

        router.push('/auth').then(() => {
          setTimeout(() => {
            isRedirecting = false
          }, 1000)
        })
      }
    } else if (status === 403) notify.show('Доступ запрещен', 'warning')
    else if (status === 422) notify.show(`Ошибка данных: ${message}`, 'warning')
    else if (status >= 500) notify.show('Ошибка сервера', 'error')
    else if (!status) notify.show('Нет соединения с сервером', 'error')

    return Promise.reject(error)
  }
)

export default api
