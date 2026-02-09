import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AccessDeniedView from '../views/AccessDeniedView.vue'
import api from '@/api/axios.js'

import AdminView from '@/views/admin/AdminView.vue'
import AdminDashboard from '@/views/admin/tabs/AdminDashboard.vue'
import AdminUsers from '@/views/admin/tabs/AdminUsers.vue'
import AdminTasks from '@/views/admin/tabs/AdminTasks.vue'
import AdminLogs from '@/views/admin/tabs/AdminLogs.vue'
import AdminPvp from '@/views/admin/tabs/AdminPvp.vue'
import NotFoundView from '../views/NotFoundView.vue'

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
        {
          path: 'pvp',
          name: 'AdminPvp',
          component: AdminPvp,
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*', // Это регулярное выражение "любой путь"
      name: 'NotFound',
      component: NotFoundView,
    },
  ],
})


router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('user-token')
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)
  const requiresAdmin = to.matched.some((record) => record.meta.requiresAdmin)


  if (requiresAuth && !token) {
    return next('/auth')
  }


  if (requiresAdmin) {
    try {

      const response = await api.get('/profile/')

      const user = response.data

      console.log('Проверка админа:', {
        username: user.username,
        is_admin: user.is_admin,
        endpoint: '/users/me',
      })

      if (!user.is_admin) {
        console.warn('Доступ запрещен: пользователь не админ')
        return next('/access-denied')
      }

      return next()
    } catch (err) {
      console.error('ОШИБКА ПРОВЕРКИ ПРАВ:', err)

      if (err.response && err.response.status === 404) {
        console.error('❌ Эндпоинт /users/me не найден! Проверьте router/index.js')
      }

      return next('/access-denied')
    }
  }

  next()
})

export default router
