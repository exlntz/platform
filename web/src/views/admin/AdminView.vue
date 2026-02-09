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
.admin-container {
  min-height: 100vh;
  background-color: #f8fafc;
  font-family:
    -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  position: relative;
  display: flex;
}

:root.dark .admin-container {
  background-color: #0f172a;
}

/* Sidebar */
.admin-sidebar {
  width: 256px;
  background-color: #0f172a;
  color: white;
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  z-index: 95;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

:root.dark .admin-sidebar {
  background-color: #1e293b;
  border-right: 1px solid #334155;
}

@media (max-width: 640px) {
  .admin-sidebar {
    transform: translateX(-100%);
  }
  .sidebar-collapsed {
    transform: translateX(0);
  }
}

.sidebar-header {
  padding: 24px;
  border-bottom: 1px solid #1e293b;
  display: flex;
  align-items: center;
  gap: 12px;
}

.sidebar-logo {
  width: 32px;
  height: 32px;
  background-color: #6366f1;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  box-shadow: 0 0 15px rgba(99, 102, 241, 0.4);
  font-size: 16px;
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
  font-weight: 500;
  font-size: 14px;
  border: none;
  cursor: pointer;
  background: none;
  color: #94a3b8;
  text-align: left;
}

.nav-btn.active {
  background-color: #4f46e5;
  color: white;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
}
.nav-btn:not(.active):hover {
  background-color: #1e293b;
  color: white;
}
.nav-icon {
  font-size: 18px;
}

.sidebar-footer {
  padding: 24px;
  border-top: 1px solid #1e293b;
}

.back-to-site {
  display: block;
  text-align: center;
  color: #94a3b8;
  font-size: 13px;
  font-weight: 700;
  text-decoration: none;
  transition: color 0.2s ease;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #1e293b;
}
.back-to-site:hover {
  color: white;
  background-color: #1e293b;
  border-color: #334155;
}

/* Main Content */
.admin-main {
  flex: 1;
  padding: 24px;
  margin-left: 256px;
  width: calc(100% - 256px);
  min-height: 100vh;
  box-sizing: border-box;
}
:root.dark .admin-main {
  background-color: #0f172a;
}

@media (max-width: 640px) {
  .admin-main {
    margin-left: 0;
    width: 100%;
    padding: 16px;
    padding-top: 60px;
  }
}

/* Mobile Menu */
.mobile-menu-btn {
  position: fixed;
  top: 16px;
  left: 16px;
  z-index: 100;
  width: 40px;
  height: 40px;
  background: white;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  display: none;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
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
