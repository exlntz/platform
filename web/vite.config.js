import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    host: true, // Позволяет Docker пробрасывать порты
    allowedHosts: true, // Разрешает работу через твой домен olymp-platform.ru

    // 1. Исправляем ошибку WebSocket (HMR) в консоли
    hmr: {
      host: 'olymp-platform.ru',
      protocol: 'wss', // Обязательно защищенный протокол для HTTPS
    },

    // 2. Настраиваем прокси для локальной разработки
    // Теперь ты можешь писать axios.get('/api/tasks/') и это будет работать везде
    proxy: {
      '/api': {
        target: 'http://localhost:8000', // Твой FastAPI бэкенд
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''), // Отрезает /api перед отправкой в Python
      }
    }
  }
})
