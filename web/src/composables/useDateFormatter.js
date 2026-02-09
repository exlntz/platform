import { ref } from 'vue'

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

    const dateValue = 
      dateString.endsWith('Z') || dateString.includes('+')
        ? dateString
        : dateString + 'Z'
    try {
      const date = new Date(dateValue)
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