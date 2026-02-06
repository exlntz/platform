import { defineStore } from 'pinia'
import axios from 'axios'
import { ref, computed } from 'vue'

export const useConstantsStore = defineStore('constants', () => {
  // Состояние
  const subjects = ref([])
  const tags = ref([])
  const difficulty = ref([])
  const ranks = ref([])
  
  const loading = ref(false)
  const isLoaded = ref(false)

  // Действия (Actions)
  const fetchConstants = async () => {
    if (isLoaded.value) return // Не грузим повторно, если уже есть
    
    loading.value = true
    try {
      // Предполагаем, что эндпоинт на бэке называется /constants
      // Если у тебя /api/constants, axios сам подставит baseURL если он настроен
      const response = await axios.get('/constants/') 
      
      subjects.value = response.data.subjects
      tags.value = response.data.tags
      difficulty.value = response.data.difficulty
      ranks.value = response.data.ranks
      
      isLoaded.value = true
    } catch (err) {
      console.error('Ошибка загрузки констант:', err)
    } finally {
      loading.value = false
    }
  }

  // Геттеры (Getters) для удобного получения Label по Key
  // Пример: getSubjectLabel('MATH') -> 'Математика'
  const getSubjectLabel = (key) => subjects.value.find(s => s.key === key)?.label || key
  const getTagLabel = (key) => tags.value.find(t => t.key === key)?.label || key
  const getDifficultyLabel = (key) => difficulty.value.find(d => d.key === key)?.label || key
  const getRankLabel = (key) => ranks.value.find(r => r.key === key)?.label || key

  return {
    subjects,
    tags,
    difficulty,
    ranks,
    loading,
    fetchConstants,
    getSubjectLabel,
    getTagLabel,
    getDifficultyLabel,
    getRankLabel
  }
})