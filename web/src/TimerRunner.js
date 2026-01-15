import { onMounted, onUnmounted } from 'vue'
import { useTimerStore } from '@/stores/useTimerStore'

export function useTimerRunner() {
  const timer = useTimerStore()
  let tickInterval = null
  let afkInterval = null

  onMounted(() => {
    timer.loadState()

    tickInterval = setInterval(() => timer.tick(), 1000)
    afkInterval = setInterval(() => timer.checkAfk(), 60 * 1000)

    const events = ['mousemove', 'keydown', 'click', 'scroll']
    events.forEach(e =>
      window.addEventListener(e, timer.updateActivity)
    )
  })

  onUnmounted(() => {
    clearInterval(tickInterval)
    clearInterval(afkInterval)

    const events = ['mousemove', 'keydown', 'click', 'scroll']
    events.forEach(e =>
      window.removeEventListener(e, timer.updateActivity)
    )
  })
}
