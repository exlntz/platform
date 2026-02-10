import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/axios'

export const useConstantsStore = defineStore('constants', () => {
  const subjects = ref([])
  const tags = ref([])
  const difficulties = ref([])
  const achievements = ref([])
  
  const loading = ref(false)
  const isLoaded = ref(false)

  const fetchConstants = async () => {
    if (loading.value || isLoaded.value) return

    loading.value = true
    try {
      // Бэкенд возвращает всё сразу в GET /constants/
      const { data } = await api.get('/constants/')
      
      subjects.value = data.subjects || []
      tags.value = data.tags || []
      difficulties.value = data.difficulty || []
      achievements.value = data.constant_achievements || []

      isLoaded.value = true
    } catch (err) {
      error.value = err.message || 'Ошибка при загрузке констант'
      console.error('Constants fetch error:', err)
    } finally {
      loading.value = false
    }
  }

  // Геттеры для быстрого поиска меток (Labels)
  // Используем замыкание, чтобы возвращать функцию поиска
  const getLabelByKey = (list) => (key) => {
    if (!list.value.length || !key) return key
    const found = list.value.find(item => item.key === key)
    return found ? found.label : key
  }

  const getSubjectLabel = computed(() => getLabelByKey(subjects))
  const getDifficultyLabel = computed(() => getLabelByKey(difficulties))

  return {
    subjects,
    tags,
    difficulties,
    achievements,
    loading,
    fetchConstants,
    getSubjectLabel,
    getDifficultyLabel
  }
})