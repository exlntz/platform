<script setup>
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { ref, onMounted, watch, computed } from 'vue'
import { useTimerRunner } from '@/pinia/TimerRunner.js'
import { useConstantsStore } from '@/pinia/ConstantsStore.js' // <--- Импортируем
import ToastContainer from '@/components/ToastContainer.vue' // <-- Импорт
// runs once for entire SPA

const constantsStore = useConstantsStore() // <--- Инициализируем
useTimerRunner()

/**
 * Состояние авторизации для динамического переключения
 * между кнопкой "Войти" и блоком "Мой профиль"
 */
const isLoggedIn = ref(false)
const route = useRoute()
const isMenuOpen = ref(false)

/**
 * Состояние тёмной темы
 */
const darkTheme = ref(false)

/**
 * Функция проверки наличия токена в локальном хранилище
 */
const checkAuth = () => {
  isLoggedIn.value = !!localStorage.getItem('user-token')
}

/**
 * Функция для проверки и применения сохранённой темы
 */
const checkSavedTheme = () => {
  const savedTheme = localStorage.getItem('dark-theme')
  if (savedTheme === 'true') {
    darkTheme.value = true
    document.documentElement.classList.add('dark')
  } else {
    darkTheme.value = false
    document.documentElement.classList.remove('dark')
  }
}

/**
 * Функция переключения темы
 */
const toggleTheme = () => {
  darkTheme.value = !darkTheme.value
  if (darkTheme.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('dark-theme', 'true')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('dark-theme', 'false')
  }
}

/**
 * Иконка для кнопки переключения темы
 */
const themeIcon = computed(() => {
  return darkTheme.value ? '🌙' : '☀️'
})

/**
 * Текст для кнопки переключения темы (для скринридеров)
 */
const themeLabel = computed(() => {
  return darkTheme.value ? 'Переключить на светлую тему' : 'Переключить на тёмную тему'
})

// Инициализация проверки при первой загрузке компонента
onMounted(async () => {
  checkAuth()
  checkSavedTheme()
  
  // Проверяем системные настройки темы, если в localStorage нет сохранённой темы
  if (!localStorage.getItem('dark-theme')) {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      darkTheme.value = true
      document.documentElement.classList.add('dark')
      localStorage.setItem('dark-theme', 'true')
    }
  }
  await constantsStore.fetchConstants()
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

      <!-- Навигация для десктопа (только на больших экранах) -->
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
        <RouterLink to="/statistics" class="nav-link">
          Статистика
        </RouterLink>
        
        <!-- Кнопка переключения темы (только для десктопа) -->
        <button 
          @click="toggleTheme" 
          class="desktop-theme-toggle"
          :aria-label="themeLabel"
          :title="themeLabel"
        >
          <span class="desktop-theme-icon">{{ themeIcon }}</span>
          <span class="desktop-theme-text">{{ darkTheme ? 'Тёмная' : 'Светлая' }}</span>
        </button>
      </div>

      <!-- Правая часть шапки -->
      <div class="header-right">
        <!-- Кнопка переключения темы (для мобильных) -->
        <button 
          @click="toggleTheme" 
          class="mobile-theme-icon-button"
          :aria-label="themeLabel"
          :title="themeLabel"
        >
          <span class="theme-icon-small">{{ themeIcon }}</span>
        </button>

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

        <!-- Бургер-меню для мобильных (только на маленьких экранах) -->
        <button 
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
            <div class="mobile-header-actions">
              <!-- Кнопка переключения темы в мобильном меню -->
              <button 
                @click="toggleTheme" 
                class="mobile-menu-theme-button"
                :aria-label="themeLabel"
              >
                <span class="mobile-menu-theme-icon">{{ themeIcon }}</span>
              </button>
              <button class="mobile-menu-close" @click="closeMenu" aria-label="Закрыть меню">
                ✕
              </button>
            </div>
          </div>

          <!-- Переключатель темы в мобильном меню -->
          <div class="mobile-theme-toggle-section">
            <button 
              @click="toggleTheme" 
              class="mobile-theme-toggle-full"
              :aria-label="themeLabel"
            >
              <span class="mobile-theme-toggle-icon">{{ themeIcon }}</span>
              <span class="mobile-theme-toggle-text">{{ darkTheme ? 'Тёмная тема включена' : 'Светлая тема включена' }}</span>
              <span class="mobile-theme-toggle-switch">
                <span class="mobile-theme-toggle-track" :class="{ 'active': darkTheme }">
                  <span class="mobile-theme-toggle-thumb"></span>
                </span>
              </span>
            </button>
          </div>

          <div class="mobile-navigation">
            <RouterLink to="/" class="mobile-nav-link" @click="closeMenu">
              <span class="mobile-nav-icon">🏠</span>
              <span class="mobile-nav-text">Главная</span>
            </RouterLink>
            <RouterLink to="/tasks" class="mobile-nav-link" @click="closeMenu">
              <span class="mobile-nav-icon">📝</span>
              <span class="mobile-nav-text">Задачи</span>
            </RouterLink>
            <RouterLink to="/pvp" class="mobile-nav-link" @click="closeMenu">
              <span class="mobile-nav-icon">⚔️</span>
              <span class="mobile-nav-text">PvP Дуэли</span>
            </RouterLink>
            <RouterLink to="/leaderboard" class="mobile-nav-link" @click="closeMenu">
              <span class="mobile-nav-icon">🏆</span>
              <span class="mobile-nav-text">Рейтинг</span>
            </RouterLink>
            <RouterLink to="/statistics" class="mobile-nav-link" @click="closeMenu">
              <span class="mobile-nav-icon">📊</span>
              <span class="mobile-nav-text">Статистика</span>
            </RouterLink>
          </div>

          <div class="mobile-auth-section">
            <div v-if="isLoggedIn" class="mobile-profile">
              <div class="mobile-profile-icon">
                👤
              </div>
              <div class="mobile-profile-info">
                <div class="mobile-profile-name">Мой профиль</div>
                <div class="mobile-profile-status">В сети</div>
              </div>
              <RouterLink to="/profile" class="mobile-profile-button" @click="closeMenu">
                Перейти
              </RouterLink>
            </div>
            <RouterLink v-else to="/auth" class="mobile-auth-button" @click="closeMenu">
              <span class="mobile-auth-icon">🔐</span>
              <span class="mobile-auth-text">Войти в аккаунт</span>
            </RouterLink>
          </div>
        </div>
      </div>
    </nav>
  </header>

  <main class="min-h-screen bg-slate-50 dark:bg-gray-900 transition-colors duration-300">
    <ToastContainer /> <RouterView />
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
  transition: background-color 0.3s ease, border-color 0.3s ease;
  padding-left: 12px;
  padding-right: 12px;
}

