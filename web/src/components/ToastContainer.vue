<script setup>
import { useNotificationStore } from '@/pinia/NotificationStore'

const store = useNotificationStore()

const typeClasses = {
  info: 'bg-blue-600 border-blue-800',
  success: 'bg-green-600 border-green-800',
  error: 'bg-red-600 border-red-800',
  warning: 'bg-yellow-600 border-yellow-800'
}
</script>

<template>
  <Teleport to="body">
    <div 
      class="fixed top-5 right-5 flex flex-col gap-3 pointer-events-none w-full max-w-sm px-4"
      style="z-index: 9999;" 
    >
      <TransitionGroup name="toast">
        <div 
          v-for="note in store.notifications" 
          :key="note.id"
          class="pointer-events-auto p-4 rounded-lg shadow-2xl text-white flex justify-between items-start border-l-4 transform transition-all duration-300 backdrop-blur-sm bg-opacity-95"
          :class="typeClasses[note.type] || typeClasses.info"
        >
          <div class="flex-1 pr-2">
            <span class="font-medium text-sm leading-snug block">{{ note.message }}</span>
          </div>
          
          <button 
            @click="store.remove(note.id)" 
            class="text-white opacity-70 hover:opacity-100 transition focus:outline-none"
          >
            ✕
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(50px) scale(0.9);
}
</style>