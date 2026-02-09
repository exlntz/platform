import { ref, readonly } from 'vue'

const visible = ref(false)
const modalData = ref({
  title: '',
  message: '',
  confirmText: 'Подтвердить',
  cancelText: 'Отмена',
  isDanger: false 
})

let resolvePromise = null

export function useConfirm() {

  const confirm = (options) => {
    modalData.value = {
      title: options.title || 'Подтверждение',
      message: options.message || 'Вы уверены, что хотите выполнить это действие?',
      confirmText: options.confirmText || 'Да',
      cancelText: options.cancelText || 'Нет',
      isDanger: options.isDanger || false
    }
    visible.value = true

    return new Promise((resolve) => {
      resolvePromise = resolve
    })
  }

  const handleConfirm = () => {
    visible.value = false
    if (resolvePromise) resolvePromise(true)
  }

  const handleCancel = () => {
    visible.value = false
    if (resolvePromise) resolvePromise(false)
  }

  return {
    visible: readonly(visible),
    modalData: readonly(modalData),
    confirm,
    handleConfirm,
    handleCancel
  }
}