.dark .header {
  background-color: rgba(15, 23, 42, 0.95);
  border-bottom: 1px solid rgb(30, 41, 59);
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.2);
}

.menu {
  max-width: 1280px;
  margin-left: auto;
  margin-right: auto;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 6px;
  text-decoration: none;
  z-index: 101;
  position: relative;
  min-width: fit-content;
  margin-left: 8px;
}

.logo {
  width: 28px;
  height: 28px;
  background-color: #4f46e5;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 900;
  font-size: 14px;
  box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.1),
              0 2px 4px -1px rgba(79, 70, 229, 0.06);
  transition: transform 0.3s ease;
  flex-shrink: 0;
}

.logo-container:hover .logo {
  transform: scale(1.05);
}

.text-logo {
  font-size: 14px;
  font-weight: 900;
  color: #1e293b;
  letter-spacing: -0.03em;
  text-transform: uppercase;
  transition: color 0.3s ease;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
}

.dark .text-logo {
  color: #f1f5f9;
}

.desktop-navigation {
  display: none;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: fit-content;
}

/* Кнопка переключения темы для мобильных */
.mobile-theme-icon-button {
  width: 36px;
  height: 36px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.dark .mobile-theme-icon-button {
  background: #334155;
  border-color: #475569;
  color: #f1f5f9;
}

.mobile-theme-icon-button:hover {
  background: #e2e8f0;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.dark .mobile-theme-icon-button:hover {
  background: #475569;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.theme-icon-small {
  font-size: 16px;
  transition: transform 0.3s ease;
}

.mobile-theme-icon-button:hover .theme-icon-small {
  transform: rotate(20deg);
}

.burger-menu {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  width: 28px;
  height: 20px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  z-index: 102;
  position: relative;
  flex-shrink: 0;
}

.burger-line {
  width: 100%;
  height: 2px;
  background-color: #4f46e5;
  border-radius: 1px;
  transition: all 0.3s ease;
}

.dark .burger-line {
  background-color: #818cf8;
}

.burger-menu[aria-expanded="true"] .burger-line:nth-child(1) {
  transform: rotate(45deg) translate(5px, 5px);
}

.burger-menu[aria-expanded="true"] .burger-line:nth-child(2) {
  opacity: 0;
}

.burger-menu[aria-expanded="true"] .burger-line:nth-child(3) {
  transform: rotate(-45deg) translate(5px, -5px);
}

.auth-block {
  display: none;
}

.profile-link {
  display: none;
}

.auth-link {
  padding: 6px 12px;
  background-color: #4f46e5;
  color: white;
  font-size: 12px;
  font-weight: 700;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.1),
              0 2px 4px -1px rgba(79, 70, 229, 0.06);
  transition: all 0.3s ease;
  text-decoration: none;
  border: none;
  cursor: pointer;
  display: none;
  white-space: nowrap;
}

