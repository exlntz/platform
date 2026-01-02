<script>
export default {
  name: "PvpView",
  data() {
    return {
      searching: false,
      // Моковые данные для демонстрации дизайна
      stats: { rank: "Gold IV", points: 1250, winStreak: 3 },
      leaderboard: [
        { id: 1, name: "Alex_Pro", points: 2840, avatar: "⚔️" },
        { id: 2, name: "Olimpiad_Master", points: 2710, avatar: "🔥" },
        { id: 3, name: "PythonLover", points: 2590, avatar: "🐍" }
      ],
      activeMatches: [
        { id: 101, p1: "User123", p2: "Bot_Hard", subject: "Math" },
        { id: 102, p1: "DevHero", p2: "CyberPonk", subject: "Informatics" }
      ]
    }
  },
  methods: {
    startMatchmaking() {
      this.searching = true;
      // Здесь будет логика поиска через WebSocket
      setTimeout(() => {
        alert("Поиск противника начат...");
      }, 500);
    }
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 py-12 px-6 font-sans">
    <div class="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">

      <div class="lg:col-span-2 space-y-8">
        <div class="relative overflow-hidden bg-slate-900 rounded-[2.5rem] p-10 shadow-2xl shadow-indigo-200">
          <div class="relative z-10 space-y-6">
            <div class="inline-block px-4 py-1 bg-indigo-500/20 text-indigo-300 text-[10px] font-black uppercase tracking-widest rounded-full border border-indigo-500/30">
              Live Arena
            </div>
            <h1 class="text-5xl font-black text-white tracking-tight">PvP Матчи</h1>
            <p class="text-indigo-200 max-w-md font-medium">Вызывай других участников на дуэль, решай задачи на скорость и забирай их очки рейтинга.</p>

            <button
              @click="startMatchmaking"
              :class="searching ? 'bg-amber-500' : 'bg-[#1fb141] hover:bg-[#199435]'"
              class="flex items-center gap-3 px-10 py-5 text-white font-black rounded-2xl shadow-xl transition-all transform hover:scale-105 active:scale-95"
            >
              <span v-if="!searching">🔥 Найти противника</span>
              <span v-else class="flex items-center gap-2">
                <span class="animate-ping w-2 h-2 bg-white rounded-full"></span>
                Поиск оппонента...
              </span>
            </button>
          </div>
          <div class="absolute -right-20 -bottom-20 w-80 h-80 bg-indigo-600/20 rounded-full blur-3xl"></div>
        </div>

        <div class="space-y-4">
          <h2 class="text-2xl font-black text-slate-800 ml-4">Прямо сейчас в бою 🔴</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-for="match in activeMatches" :key="match.id" class="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm flex items-center justify-between">
              <div class="text-center flex-1">
                <p class="font-bold text-slate-900">{{ match.p1 }}</p>
                <span class="text-[10px] text-slate-400 font-black uppercase">Rank 1200</span>
              </div>
              <div class="px-4 font-black text-indigo-600 italic text-xl italic">VS</div>
              <div class="text-center flex-1">
                <p class="font-bold text-slate-900">{{ match.p2 }}</p>
                <span class="text-[10px] text-slate-400 font-black uppercase">Rank 1150</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="space-y-8">
        <div class="bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-xl">
          <h3 class="text-xl font-black text-slate-900 mb-6">Твои успехи</h3>
          <div class="space-y-4">
            <div class="flex justify-between items-center p-4 bg-slate-50 rounded-2xl">
              <span class="text-xs font-bold text-slate-400 uppercase">Ранг</span>
              <span class="font-black text-indigo-600">{{ stats.rank }}</span>
            </div>
            <div class="flex justify-between items-center p-4 bg-slate-50 rounded-2xl">
              <span class="text-xs font-bold text-slate-400 uppercase">Очки</span>
              <span class="font-black text-slate-900">{{ stats.points }}</span>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden rounded-[2.5rem] border border-slate-100 shadow-xl">
          <div class="p-6 bg-slate-900 text-white font-black text-center">
            🏆 ТОП МАСТЕРОВ
          </div>
          <div class="p-2">
            <div v-for="(player, index) in leaderboard" :key="player.id" class="flex items-center gap-4 p-4 hover:bg-slate-50 rounded-2xl transition-colors">
              <span class="w-6 text-sm font-black text-slate-300">#{{ index + 1 }}</span>
              <div class="w-10 h-10 bg-slate-100 rounded-xl flex items-center justify-center text-lg">
                {{ player.avatar }}
              </div>
              <div class="flex-1">
                <p class="text-sm font-bold text-slate-800">{{ player.name }}</p>
                <p class="text-[10px] font-black text-indigo-500 uppercase">{{ player.points }} PTS</p>
              </div>
            </div>
          </div>
          <button class="w-full py-4 text-xs font-bold text-slate-400 hover:text-indigo-600 transition-colors">Смотреть всех</button>
        </div>
      </div>

    </div>
  </div>
</template>
