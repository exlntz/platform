<script>
import axios from "axios";

export default {
  name: "LeaderboardView",
  data() {
    return {
      // Данные пользователей
      topUsers: [
        { id: 1, username: "Alex_Pro", elo: 2840, wins: 150 },
        { id: 2, username: "Olimpiad_Master", elo: 2710, wins: 142 },
        { id: 3, username: "PythonLover", elo: 2590, wins: 130 },
        { id: 4, username: "CyberKnight", elo: 2400, wins: 110 },
        { id: 5, username: "DevHero", elo: 2350, wins: 95 },
        { id: 6, username: "CodeNinja", elo: 2200, wins: 88 },
        { id: 7, username: "LogicWizard", elo: 2150, wins: 82 },
        { id: 8, username: "AlgoQueen", elo: 2100, wins: 79 },
        { id: 9, username: "BinaryBoss", elo: 2050, wins: 75 },
        { id: 10, username: "FastSolver", elo: 2000, wins: 70 }
      ],
      loading: false
    }
  },
  mounted() {
    // this.fetchLeaderboard();
  },
  methods: {
    async fetchLeaderboard() {
      this.loading = true;
      try {
        const response = await axios.get('http://127.0.0.1:8000/users/leaderboard');
        this.topUsers = response.data.slice(0, 10);
      } catch (err) {
        console.error("Ошибка загрузки таблицы лидеров:", err);
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 py-12 px-6 font-sans">
    <div class="max-w-4xl mx-auto space-y-10">

      <div class="text-center space-y-4">
        <div class="inline-block px-4 py-1 bg-amber-100 text-amber-600 text-[10px] font-black uppercase tracking-widest rounded-full">
          Hall of Fame
        </div>
        <h1 class="text-5xl font-black text-slate-900 tracking-tight">Зал славы</h1>
        <p class="text-slate-500 font-medium max-w-lg mx-auto">Десятка лучших умов платформы. Решай задачи, побеждай в PvP и попади в этот список!</p>
      </div>

      <div class="bg-white rounded-[2.5rem] shadow-2xl shadow-slate-200/50 border border-slate-100 overflow-hidden">

        <div class="grid grid-cols-12 gap-4 px-8 py-6 bg-slate-900 text-[10px] font-black text-slate-400 uppercase tracking-widest">
          <div class="col-span-2 text-center">Ранг</div>
          <div class="col-span-6">Пользователь</div>
          <div class="col-span-2 text-right">Победы</div>
          <div class="col-span-2 text-right">Рейтинг</div>
        </div>

        <div class="divide-y divide-slate-50">
          <div
            v-for="(user, index) in topUsers"
            :key="user.id"
            class="grid grid-cols-12 gap-4 px-8 py-6 items-center transition-all group border-l-4"
            :class="{
              'bg-gradient-to-r from-amber-50 to-white border-amber-400': index === 0,
              'bg-gradient-to-r from-slate-50 to-white border-slate-300': index === 1,
              'bg-gradient-to-r from-orange-50 to-white border-orange-300': index === 2,
              'hover:bg-slate-50 border-transparent': index > 2
            }"
          >
            <div class="col-span-2 flex justify-center items-center">
              <span v-if="index === 0" class="text-2xl drop-shadow-sm">🥇</span>
              <span v-else-if="index === 1" class="text-2xl drop-shadow-sm">🥈</span>
              <span v-else-if="index === 2" class="text-2xl drop-shadow-sm">🥉</span>
              <span v-else class="text-lg font-black text-slate-300 ml-1">#{{ index + 1 }}</span>
            </div>

            <div class="col-span-6 flex items-center gap-4">
              <div
                class="w-10 h-10 rounded-xl flex items-center justify-center text-white font-black shadow-lg transition-transform group-hover:rotate-6"
                :class="{
                  'bg-amber-500 shadow-amber-200': index === 0,
                  'bg-slate-400 shadow-slate-200': index === 1,
                  'bg-orange-500 shadow-orange-200': index === 2,
                  'bg-slate-200 text-slate-500': index > 2
                }"
              >
                {{ user.username.charAt(0).toUpperCase() }}
              </div>
              <span
                class="font-bold transition-colors"
                :class="index < 3 ? 'text-slate-900' : 'text-slate-600'"
              >
                {{ user.username }}
              </span>
            </div>

            <div class="col-span-2 text-right font-bold text-slate-400 italic">
              {{ user.wins }}
            </div>

            <div
              class="col-span-2 text-right font-black text-lg tracking-tight"
              :class="{
                'text-amber-600': index === 0,
                'text-slate-500': index === 1,
                'text-orange-600': index === 2,
                'text-slate-900': index > 2
              }"
            >
              {{ user.elo }}
            </div>
          </div>
        </div>

      </div>

      <div v-if="!loading" class="text-center pt-4">
        <router-link to="/pvp" class="inline-flex items-center gap-3 px-10 py-5 bg-indigo-600 hover:bg-indigo-700 text-white font-black rounded-2xl shadow-xl shadow-indigo-100 transition-all active:scale-95 group">
          <span class="text-xl group-hover:scale-125 transition-transform">⚔️</span>
          <span>Бросить вызов</span>
        </router-link>
      </div>

    </div>
  </div>
</template>
