import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref([])

  // Добавить уведомление
  const show = (message, type = 'info') => {
    // ЗАЩИТА ОТ ДУБЛЕЙ: Если такое сообщение уже есть, не показываем снова
    const exists = notifications.value.find(n => n.message === message)
    if (exists) return

    const id = Date.now()
    
    notifications.value.push({ id, message, type })

    // Авто-удаление через 3 секунды
    setTimeout(() => {
      remove(id)
    }, 3000)
  }

  const remove = (id) => {
    notifications.value = notifications.value.filter(n => n.id !== id)
  }

  return { notifications, show, remove }
})