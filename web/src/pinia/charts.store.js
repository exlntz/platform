import { defineStore } from 'pinia'
import { useProfileStore } from './profile.store'

export const useChartsStore = defineStore('charts', {
  state: () => ({
    ready: false
  }),

  getters: {
    pieData: () => {
      const profileStore = useProfileStore()
      const stats = profileStore.stats
      if (!stats) return null

      return {
        labels: ['Ошибки', 'Решено'],
        datasets: [
          {
            data: [
              stats.total_attempts - stats.correct_solutions,
              stats.correct_solutions
            ],
            backgroundColor: ['#ef4444', '#22c55e']
          }
        ]
      }
    },

    lineData: () => {
      const profileStore = useProfileStore()
      const user = profileStore.user
      if (!user) return null

      const history = user.rating_history || [
        user.rating - 120,
        user.rating - 80,
        user.rating - 40,
        user.rating
      ]

      return {
        labels: history.map((_, i) => `#${i + 1}`),
        datasets: [
          {
            label: 'Рейтинг',
            data: history,
            borderColor: '#4f46e5',
            backgroundColor: 'rgba(79,70,229,0.2)',
            tension: 0.4
          }
        ]
      }
    }
  },

  actions: {
    enableCharts() {
      this.ready = true
    }
  }
})
