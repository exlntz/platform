<script setup>
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { ref, onMounted, watch } from 'vue'
import { useTimerRunner } from '@/pinia/TimerRunner.js'

// runs once for entire SPA
useTimerRunner()

/**
 * Состояние авторизации для динамического переключения
 * между кнопкой "Войти" и блоком "Мой профиль"
 */
const isLoggedIn = ref(false)
const route = useRoute()
const isMenuOpen = ref(false)

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
  // Закрываем меню при смене маршрута на мобильных устройствах
  isMenuOpen.value = false
})

/**
 * Функция переключения меню
 */
const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

/**
 * Функция закрытия меню
 */
const closeMenu = () => {
  isMenuOpen.value = false
}
</script>

<template>
  <header class="header">
    <nav class="menu">
      <!-- Логотип -->
      <RouterLink to="/" class="logo-container" @click="closeMenu">
        <div class="logo">
          L
        </div>
        <span class="text-logo">Platform</span>
      </RouterLink>

      <!-- Навигация для десктопа -->
      <div class="desktop-navigation">
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
          Рейтинг
        </RouterLink>
      </div>

      <!-- Правая часть шапки -->
      <div class="header-right">
        <!-- Блок авторизации/профиля -->
        <div class="auth-block">
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

        <!-- Бургер-меню для мобильных -->
        <button 
          v-show="!isMenuOpen"
          class="burger-menu" 
          @click="toggleMenu"
          :aria-expanded="isMenuOpen"
          aria-label="Меню навигации"
        >
          <span class="burger-line"></span>
          <span class="burger-line"></span>
          <span class="burger-line"></span>
        </button>
      </div>

      <!-- Мобильное меню (появляется при клике на бургер) -->
      <div v-if="isMenuOpen" class="mobile-menu">
        <div class="mobile-menu-overlay" @click="closeMenu"></div>
        <div class="mobile-menu-content">
          <div class="mobile-menu-header">
            <RouterLink to="/" class="mobile-logo" @click="closeMenu">
              <div class="logo">
                L
              </div>
              <span class="text-logo">Platform</span>
            </RouterLink>
            <button class="mobile-menu-close" @click="closeMenu" aria-label="Закрыть меню">
              ✕
            </button>
          </div>

          <div class="mobile-navigation">
            <RouterLink to="/" class="mobile-nav-link" @click="closeMenu">
              Главная
            </RouterLink>
            <RouterLink to="/tasks" class="mobile-nav-link" @click="closeMenu">
              Задачи
            </RouterLink>
            <RouterLink to="/pvp" class="mobile-nav-link" @click="closeMenu">
              PvP Дуэли
            </RouterLink>
            <RouterLink to="/leaderboard" class="mobile-nav-link" @click="closeMenu">
              Рейтинг
            </RouterLink>
          </div>

          <div class="mobile-auth-section">
            <div v-if="isLoggedIn" class="mobile-profile">
              <div class="mobile-profile-info">
                <div class="mobile-profile-name">Мой профиль</div>
                <div class="mobile-profile-status">В сети</div>
              </div>
              <RouterLink to="/profile" class="mobile-profile-button" @click="closeMenu">
                Перейти
              </RouterLink>
            </div>
            <RouterLink v-else to="/auth" class="mobile-auth-button" @click="closeMenu">
              Войти в аккаунт
            </RouterLink>
          </div>
        </div>
      </div>
    </nav>
  </header>

  <main class="min-h-screen bg-slate-50">
    <RouterView />
  </main>
</template>

<style scoped>
/* ==================== БАЗОВЫЕ СТИЛИ ==================== */

.header {
  position: sticky;
  top: 0;
  z-index: 100;
  background-color: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgb(241 245 249);
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  padding-left: 20px;
  padding-right: 20px;
}

.menu {
  max-width: 1280px;
  margin-left: auto;
  margin-right: auto;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  z-index: 101; 
  position: relative;
}

.logo {
  width: 32px;
  height: 32px;
  background-color: #4f46e5;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 900;
  font-size: 16px;
  box-shadow: 0 8px 12px -3px rgba(79, 70, 229, 0.1),
              0 3px 5px -3px rgba(79, 70, 229, 0.1);
  transition: transform 0.2s ease;
}

.text-logo {
  font-size: 16px;
  font-weight: 900;
  color: #1e293b;
  letter-spacing: -0.05em;
  text-transform: uppercase;
}

