import { ref } from 'vue'

// Создаем форматтер один раз вне функции (Singleton pattern для производительности)
const dateTimeFormatter = new Intl.DateTimeFormat('ru-RU', {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
})

export function useDateFormatter() {
  const formatDate = (dateString) => {
    if (!dateString) return '-'

    // Проверка и нормализация: если нет 'Z' и нет смещения, считаем это UTC
    // (бэкенд иногда грешит тем, что отдает UTC без указания зоны)
    const dateValue = 
      dateString.endsWith('Z') || dateString.includes('+')
        ? dateString
        : dateString + 'Z'

    try {
      const date = new Date(dateValue)
      
      // Проверка на Invalid Date
      if (isNaN(date.getTime())) {
        return dateString
      }

      return dateTimeFormatter.format(date)
    } catch (e) {
      console.warn('Date formatting error:', e)
      return dateString
    }
  }

  return {
    formatDate
  }
}