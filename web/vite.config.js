import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  // 1. Указываем путь к папке, где лежит .env (если он в корне проекта, это '../')
  const envDir = '../'
  const env = loadEnv(mode, envDir, '')

  // 2. Улучшенная проверка переменных (Docker vs Local)
  // Мы принудительно переводим значение в строку и удаляем пробелы, чтобы избежать ошибок парсинга
  const dockerRaw = process.env.VITE_IS_DOCKER || env.VITE_IS_DOCKER;
  const isDocker = String(dockerRaw).trim() === 'true';

  const prodRaw = process.env.VITE_IS_PROD || env.VITE_IS_PROD;
  const isProd = String(prodRaw).trim() === 'true';

  // ВЫВОД ОТЛАДКИ: Эти строки появятся в терминале при запуске
  console.log('--- Vite Config Debug Start ---');
  console.log('VITE_IS_DOCKER raw:', dockerRaw);
  console.log('Final isDocker status:', isDocker);
  console.log('VITE_IS_PROD raw:', prodRaw);
  console.log('Final isProd status:', isProd);
  console.log('--- Vite Config Debug End ---');

  return {
    // Говорим Vite искать .env файлы в корневой папке
    envDir: envDir,

    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    server: {
      host: true,
      port: 5173,

      // 3. Настройка Hot Module Replacement (HMR)
      // На сервере (Prod) используем защищенный протокол wss через домен
      hmr: isProd ? {
        host: 'olymp-platform.ru',
        protocol: 'wss',
        clientPort: 443
      } : true,

      proxy: {
        '/api': {
          // Если мы в докере — стучимся к контейнеру fastapi_app
          // Если на Windows (npm run dev) — к локальному порту 127.0.0.1
          target: isDocker ? 'http://fastapi_app:8000' : 'http://127.0.0.1:8000',
          changeOrigin: true,
          ws: true, // Важно для PvP (вебсокеты)
          rewrite: (path) => path.replace(/^\/api/, ''),

          // Логирование ошибок прокси прямо в терминал
          configure: (proxy) => {
            proxy.on('error', (err) => {
              console.log('--- Proxy Error Detected ---');
              console.log('Target used:', isDocker ? 'Docker (fastapi_app:8000)' : 'Local (127.0.0.1:8000)');
              console.log('Error details:', err.message);
            });
          }
        }
      }
    }
  }
})
