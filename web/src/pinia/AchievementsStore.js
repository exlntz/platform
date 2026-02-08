import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAchievementsStore = defineStore('achievements', () => {
  // Очередь ачивок (массив строк или объектов)
  const queue = ref([])
  
  // Текущая отображаемая ачивка
  const currentAchievement = ref(null)
  
  // Флаг видимости
  const isVisible = ref(false)

  /**
   * Добавить ачивки в очередь
   * @param {string[]} achievementsList 
   */
  const addAchievements = (achievementsList) => {
    if (!Array.isArray(achievementsList) || achievementsList.length === 0) return
    
    // Добавляем новые в конец очереди
    queue.value.push(...achievementsList)
    
    // Если ничего сейчас не показывается, запускаем показ
    if (!isVisible.value) {
      showNext()
    }
  }

  const showNext = () => {
    if (queue.value.length === 0) {
      isVisible.value = false
      currentAchievement.value = null
      return
    }

    // Берем первую из очереди
    currentAchievement.value = queue.value.shift()
    isVisible.value = true

    // Скрываем через 3 секунды и запускаем следующую
    setTimeout(() => {
      isVisible.value = false
      // Даем время на анимацию исчезновения (например, 300мс) перед показом следующей
      setTimeout(() => {
        showNext()
      }, 300) 
    }, 4000)
  }

  return {
    queue,
    currentAchievement,
    isVisible,
    addAchievements
  }
})