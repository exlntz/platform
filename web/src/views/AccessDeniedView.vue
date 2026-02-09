<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="denied-container">
    <div class="denied-card">
      <div class="icon-wrapper">🚫</div>
      <h1 class="denied-title">Доступ запрещен</h1>
      <p class="denied-text">
        У вас недостаточно прав для просмотра этой страницы.<br />
        Этот раздел доступен только администраторам.
      </p>
      <button @click="goHome" class="home-btn">← Вернуться на главную</button>
    </div>
  </div>
</template>

<style scoped>
.denied-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8fafc;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}

:root.dark .denied-container {
  background-color: #0f172a;
}

.denied-card {
  background: white;
  padding: 40px;
  border-radius: 24px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 400px;
  width: 100%;
  border: 1px solid #e2e8f0;
}

:root.dark .denied-card {
  background-color: #1e293b;
  border-color: #334155;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
}

.icon-wrapper {
  font-size: 64px;
  margin-bottom: 24px;
}

.denied-title {
  font-size: 24px;
  font-weight: 900;
  color: #0f172a;
  margin-bottom: 12px;
}

:root.dark .denied-title {
  color: #f8fafc;
}

.denied-text {
  font-size: 15px;
  color: #64748b;
  line-height: 1.5;
  margin-bottom: 32px;
}

:root.dark .denied-text {
  color: #94a3b8;
}

.home-btn {
  width: 100%;
  padding: 14px;
  background-color: #4f46e5;
  color: white;
  font-weight: 700;
  font-size: 14px;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  transition:
    background-color 0.2s ease,
    transform 0.1s ease;
}

.home-btn:hover {
  background-color: #4338ca;
}

.home-btn:active {
  transform: scale(0.98);
}

:root.dark .home-btn {
  background-color: #3b82f6;
}

:root.dark .home-btn:hover {
  background-color: #2563eb;
}
</style>
