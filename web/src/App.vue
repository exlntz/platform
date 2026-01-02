<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { ref, onMounted } from 'vue'

// Состояние авторизации для отображения Профиля или Входа
const isLoggedIn = ref(false)

onMounted(() => {
  isLoggedIn.value = !!localStorage.getItem('user-token')
})
</script>

<template>
  <header class="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-100 shadow-sm">
    <nav class="max-w-7xl mx-auto px-6 h-18 flex items-center justify-between">

      <RouterLink to="/" class="flex items-center gap-2 group">
        <div class="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center text-white font-black text-xl shadow-lg shadow-indigo-100 group-hover:rotate-6 transition-transform">
          L
        </div>
        <span class="text-xl font-black text-slate-800 tracking-tighter">PLATFORM</span>
      </RouterLink>

      <div class="hidden md:flex items-center gap-x-8">
        <RouterLink
          to="/"
          active-class="text-indigo-600"
          class="text-sm font-bold text-slate-500 hover:text-indigo-600 transition-colors"
        >
          Главная
        </RouterLink>
        <RouterLink
          to="/tasks"
          active-class="text-indigo-600"
          class="text-sm font-bold text-slate-500 hover:text-indigo-600 transition-colors"
        >
          Задачи
        </RouterLink>
        <RouterLink
          to="/pvp"
          active-class="text-indigo-600"
          class="text-sm font-bold text-slate-500 hover:text-indigo-600 transition-colors"
        >
          PvP Дуэли
        </RouterLink>

        <RouterLink
          to="/leaderboard"
          active-class="text-indigo-600"
          class="text-sm font-bold text-slate-500 hover:text-indigo-600 transition-colors flex items-center gap-1.5"
        >
          <span>🏆</span> Рейтинг
        </RouterLink>
      </div>

      <div class="flex items-center gap-x-4">
        <RouterLink
          v-if="isLoggedIn"
          to="/profile"
          class="flex items-center gap-3 pl-4 border-l border-slate-100"
        >
          <div class="text-right hidden sm:block">
            <p class="text-xs font-bold text-slate-900 leading-none">Мой профиль</p>
            <p class="text-[10px] font-medium text-slate-400">В сети</p>
          </div>
          <div class="w-10 h-10 bg-slate-100 rounded-full flex items-center justify-center text-lg shadow-inner border border-white">
            👤
          </div>
        </RouterLink>

        <RouterLink
          v-else
          to="/auth"
          class="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-bold rounded-xl shadow-lg shadow-indigo-100 transition-all active:scale-95"
        >
          Войти
        </RouterLink>
      </div>

    </nav>
  </header>

  <main class="min-h-screen bg-slate-50">
    <RouterView />
  </main>
</template>
