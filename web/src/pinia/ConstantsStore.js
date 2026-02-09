import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api/axios'

export const useConstantsStore = defineStore('constants', () => {
  // Инициализируем как пустые массивы, чтобы не было ошибок "undefined"
  const subjects = ref([])
  const tags = ref([])
  const difficulty = ref([])
  const achievements = ref([])

  const loading = ref(false)
  const isLoaded = ref(false)

  const fetchConstants = async () => {
    if (loading.value || isLoaded.value) return

    loading.value = true
    try {
      // Запрашиваем все константы параллельно
      const [subjRes, tagsRes, diffRes, achRes] = await Promise.all([
        api.get('/constants/subjects'),
        api.get('/constants/tags'),
        api.get('/constants/difficulty'),
        api.get('/constants/achievements'),
      ])

      subjects.value = subjRes.data || []
      tags.value = tagsRes.data || []
      difficulty.value = diffRes.data || []
      achievements.value = achRes.data || []

      isLoaded.value = true
    } catch (err) {
      console.error('Ошибка загрузки констант:', err)
    } finally {
      loading.value = false
    }
  }

  // Безопасные геттеры (проверяют наличие массива)
  const getSubjectLabel = (key) => {
    if (!subjects.value || !key) return key
    const found = subjects.value.find((s) => s.key === key)
    return found ? found.label : key
  }

  const getDifficultyLabel = (key) => {
    if (!difficulty.value || !key) return key
    const found = difficulty.value.find((d) => d.key === key)
    return found ? found.label : key
  }

  return {
    subjects,
    tags,
    difficulty,
    achievements,
    loading,
    isLoaded,
    fetchConstants,
    getSubjectLabel,
    getDifficultyLabel,
  }
})