.desktop-navigation {
  display: none;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.burger-menu {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  width: 32px;
  height: 24px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  z-index: 102; 
  position: relative;
}

.burger-line {
  width: 100%;
  height: 3px;
  background-color: #4f46e5;
  border-radius: 2px;
  transition: all 0.3s ease;
}

.burger-menu[aria-expanded="true"] .burger-line:nth-child(1) {
  transform: rotate(45deg) translate(6px, 6px);
}

.burger-menu[aria-expanded="true"] .burger-line:nth-child(2) {
  opacity: 0;
}

.burger-menu[aria-expanded="true"] .burger-line:nth-child(3) {
  transform: rotate(-45deg) translate(6px, -6px);
}

.auth-block {
  display: none;
}

.profile-link {
  display: none;
}

.auth-link {
  padding: 8px 16px;
  background-color: #4f46e5;
  color: white;
  font-size: 14px;
  font-weight: 700;
  border-radius: 10px;
  box-shadow: 0 8px 12px -3px rgba(79, 70, 229, 0.1),
              0 3px 5px -3px rgba(79, 70, 229, 0.1);
  transition: all 0.2s ease;
  text-decoration: none;
  border: none;
  cursor: pointer;
  display: none;
}

.auth-link:hover {
  background-color: #4338ca;
}

.mobile-menu {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  z-index: 102; 
}

.mobile-menu-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}

.mobile-menu-content {
  position: absolute;
  top: 0;
  right: 0;
  width: 85%;
  max-width: 320px;
  height: 100%;
  background-color: white;
  box-shadow: -5px 0 25px rgba(0, 0, 0, 0.1);
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}

.mobile-menu-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border-bottom: 1px solid #f1f5f9;
}

.mobile-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
}

.mobile-logo .logo {
  width: 36px;
  height: 36px;
  font-size: 18px;
}

.mobile-menu-close {
  width: 36px;
  height: 36px;
  background: #f8fafc;
  border: none;
  border-radius: 8px;
  font-size: 20px;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.mobile-menu-close:hover {
  background: #f1f5f9;
  color: #4f46e5;
}

.mobile-navigation {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mobile-nav-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  text-decoration: none;
  color: #334155;
  font-weight: 600;
  font-size: 16px;
  border-radius: 12px;
  transition: all 0.2s ease;
}

.mobile-nav-link:hover,
.mobile-nav-link.router-link-active {
  background-color: #f8fafc;
  color: #4f46e5;
}

.mobile-auth-section {
  padding: 20px;
  border-top: 1px solid #f1f5f9;
}

.mobile-profile {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
  margin-bottom: 12px;
}

.mobile-profile-info {
  flex: 1;
}

.mobile-profile-name {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 2px;
}

.mobile-profile-status {
  font-size: 12px;
  color: #94a3b8;
  font-weight: 500;
}

.mobile-profile-button {
  padding: 8px 16px;
  background: #4f46e5;
  color: white;
  font-size: 13px;
  font-weight: 600;
  border-radius: 8px;
  text-decoration: none;
  transition: background-color 0.2s ease;
}

.mobile-profile-button:hover {
  background-color: #4338ca;
}

.mobile-auth-button {
  display: block;
  width: 100%;
  padding: 16px;
  background: #4f46e5;
  color: white;
  font-size: 16px;
  font-weight: 700;
  border-radius: 12px;
  text-align: center;
  text-decoration: none;
  transition: background-color 0.2s ease;
}

.mobile-auth-button:hover {
  background-color: #4338ca;
}

/* ==================== АДАПТИВНЫЕ СТИЛИ ==================== */

@media (min-width: 641px) {
  .header {
    padding-left: 0;
    padding-right: 0;
  }

  .menu {
    padding-left: 24px;
    padding-right: 24px;
    height: 72px;
  }

  .logo {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }

  .text-logo {
    font-size: 20px;
  }

  .auth-block {
    display: block;
  }

  .auth-link {
    display: inline-block;
  }

  .profile-link {
    display: flex;
    align-items: center;
    gap: 12px;
    padding-left: 16px;
    border-left: 1px solid #f1f5f9;
    text-decoration: none;
  }

  .profile-button {
    display: block;
    text-align: right;
  }

  .small-text {
    font-size: 12px;
    font-weight: 700;
    color: #0f172a;
    line-height: 1;
    transition: color 0.2s ease;
  }

  .profile-link:hover .small-text {
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
}


@media (min-width: 768px) {
  .burger-menu {
    display: none;
  }

  .desktop-navigation {
    display: flex;
    align-items: center;
    gap: 32px;
    margin-left: 32px;
  }

  .nav-link {
    font-size: 14px;
    font-weight: 700;
    color: #64748b;
    transition: color 0.2s ease;
    text-decoration: none;
  }

  .nav-link:hover {
    color: #4f46e5;
  }

  .nav-link.router-link-active {
    color: #4f46e5;
  }

  .auth-link {
    padding: 10px 24px;
    font-size: 14px;
    border-radius: 12px;
  }
}


@media (min-width: 1024px) {
  .menu {
    padding-left: 32px;
    padding-right: 32px;
  }
}


@media (min-width: 1280px) {
  .menu {
    max-width: 1280px;
  }
}


@media (min-width: 1536px) {
  .menu {
    max-width: 1400px;
  }
}
</style>