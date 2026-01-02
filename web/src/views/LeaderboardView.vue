<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const topUsers = ref([])
const loading = ref(true)
const error = ref(null)

/**
 * Загрузка данных таблицы лидеров с бэкенда
 * URL: http://127.0.0.1:8000/leaderboard/
 */
const fetchLeaderboard = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await axios.get('http://127.0.0.1:8000/leaderboard/')
    // Бэкенд возвращает список моделей UserModel
    topUsers.value = response.data
  } catch (err) {
    console.error("Ошибка загрузки таблицы лидеров:", err)
    error.value = "Не удалось загрузить список лучших"
  } finally {
    // Искусственная задержка для плавности анимации
    setTimeout(() => { loading.value = false }, 500)
  }
}

onMounted(() => {
  fetchLeaderboard()
})
</script>

<template>
  <div class="min-h-screen bg-slate-50 py-12 px-6 font-sans">
    <div class="max-w-4xl mx-auto space-y-10">

      <div class="text-center space-y-4 animate-fade-in">
        <div class="inline-block px-4 py-1 bg-amber-100 text-amber-600 text-[10px] font-black uppercase tracking-widest rounded-full shadow-sm border border-amber-200">
          Hall of Fame
        </div>
        <h1 class="text-5xl md:text-6xl font-black text-slate-900 tracking-tight leading-none">Зал славы</h1>
        <p class="text-slate-500 font-medium max-w-lg mx-auto text-lg">
          Десятка лучших умов платформы. Решай задачи, побеждай в PvP и возглавь этот список!
        </p>
      </div>

      <div class="bg-white rounded-[2.5rem] shadow-2xl shadow-slate-200/60 border border-slate-100 overflow-hidden relative">

        <div class="grid grid-cols-12 gap-4 px-10 py-6 bg-slate-900 text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">
          <div class="col-span-2 text-center">Ранг</div>
          <div class="col-span-7">Пользователь</div>
          <div class="col-span-3 text-right">Рейтинг ELO</div>
        </div>

        <div v-if="loading" class="divide-y divide-slate-50">
          <div v-for="n in 5" :key="n" class="grid grid-cols-12 gap-4 px-10 py-8 animate-pulse">
            <div class="col-span-2 flex justify-center"><div class="w-8 h-8 bg-slate-100 rounded-full"></div></div>
            <div class="col-span-7 flex items-center gap-4">
              <div class="w-12 h-12 bg-slate-100 rounded-xl"></div>
              <div class="h-4 w-32 bg-slate-100 rounded-full"></div>
            </div>
            <div class="col-span-3 flex justify-end"><div class="h-6 w-16 bg-slate-100 rounded-full"></div></div>
          </div>
        </div>

        <div v-else class="divide-y divide-slate-50">
          <div
            v-for="(user, index) in topUsers"
            :key="user.id"
            class="grid grid-cols-12 gap-4 px-10 py-7 items-center transition-all group border-l-4"
            :class="{
              'bg-gradient-to-r from-amber-50/50 to-transparent border-amber-400': index === 0,
              'bg-gradient-to-r from-slate-50/50 to-transparent border-slate-300': index === 1,
              'bg-gradient-to-r from-orange-50/50 to-transparent border-orange-300': index === 2,
              'hover:bg-slate-50/80 border-transparent': index > 2
            }"
          >
            <div class="col-span-2 flex justify-center items-center">
              <span v-if="index === 0" class="text-3xl drop-shadow-md">🥇</span>
              <span v-else-if="index === 1" class="text-3xl drop-shadow-md">🥈</span>
              <span v-else-if="index === 2" class="text-3xl drop-shadow-md">🥉</span>
              <span v-else class="text-xl font-black text-slate-200 tabular-nums">#{{ index + 1 }}</span>
            </div>

            <div class="col-span-7 flex items-center gap-5">
              <div
                class="w-12 h-12 rounded-2xl flex items-center justify-center text-white font-black text-xl shadow-lg transition-all duration-500 group-hover:rotate-6 group-hover:scale-110"
                :class="{
                  'bg-gradient-to-br from-amber-400 to-amber-600 shadow-amber-200': index === 0,
                  'bg-gradient-to-br from-slate-300 to-slate-500 shadow-slate-200': index === 1,
                  'bg-gradient-to-br from-orange-400 to-orange-600 shadow-orange-200': index === 2,
                  'bg-slate-200 text-slate-400': index > 2
                }"
              >
                {{ user.username.charAt(0).toUpperCase() }}
              </div>
              <div class="flex flex-col">
                <span class="font-black text-lg transition-colors" :class="index < 3 ? 'text-slate-900' : 'text-slate-700'">
                  {{ user.username }}
                </span>
                <span v-if="index === 0" class="text-[10px] font-bold text-amber-600 uppercase tracking-widest">Абсолютный лидер</span>
              </div>
            </div>

            <div
              class="col-span-3 text-right font-black text-2xl tracking-tighter"
              :class="{
                'text-amber-600': index === 0,
                'text-slate-500': index === 1,
                'text-orange-600': index === 2,
                'text-indigo-600': index > 2
              }"
            >
              {{ user.rating }}
            </div>
          </div>
        </div>
      </div>

      <div v-if="!loading" class="text-center pt-8 animate-fade-in-up">
        <router-link to="/pvp" class="inline-flex items-center gap-4 px-12 py-6 bg-slate-900 hover:bg-indigo-600 text-white font-black rounded-[2rem] shadow-2xl shadow-slate-200 transition-all active:scale-95 group">
          <span class="text-2xl group-hover:rotate-12 transition-transform">⚔️</span>
          <span class="text-lg">Бросить вызов</span>
          <span class="opacity-40 group-hover:translate-x-2 transition-transform">→</span>
        </router-link>
      </div>

    </div>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.8s ease-out;
}
.animate-fade-in-up {
  animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