.auth-link:hover {
  background-color: #4338ca;
  transform: translateY(-1px);
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
  max-width: 300px;
  height: 100%;
  background-color: white;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.1);
  animation: slideIn 0.3s ease-out;
  transition: background-color 0.3s ease;
  display: flex;
  flex-direction: column;
}

.dark .mobile-menu-content {
  background-color: #0f172a;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.3);
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
  padding: 16px;
  border-bottom: 1px solid #f1f5f9;
  transition: border-color 0.3s ease;
  flex-shrink: 0;
}

.dark .mobile-menu-header {
  border-bottom: 1px solid #1e293b;
}

.mobile-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
}

.mobile-logo .logo {
  width: 32px;
  height: 32px;
  font-size: 16px;
}

.mobile-header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mobile-menu-theme-button {
  width: 36px;
  height: 36px;
  background: #f8fafc;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.dark .mobile-menu-theme-button {
  background: #334155;
  color: #f1f5f9;
}

.mobile-menu-theme-button:hover {
  background: #e2e8f0;
  color: #4f46e5;
}

.dark .mobile-menu-theme-button:hover {
  background: #475569;
  color: #818cf8;
}

.mobile-menu-close {
  width: 36px;
  height: 36px;
  background: #f8fafc;
  border: none;
  border-radius: 8px;
  font-size: 18px;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.dark .mobile-menu-close {
  background: #334155;
  color: #f1f5f9;
}

.mobile-menu-close:hover {
  background: #f1f5f9;
  color: #4f46e5;
  transform: rotate(90deg);
}

.dark .mobile-menu-close:hover {
  background: #475569;
  color: #818cf8;
}

/* Переключатель темы в мобильном меню */
.mobile-theme-toggle-section {
  padding: 16px;
  border-bottom: 1px solid #f1f5f9;
  transition: border-color 0.3s ease;
  flex-shrink: 0;
}

.dark .mobile-theme-toggle-section {
  border-bottom: 1px solid #1e293b;
}

.mobile-theme-toggle-full {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  color: #475569;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.dark .mobile-theme-toggle-full {
  background: #334155;
  border-color: #475569;
  color: #e2e8f0;
}

.mobile-theme-toggle-full:hover {
  background: #e2e8f0;
}

.dark .mobile-theme-toggle-full:hover {
  background: #475569;
}

.mobile-theme-toggle-icon {
  font-size: 18px;
  width: 24px;
  text-align: center;
}

.mobile-theme-toggle-text {
  flex: 1;
  margin-left: 12px;
  text-align: left;
  font-size: 14px;
}

.mobile-theme-toggle-switch {
  width: 44px;
  height: 24px;
  padding-right: 35px;
  position: relative;
}

.mobile-theme-toggle-track {
  width: 100%;
  height: 100%;
  background: #cbd5e1;
  border-radius: 12px;
  position: relative;
  transition: background-color 0.3s ease;
}

.mobile-theme-toggle-track.active {
  background: #4f46e5;
}

.dark .mobile-theme-toggle-track {
  background: #475569;
}

.dark .mobile-theme-toggle-track.active {
  background: #818cf8;
}

.mobile-theme-toggle-thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  transition: transform 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.mobile-theme-toggle-track.active .mobile-theme-toggle-thumb {
  transform: translateX(20px);
}

.mobile-navigation {
  flex: 1;
  padding: 8px 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow-y: auto;
}

.mobile-nav-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  text-decoration: none;
  color: #334155;
  font-weight: 600;
  font-size: 15px;
  border-radius: 10px;
  transition: all 0.3s ease;
}

.dark .mobile-nav-link {
  color: #cbd5e1;
}

.mobile-nav-link:hover,
.mobile-nav-link.router-link-active {
  background-color: #f8fafc;
  color: #4f46e5;
}

