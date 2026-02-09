import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

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
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/tasks',
      name: 'tasks',
      component: () => import('../views/TasksView.vue'),
      // meta: { requiresAuth: true },
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
      meta: { requiresAuth: true }, // Можно добавить поле requiresAdmin: true, если допишешь проверку роли
      children: [
        {
          path: '',
          redirect: '/admin/dashboard', // Перенаправляем пустой /admin сразу на дашборд
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

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('user-token')
  if (to.meta.requiresAuth && !token) {
    next('/auth')
  } else {
    next()
  }
})

export default router
