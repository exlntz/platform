import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref([])

  // Добавили duration с дефолтом 3000
  const show = (message, type = 'info', duration = 3000) => {
    
    // Для ачивок ставим дефолт подольше (если не передали явно)
    if (type === 'achievement' && duration === 3000) {
      duration = 5000 // 5 секунд для ачивок
    }

    const exists = notifications.value.find(n => n.message === message)
    if (exists) return

    const id = Date.now()
    
    notifications.value.push({ id, message, type })

    setTimeout(() => {
      remove(id)
    }, duration) // Используем переменную
  }

  const remove = (id) => {
    notifications.value = notifications.value.filter(n => n.id !== id)
  }

  return { notifications, show, remove }
})