import { ref, readonly } from 'vue'

// Глобальный стейт (синглтон)
const visible = ref(false)
const modalData = ref({
  title: '',
  message: '',
  confirmText: 'Подтвердить',
  cancelText: 'Отмена',
  isDanger: false // Опция для красной кнопки (удаление и т.д.)
})

// Сюда сохраним функцию resolve от Promise
let resolvePromise = null

export function useConfirm() {
  /**
   * Вызывает модальное окно.
   * Возвращает Promise, который резолвится в true (ОК) или false (Отмена).
   */
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

  // Методы для использования внутри самого компонента модалки
  const handleConfirm = () => {
    visible.value = false
    if (resolvePromise) resolvePromise(true)
  }

  const handleCancel = () => {
    visible.value = false
    if (resolvePromise) resolvePromise(false)
  }

  return {
    // Readonly стейт для компонента, чтобы случайно не мутировали снаружи
    visible: readonly(visible),
    modalData: readonly(modalData),
    confirm,
    handleConfirm,
    handleCancel
  }
}