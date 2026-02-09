import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AccessDeniedView from '../views/AccessDeniedView.vue'
import api from '@/api/axios.js' // Используем наш настроенный axios

// Импорты админки
import AdminView from '@/views/admin/AdminView.vue'
import AdminDashboard from '@/views/admin/tabs/AdminDashboard.vue'
import AdminUsers from '@/views/admin/tabs/AdminUsers.vue'
import AdminTasks from '@/views/admin/tabs/AdminTasks.vue'
import AdminLogs from '@/views/admin/tabs/AdminLogs.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/access-denied',
      name: 'AccessDenied',
      component: AccessDeniedView,
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/tasks',
      name: 'tasks',
      component: () => import('../views/TasksView.vue'),
    },
    {
      path: '/tasks/:id',
      name: 'task',
      component: () => import('../views/TaskView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/pvp',
      name: 'pvp',
      component: () => import('../views/PvpView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/leaderboard',
      name: 'leaderboard',
      component: () => import('../views/LeaderboardView.vue'),
    },
    {
      path: '/auth',
      name: 'auth',
      component: () => import('../views/AuthView.vue'),
    },
    {
      path: '/auth/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
    },
    {
      path: '/statistics',
      name: 'statistics',
      component: () => import('../views/StatisticsView.vue'),
      meta: { requiresAuth: true },
    },

    // --- МАРШРУТЫ АДМИНКИ ---
    {
      path: '/admin',
      component: AdminView,
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        {
          path: '',
          redirect: '/admin/dashboard',
        },
        {
          path: 'dashboard',
          name: 'AdminDashboard',
          component: AdminDashboard,
        },
        {
          path: 'users',
          name: 'AdminUsers',
          component: AdminUsers,
        },
        {
          path: 'tasks',
          name: 'AdminTasks',
          component: AdminTasks,
        },
        {
          path: 'logs',
          name: 'AdminLogs',
          component: AdminLogs,
        },
      ],
    },
  ],
})

// Глобальная проверка прав
router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('user-token')
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)
  const requiresAdmin = to.matched.some((record) => record.meta.requiresAdmin)

  // 1. Если нужна авторизация, а токена нет — на страницу входа
  if (requiresAuth && !token) {
    return next('/auth')
  }

  // 2. Проверка прав администратора
  if (requiresAdmin) {
    try {
      // ⚠️ ВНИМАНИЕ: Проверьте этот адрес!
      // Если вашего эндпоинта нет по адресу /users/me, поменяйте его на правильный (например /auth/me)
      const response = await api.get('/profile/')

      const user = response.data

      // Лог для отладки (смотрите в консоли браузера F12)
      console.log('Проверка админа:', {
        username: user.username,
        is_admin: user.is_admin,
        endpoint: '/users/me',
      })

      // Если поле false или undefined — доступ запрещен
      if (!user.is_admin) {
        console.warn('Доступ запрещен: пользователь не админ')
        return next('/access-denied')
      }

      // Если всё ок — пропускаем
      return next()
    } catch (err) {
      // Подробный вывод ошибки в консоль
      console.error('ОШИБКА ПРОВЕРКИ ПРАВ:', err)

      if (err.response && err.response.status === 404) {
        console.error('❌ Эндпоинт /users/me не найден! Проверьте router/index.js')
      }

      // Если проверка не прошла (ошибка сети, 404, 500) — считаем, что доступа нет
      return next('/access-denied')
    }
  }

  next()
})

export default router
