<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const isSidebarCollapsed = ref(false)

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

const navigateTo = (path) => {
  router.push(path)
  isSidebarCollapsed.value = false
}

const isActive = (pathPart) => {
  return route.path.includes(`/admin/${pathPart}`)
}
</script>

<template>
  <div class="admin-container">
    <div class="mobile-menu-btn" @click="toggleSidebar">
      <span class="burger-line"></span>
      <span class="burger-line"></span>
      <span class="burger-line"></span>
    </div>

    <div class="mobile-overlay" v-if="isSidebarCollapsed" @click="toggleSidebar"></div>

    <aside class="admin-sidebar" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
      <div class="sidebar-header">
        <div class="sidebar-logo">A</div>
        <span class="sidebar-title">Admin Panel</span>
        <button class="sidebar-close" @click="toggleSidebar">✕</button>
      </div>

      <nav class="sidebar-nav">
        <button
          @click="navigateTo('/admin/dashboard')"
          class="nav-btn"
          :class="{ active: isActive('dashboard') }"
        >
          <span class="nav-icon">📊</span> <span class="nav-text">Дашборд</span>
        </button>
        <button
          @click="navigateTo('/admin/users')"
          class="nav-btn"
          :class="{ active: isActive('users') }"
        >
          <span class="nav-icon">👥</span> <span class="nav-text">Пользователи</span>
        </button>
        <button
          @click="navigateTo('/admin/tasks')"
          class="nav-btn"
          :class="{ active: isActive('tasks') }"
        >
          <span class="nav-icon">📝</span> <span class="nav-text">Задачи</span>
        </button>
        <button
          @click="navigateTo('/admin/pvp')"
          class="nav-btn"
          :class="{ active: isActive('pvp') }"
        >
          <span class="nav-icon">⚔️</span> <span class="nav-text">PvP Матчи</span>
        </button>
        <button
          @click="navigateTo('/admin/logs')"
          class="nav-btn"
          :class="{ active: isActive('logs') }"
        >
          <span class="nav-icon">🛡️</span> <span class="nav-text">Логи</span>
        </button>
      </nav>

      <div class="sidebar-footer">
        <router-link to="/" class="back-to-site">← Вернуться на сайт</router-link>
      </div>
    </aside>

    <main class="admin-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<style scoped>
/* --- БАЗОВЫЙ КОНТЕЙНЕР --- */
.admin-container {
  min-height: 100vh;
  background-color: #f1f5f9; /* Светлый фон по умолчанию */
  font-family:
    -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  position: relative;
  display: flex;
  transition: background-color 0.2s ease;
}

:root.dark .admin-container {
  background-color: #0f172a; /* Темный фон всего контейнера */
}

/* --- SIDEBAR (Меню) --- */
.admin-sidebar {
  width: 256px;
  /* СВЕТЛАЯ ТЕМА ПО УМОЛЧАНИЮ */
  background-color: white;
  color: #0f172a;
  border-right: 1px solid #e2e8f0;

  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  z-index: 95;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.05);
  transition:
    transform 0.3s ease,
    background-color 0.2s ease,
    border-color 0.2s ease;
}

/* ТЕМНАЯ ТЕМА ДЛЯ МЕНЮ */
:root.dark .admin-sidebar {
  background-color: #1e293b; /* Ваш цвет фона для темных панелей */
  color: #f1f5f9;
  border-right: 1px solid #334155; /* Цвет рамок в темной теме */
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.2);
}

@media (max-width: 640px) {
  .admin-sidebar {
    transform: translateX(-100%);
  }
  .sidebar-collapsed {
    transform: translateX(0);
  }
}

/* --- HEADER МЕНЮ --- */
.sidebar-header {
  padding: 24px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: border-color 0.2s ease;
}

:root.dark .sidebar-header {
  border-bottom: 1px solid #334155;
}

.sidebar-logo {
  width: 32px;
  height: 32px;
  background-color: #4f46e5;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  box-shadow: 0 0 15px rgba(79, 70, 229, 0.4);
  font-size: 16px;
  color: white;
}

.sidebar-title {
  font-weight: 700;
  font-size: 16px;
  letter-spacing: -0.01em;
}

.sidebar-close {
  display: none;
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 20px;
  margin-left: auto;
  cursor: pointer;
}
@media (max-width: 640px) {
  .sidebar-close {
    display: block;
  }
}

/* --- НАВИГАЦИЯ --- */
.sidebar-nav {
  flex: 1;
  padding: 24px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.nav-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 12px;
  transition: all 0.2s ease;
  font-weight: 600;
  font-size: 14px;
  border: none;
  cursor: pointer;
  background: none;

  /* Цвета кнопок в СВЕТЛОЙ теме */
  color: #64748b;
  text-align: left;
}

/* Цвета кнопок в ТЕМНОЙ теме */
:root.dark .nav-btn {
  color: #94a3b8; /* Используем ваш цвет для неактивного текста */
}

/* --- Стили для АКТИВНОЙ кнопки (одинаковые для обеих тем, но можно менять) --- */
.nav-btn.active {
  background-color: #4f46e5;
  color: white;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
}
:root.dark .nav-btn.active {
  color: white; /* Убеждаемся, что текст белый */
}

/* --- HOVER (Наведение) --- */
.nav-btn:not(.active):hover {
  background-color: #f1f5f9; /* Светлый ховер */
  color: #0f172a;
}

:root.dark .nav-btn:not(.active):hover {
  background-color: #334155; /* Ваш темный цвет фона (как у инпутов) */
  color: #f1f5f9;
}

.nav-icon {
  font-size: 18px;
}

/* --- FOOTER МЕНЮ --- */
.sidebar-footer {
  padding: 24px;
  border-top: 1px solid #e2e8f0;
  transition: border-color 0.2s ease;
}

:root.dark .sidebar-footer {
  border-top: 1px solid #334155;
}

.back-to-site {
  display: block;
  text-align: center;
  font-size: 13px;
  font-weight: 700;
  text-decoration: none;
  transition: all 0.2s ease;
  padding: 10px;
  border-radius: 8px;

  /* Светлая тема */
  color: #64748b;
  border: 1px solid #e2e8f0;
  background-color: transparent;
}

/* Темная тема */
:root.dark .back-to-site {
  color: #94a3b8;
  border-color: #475569; /* Ваш цвет бордера */
}

.back-to-site:hover {
  background-color: #f1f5f9;
  color: #0f172a;
  border-color: #cbd5e1;
}

:root.dark .back-to-site:hover {
  background-color: #334155;
  color: white;
}

/* --- MAIN CONTENT --- */
.admin-main {
  flex: 1;
  padding: 24px;
  margin-left: 256px;
  width: calc(100% - 256px);
  min-height: 100vh;
  box-sizing: border-box;
}

@media (max-width: 640px) {
  .admin-main {
    margin-left: 0;
    width: 100%;
    padding: 16px;
    padding-top: 60px;
  }
}

/* --- MOBILE BUTTON --- */
.mobile-menu-btn {
  position: fixed;
  top: 16px;
  left: 16px;
  z-index: 100;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: none;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);

  /* Светлая тема */
  background: white;
  border: 1px solid #e2e8f0;
}

:root.dark .mobile-menu-btn {
  background-color: #1e293b;
  border-color: #334155;
}

@media (max-width: 640px) {
  .mobile-menu-btn {
    display: flex;
  }
}

.burger-line {
  width: 20px;
  height: 2px;
  background-color: #0f172a;
  border-radius: 1px;
}

:root.dark .burger-line {
  background-color: #f8fafc;
}

.mobile-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(2px);
  z-index: 90;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
