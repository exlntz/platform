import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  // Загружаем переменные окружения
  const env = loadEnv(mode, process.cwd(), '')

  // Проверяем, задан ли хост принудительно (как мы сделаем на сервере)
  const isProd = env.VITE_IS_PROD === 'true'

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    server: {
      host: true,
      port: 5173,

      // Если это Продакшн (сервер) — включаем настройки для HMR через домен
      // Если Локалка — используем стандартные (ничего не пишем)
      hmr: isProd ? {
        host: 'olymp-platform.ru',
        protocol: 'wss',
        clientPort: 443
      } : undefined,

      proxy: {
        '/api': {
          target: 'http://localhost:8000', // Локально Vite будет стучаться в локальный бэкенд
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '')
        }
      }
    }
  }
})
