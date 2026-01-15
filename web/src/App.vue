<script setup>
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { ref, onMounted, watch } from 'vue'
import { useTimerRunner } from '@/TimerRunner.js'


// runs once for entire SPA
useTimerRunner()



/**
 * Состояние авторизации для динамического переключения
 * между кнопкой "Войти" и блоком "Мой профиль"
 */
const isLoggedIn = ref(false)
const route = useRoute()

/**
 * Функция проверки наличия токена в локальном хранилище
 */
const checkAuth = () => {
  isLoggedIn.value = !!localStorage.getItem('user-token')
}

// Инициализация проверки при первой загрузке компонента
onMounted(() => {
  checkAuth()
})

/**
 * Реактивное отслеживание смены маршрута.
 * Позволяет обновлять статус входа сразу после редиректа из формы логина
 */
watch(() => route.path, () => {
  checkAuth()
})
</script>

<template>
  <header class="header">
    <nav class="menu">

      <RouterLink to="/" class="flex">
        <div class="logo">
          L
        </div>
        <span class="text-logo">Platform</span>
      </RouterLink>

      <div class="navigation">
        <RouterLink to="/" class="nav-link">
          Главная
        </RouterLink>
        <RouterLink to="/tasks" class="nav-link">
          Задачи
        </RouterLink>
        <RouterLink to="/pvp" class="nav-link">
          PvP Дуэли
        </RouterLink>
        <RouterLink to="/leaderboard" class="nav-link">
          <span>🏆</span> Рейтинг
        </RouterLink>
      </div>

      <div class="flex">
        <RouterLink v-if="isLoggedIn" to="/profile" class="profile-link">
          <div class="profile-button">
            <p class="small-text">Мой профиль</p>
            <p class="tiny-text">В сети</p>
          </div>
          <div class="profile-icon">
            👤
          </div>
        </RouterLink>

        <RouterLink v-else to="/auth" class="auth-link">
          Войти
        </RouterLink>
      </div>

    </nav>
  </header>

  <main class="min-h-screen bg-slate-50">
    <RouterView />
  </main>
</template>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 50;
  background-color: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgb(241 245 249);
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}
.header .menu {
  max-width: 1280px;
  margin-left: auto;
  margin-right: auto;
  padding-left: 24px;
  padding-right: 1.5rem;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.flex {
  display: flex;
  align-items: center;
  gap: 8px;
}
.logo {
  width: 40px;
  height: 40px;
  background-color: #4f46e5;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 900;
  font-size: 20px;
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.1),
              0 4px 6px -4px rgba(79, 70, 229, 0.1);
  transition: transform 0.2s ease;
}
.logo:hover {
  transform: rotate(6deg);
}
.text-logo {
  font-size: 20px;
  font-weight: 900;
  color: #1e293b;
  letter-spacing: -0.05em;
  text-transform: uppercase;
}
.navigation {
  display: none;
}
@media (min-width: 768px) {
  .navigation {
    display: flex;
    align-items: center;
    gap: 32px;
  }
}
.nav-link {
  font-size: 14px;
  font-weight: 700;
  color: #64748b;
  transition: color 0.2s ease;
}
.nav-link:hover {
  color: #4f46e5;
}
.nav-link:active {
  color: #4f46e5;
}
.profile-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-left: 16px;
  border-left: 1px solid #f1f5f9;
}
.profile-link:hover {
  border-left-color: #4f46e5;
}
.profile-button {
  display: none;
  text-align: right;
}
@media (min-width: 640px) {
  .profile-button {
    display: block;
  }
}
.small-text {
  font-size: 12px;
  font-weight: 700;
  color: #0f172a;
  line-height: 1;
  transition: color 0.2s ease;
}
.profile-button:hover .small-text {
  color: #4f46e5;
}
.tiny-text {
  font-size: 10px;
  font-weight: 500;
  color: #94a3b8;
}
.profile-icon {
  width: 40px;
  height: 40px;
  background-color: #f1f5f9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06);
  border: 1px solid white;
  transition: transform 0.2s ease;
}
.profile-link:hover .profile-icon {
  transform: scale(1.1);
}
.auth-link {
  padding: 10px 24px;
  background-color: #4f46e5;
  color: white;
  font-size: 14px;
  font-weight: 700;
  border-radius: 12px;
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.1),
              0 4px 6px -4px rgba(79, 70, 229, 0.1);
  transition: all 0.2s ease;
  border: none;
  cursor: pointer;
}
.auth-link:hover {
  background-color: #4338ca;
}
.auth-link:active {
  transform: scale(0.95);
}
</style>