.dark .mobile-nav-link:hover,
.dark .mobile-nav-link.router-link-active {
  background-color: #1e293b;
  color: #818cf8;
}

.mobile-nav-icon {
  font-size: 18px;
  width: 24px;
  text-align: center;
}

.mobile-nav-text {
  flex: 1;
}

.mobile-auth-section {
  padding: 16px;
  border-top: 1px solid #f1f5f9;
  transition: border-color 0.3s ease;
  flex-shrink: 0;
}

.dark .mobile-auth-section {
  border-top: 1px solid #1e293b;
}

.mobile-profile {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  background: #f8fafc;
  border-radius: 12px;
  margin-bottom: 12px;
  transition: background-color 0.3s ease;
}

.dark .mobile-profile {
  background: #1e293b;
}

.mobile-profile-icon {
  width: 36px;
  height: 36px;
  background: #e2e8f0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}

.dark .mobile-profile-icon {
  background: #334155;
}

.mobile-profile-info {
  flex: 1;
  min-width: 0;
}

.mobile-profile-name {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 2px;
  transition: color 0.3s ease;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dark .mobile-profile-name {
  color: #f1f5f9;
}

.mobile-profile-status {
  font-size: 12px;
  color: #94a3b8;
  font-weight: 500;
  transition: color 0.3s ease;
}

.mobile-profile-button {
  padding: 8px 14px;
  background: #4f46e5;
  color: white;
  font-size: 12px;
  font-weight: 600;
  border-radius: 8px;
  text-decoration: none;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.mobile-profile-button:hover {
  background-color: #4338ca;
  transform: translateY(-1px);
}

.mobile-auth-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 14px;
  background: #4f46e5;
  color: white;
  font-size: 15px;
  font-weight: 700;
  border-radius: 12px;
  text-align: center;
  text-decoration: none;
  transition: all 0.3s ease;
}

.mobile-auth-button:hover {
  background-color: #4338ca;
  transform: translateY(-1px);
}

.mobile-auth-icon {
  font-size: 16px;
}

.mobile-auth-text {
  flex: 1;
}

/* ==================== АДАПТИВНЫЕ СТИЛИ ==================== */

@media (max-width: 360px) {
  .menu {
    padding: 0 8px;
  }
  
  .logo-container {
    margin-left: 4px;
    gap: 4px;
  }
  
  .text-logo {
    max-width: 85px;
    font-size: 12px;
  }
  
  .logo {
    width: 24px;
    height: 24px;
    font-size: 12px;
  }
  
  .burger-menu {
    width: 24px;
    height: 18px;
  }
  
  .mobile-theme-icon-button {
    width: 32px;
    height: 32px;
  }
  
  .header-right {
    gap: 6px;
  }
}

@media (min-width: 380px) {
  .menu {
    padding: 0 12px;
  }
  
  .logo-container {
    margin-left: 12px;
  }
  
  .logo {
    width: 28px;
    height: 28px;
    font-size: 14px;
  }
  
  .text-logo {
    font-size: 14px;
    max-width: 100px;
  }
  
  .mobile-theme-icon-button {
    width: 36px;
    height: 36px;
  }
  
  .burger-menu {
    width: 28px;
    height: 20px;
  }
}

@media (min-width: 480px) {
  .menu {
    padding: 0 16px;
    height: 60px;
  }
  
  .logo-container {
    margin-left: 20px;
    gap: 8px;
  }
  
  .logo {
    width: 32px;
    height: 32px;
    font-size: 16px;
  }
  
  .text-logo {
    font-size: 16px;
    max-width: 120px;
  }
  
  .header-right {
    gap: 12px;
  }
}

@media (max-width: 640px) {
  .logo-container {
    margin-left: 50px;
  }
}

@media (max-width: 800px) {
  .burger-menu {
    display: flex;
  }
  
  .mobile-theme-icon-button {
    display: flex;
  }
  
  .desktop-navigation {
    display: none;
  }
  
  @media (min-width: 641px) {
    .menu {
      padding: 0 20px;
      height: 72px;
    }
    
    .logo-container {
      margin-left: 24px;
    }
    
    .logo {
      width: 36px;
      height: 36px;
      font-size: 18px;
    }
    
    .text-logo {
      font-size: 18px;
      max-width: none;
    }
    
    .auth-block {
      display: block;
    }
    
    .auth-link {
      display: inline-block;
      padding: 8px 16px;
      font-size: 14px;
    }
    
    .profile-link {
      display: flex;
      align-items: center;
      gap: 12px;
      padding-left: 16px;
      border-left: 1px solid #f1f5f9;
      text-decoration: none;
      transition: border-color 0.3s ease;
    }
    
    .dark .profile-link {
      border-left: 1px solid #1e293b;
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
      transition: color 0.3s ease;
    }
    
    .dark .small-text {
      color: #f1f5f9;
    }
    
    .profile-link:hover .small-text {
      color: #4f46e5;
    }
    
    .dark .profile-link:hover .small-text {
      color: #818cf8;
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
      transition: all 0.3s ease;
    }
    
    .dark .profile-icon {
      background-color: #334155;
      border-color: #475569;
    }
    
    .profile-link:hover .profile-icon {
      transform: scale(1.1);
    }
  }
}

@media (min-width: 801px) {
  .burger-menu {
    display: none;
  }
  
  .mobile-theme-icon-button {
    display: none;
  }
  
  .desktop-navigation {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-left: 32px;
    flex-wrap: wrap;
  }
  
  .nav-link {
    font-size: 14px;
    font-weight: 700;
    color: #64748b;
    transition: color 0.3s ease;
    text-decoration: none;
    white-space: nowrap;
  }
  
  .dark .nav-link {
    color: #94a3b8;
  }
  
  .nav-link:hover {
    color: #4f46e5;
  }
  
  .dark .nav-link:hover {
    color: #818cf8;
  }
  
  .nav-link.router-link-active {
    color: #4f46e5;
  }
  
  .dark .nav-link.router-link-active {
    color: #818cf8;
  }
  
  .desktop-theme-toggle {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 600;
    color: #475569;
    cursor: pointer;
    transition: all 0.3s ease;
    margin-left: 20px;
    white-space: nowrap;
  }
  
  .dark .desktop-theme-toggle {
    background: #334155;
    border-color: #475569;
    color: #e2e8f0;
  }
  
  .desktop-theme-toggle:hover {
    background: #e2e8f0;
    transform: translateY(-1px);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  }
  
  .dark .desktop-theme-toggle:hover {
    background: #475569;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
  }
  
  .desktop-theme-icon {
    font-size: 15px;
    transition: transform 0.3s ease;
  }
  
  .desktop-theme-toggle:hover .desktop-theme-icon {
    transform: rotate(30deg);
  }
  
  .desktop-theme-text {
    display: inline;
  }
  
  .auth-block {
    display: block;
  }
  
  .auth-link {
    display: inline-block;
    padding: 10px 24px;
    font-size: 14px;
    border-radius: 12px;
  }
  
  .profile-link {
    display: flex;
    align-items: center;
    gap: 12px;
    padding-left: 16px;
    border-left: 1px solid #f1f5f9;
    text-decoration: none;
    transition: border-color 0.3s ease;
  }
  
  .dark .profile-link {
    border-left: 1px solid #1e293b;
  }
  
  .profile-icon {
  width: 44px;               
  height: 44px;              
  min-width: 44px;           
  min-height: 44px;          
  background-color: #f1f5f9; 
  border-radius: 50%;        
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;           
  box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06);
  border: 3px solid white;   
  transition: all 0.3s ease;
  overflow: hidden;          
}

.dark .profile-icon {
  background-color: #334155;
  border-color: #1e293b;     
}

.profile-link:hover .profile-icon {
  transform: scale(1.05);    
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3); 
}
  
  .small-text {
    font-size: 12px;
  }
  
  .tiny-text {
    font-size: 10px;
  }
  
  .header-right {
    gap: 20px;
  }
}

@media (min-width: 801px) and (max-width: 1023px) {
  .desktop-navigation {
    gap: 8px;
    margin-left: 20px;
  }
  
  .nav-link {
    font-size: 12px;
  }
  
  .desktop-theme-toggle {
    padding: 6px 12px;
    font-size: 12px;
    margin-left: 12px;
  }
  
  .desktop-theme-icon {
    font-size: 12px;
  }
  
  .auth-link {
    padding: 8px 18px;
    font-size: 13px;
  }
}

@media (min-width: 1024px) {
  .menu {
    padding: 0 24px;
  }
  
  .desktop-navigation {
    gap: 25px;
    margin-left: 40px;
  }
  
  .nav-link {
    font-size: 14px;
  }
  
  .desktop-theme-toggle {
    padding: 8px 18px;
    font-size: 14px;
    margin-left: 24px;
  }
  
  .desktop-theme-icon {
    font-size: 16px;
  }
  
  .header-right {
    gap: 24px;
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