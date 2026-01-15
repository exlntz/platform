import { defineStore } from 'pinia'

const STORAGE_KEY = 'task_timer'
const AFK_LIMIT = 3 * 60 * 60 * 1000 // 3 hours

export const useTimerStore = defineStore('timer', {
  state: () => ({
    elapsedSeconds: 0,
    isRunning: false,
    isAfkAlertVisible: false,

    // internal state (persisted)
    taskStartTime: null,
    accumulatedSeconds: 0,
    lastActivityTime: Date.now()
  }),

  actions: {
    // ----------------------
    // PERSISTENCE
    // ----------------------
    saveState() {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          elapsedSeconds: this.elapsedSeconds,
          isRunning: this.isRunning,
          isAfkAlertVisible: this.isAfkAlertVisible,
          taskStartTime: this.taskStartTime,
          accumulatedSeconds: this.accumulatedSeconds,
          lastActivityTime: this.lastActivityTime
        })
      )
    },

    loadState() {
      const data = JSON.parse(localStorage.getItem(STORAGE_KEY))
      if (!data) return

      Object.assign(this, data)
    },

    clearState() {
      localStorage.removeItem(STORAGE_KEY)
    },

    // ----------------------
    // TIMER
    // ----------------------
    startTimer() {
      if (this.isRunning) return

      this.taskStartTime = Date.now()
      this.isRunning = true
      this.saveState()
    },

    pauseTimer() {
      if (!this.isRunning) return

      this.accumulatedSeconds += Math.floor(
        (Date.now() - this.taskStartTime) / 1000
      )

      this.isRunning = false
      this.taskStartTime = null
      this.saveState()
    },

    stopTimer() {
      this.pauseTimer()
      this.clearState()
    },

    tick() {
      if (!this.isRunning) return

      this.elapsedSeconds =
        this.accumulatedSeconds +
        Math.floor((Date.now() - this.taskStartTime) / 1000)
    },

    // ----------------------
    // AFK
    // ----------------------
    updateActivity() {
      this.lastActivityTime = Date.now()
      this.saveState()
    },

    checkAfk() {
      if (
        this.isRunning &&
        !this.isAfkAlertVisible &&
        Date.now() - this.lastActivityTime >= AFK_LIMIT
      ) {
        this.isAfkAlertVisible = true
        this.pauseTimer()
      }
    },

    confirmAfk() {
      this.isAfkAlertVisible = false
      this.lastActivityTime = Date.now()
      this.startTimer()
    },

    // ----------------------
    // TASK
    // ----------------------
    startTask() {
      this.elapsedSeconds = 0
      this.accumulatedSeconds = 0
      this.lastActivityTime = Date.now()
      this.startTimer()
    },

    async submitAnswer(isCorrect) {
      if (!isCorrect) return

      this.stopTimer()

      await fetch('/api/save-task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          timeSpent: this.elapsedSeconds
        })
      })
    }
  }
})
