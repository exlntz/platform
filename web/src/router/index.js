import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

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
      meta: { requiresAuth: true },
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
    // НОВЫЙ МАРШРУТ ДЛЯ РЕЙТИНГА
    {
      path: '/leaderboard',
      name: 'leaderboard',
      // Используем ленивую загрузку (lazy-loading) для оптимизации
      component: () => import('../views/LeaderboardView.vue'),
      // Оставляем без requiresAuth, чтобы рейтинг был доступен всем
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
  ],
})

// Навигационный гард для проверки авторизации
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('user-token')
  if (to.meta.requiresAuth && !token) {
    next('/auth')
  } else {
    next()
  }
})

export default router
