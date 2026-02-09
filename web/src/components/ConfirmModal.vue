<script setup>
import { onMounted, onUnmounted, watch } from 'vue'
import { useConfirm } from '@/composables/useConfirm'

const { visible, modalData, handleConfirm, handleCancel } = useConfirm()

// Обработка нажатия ESC для закрытия
const handleKeydown = (e) => {
  if (visible.value && e.key === 'Escape') {
    handleCancel()
  }
}

// Блокировка скролла страницы, когда модалка открыта
watch(visible, (isShown) => {
  if (isShown) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

// Вешаем слушатели (Clean Code: не забываем чистить за собой)
onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  document.body.style.overflow = '' // На случай, если компонент удалится открытым
})
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="visible"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
        @click.self="handleCancel"
      >
        <div
          class="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 shadow-xl transition-all dark:bg-gray-800"
          role="dialog"
          aria-modal="true"
        >
          <h3 class="text-lg font-bold leading-6 text-gray-900 dark:text-white">
            {{ modalData.title }}
          </h3>
          
          <div class="mt-2">
            <p class="text-sm text-gray-500 dark:text-gray-300">
              {{ modalData.message }}
            </p>
          </div>

          <div class="mt-6 flex justify-end gap-3">
            <button
              type="button"
              class="rounded-lg px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-300 dark:text-gray-200 dark:hover:bg-gray-700"
              @click="handleCancel"
            >
              {{ modalData.cancelText }}
            </button>
            
            <button
              type="button"
              :class="[
                'rounded-lg px-4 py-2 text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-offset-2',
                modalData.isDanger 
                  ? 'bg-red-600 hover:bg-red-700 focus:ring-red-500' 
                  : 'bg-indigo-600 hover:bg-indigo-700 focus:ring-indigo-500'
              ]"
              @click="handleConfirm"
            >
              {{ modalData.confirmText }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>