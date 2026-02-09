<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="not-found-container">
    <div class="not-found-card">
      <div class="icon-wrapper">🛸</div>
      <h1 class="not-found-title">404</h1>
      <p class="not-found-subtitle">Страница не найдена</p>
      <p class="not-found-text">
        Кажется, вы заблудились в открытом космосе.<br />
        Такой страницы не существует.
      </p>
      <button @click="goHome" class="home-btn">← Вернуться на главную</button>
    </div>
  </div>
</template>

<style scoped>
/* --- КОНТЕЙНЕР --- */
.not-found-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  /* Светлая тема: Slate-50 */
  background-color: #f8fafc;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  transition: background-color 0.2s ease;
}

/* Темная тема: Slate-900 */
:root.dark .not-found-container {
  background-color: #0f172a;
}

/* --- КАРТОЧКА --- */
.not-found-card {
  background: white;
  padding: 40px;
  border-radius: 24px;
  /* Тень для светлой темы */
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 400px;
  width: 100%;
  border: 1px solid #e2e8f0;
  transition:
    background-color 0.2s ease,
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

/* Темная тема: Slate-800 */
:root.dark .not-found-card {
  background-color: #1e293b;
  border-color: #334155;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
}

/* --- ИКОНКА --- */
.icon-wrapper {
  font-size: 64px;
  margin-bottom: 16px;
  animation: float 3s ease-in-out infinite;
}

/* --- ЗАГОЛОВОК (404) --- */
.not-found-title {
  font-size: 48px;
  font-weight: 900;
  color: #4f46e5;
  margin: 0;
  line-height: 1;
}

/* В темной теме делаем заголовок чуть светлее для контраста */
:root.dark .not-found-title {
  color: #6366f1;
}

/* --- ПОДЗАГОЛОВОК --- */
.not-found-subtitle {
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
  margin-top: 8px;
  margin-bottom: 16px;
}

:root.dark .not-found-subtitle {
  color: #f8fafc;
}

/* --- ТЕКСТ --- */
.not-found-text {
  font-size: 15px;
  color: #64748b;
  margin-bottom: 32px;
  line-height: 1.6;
}

:root.dark .not-found-text {
  color: #94a3b8;
}

/* --- КНОПКА --- */
.home-btn {
  background-color: #4f46e5;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  transition:
    background-color 0.2s ease,
    transform 0.1s ease;
  width: 100%;
}

.home-btn:hover {
  background-color: #4338ca;
}

.home-btn:active {
  transform: translateY(1px);
}

/* Кнопка в темной теме */
:root.dark .home-btn {
  background-color: #4f46e5; /* Можно оставить тот же или #6366f1 */
}

:root.dark .home-btn:hover {
  background-color: #6366f1; /* Чуть светлее при наведении в темной теме */
}

/* --- АНИМАЦИЯ --- */
@keyframes float {
  0% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
  100% {
    transform: translateY(0px);
  }
}
</style>
