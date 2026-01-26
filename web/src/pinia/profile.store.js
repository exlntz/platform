import { defineStore } from 'pinia'
import axios from 'axios'

export const useProfileStore = defineStore('profile', {
  state: () => ({
    profile: null,
    loading: false,
    error: null
  }),

  getters: {
    stats: (state) => state.profile?.stats || null,
    user: (state) => state.profile?.user || null
  },

  actions: {
    async fetchProfile() {
      if (this.profile) return // 🔥 кеш

      this.loading = true
      try {
        const token = localStorage.getItem('user-token')
        const res = await axios.get('http://127.0.0.1:8000/profile/', {
          headers: { Authorization: `Bearer ${token}` }
        })
        this.profile = res.data
      } catch (e) {
        this.error = 'Ошибка загрузки профиля'
      } finally {
        this.loading = false
      }
    },

    updateAvatar(url) {
      if (this.profile) {
        this.profile.user.avatar_url = url
      }
    },

    logout() {
      localStorage.removeItem('user-token')
      this.profile = null
    }
  }
})
