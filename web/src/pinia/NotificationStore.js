import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref([])


  const show = (message, type = 'info', duration = 3000) => {
    
    if (type === 'achievement' && duration === 3000) {
      duration = 5000 
    }

    const exists = notifications.value.find(n => n.message === message)
    if (exists) return

    const id = Date.now()
    
    notifications.value.push({ id, message, type })

    setTimeout(() => {
      remove(id)
    }, duration) 
  }

  const remove = (id) => {
    notifications.value = notifications.value.filter(n => n.id !== id)
  }

  return { notifications, show, remove }
})