<script>
export default {
  name: "ProfileView",
  data() {
    return {
      // Моковые данные (позже заменишь на данные с бекенда)
      user: {
        username: "Champion_2026",
        tasksDone: 124,
        elo: 1450,
        winRate: "68%",
        wins: 84
      }
    }
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 py-12 px-6">
    <div class="max-w-5xl mx-auto space-y-8">

      <div class="bg-white rounded-[2.5rem] p-8 md:p-12 shadow-2xl shadow-slate-200/50 border border-slate-100 flex flex-col md:flex-row items-center gap-8">
        <div class="relative">
          <div class="w-32 h-32 md:w-40 md:h-40 bg-indigo-600 rounded-[2.5rem] flex items-center justify-center text-white text-5xl font-black shadow-2xl shadow-indigo-200 rotate-3 group-hover:rotate-0 transition-transform">
            {{ user.username.charAt(0).toUpperCase() }}
          </div>
          <div class="absolute -bottom-2 -right-2 bg-green-500 border-4 border-white w-8 h-8 rounded-full shadow-lg"></div>
        </div>

        <div class="text-center md:text-left space-y-2">
          <div class="inline-block px-4 py-1 bg-indigo-50 text-indigo-600 text-[10px] font-black uppercase tracking-widest rounded-full mb-2">
            PRO ACCOUNT
          </div>
          <h1 class="text-4xl md:text-5xl font-black text-slate-900 tracking-tight">
            {{ user.username }}
          </h1>
          <p class="text-slate-400 font-medium">На платформе с января 2026 • Уровень: Гроссмейстер</p>
        </div>

        <button class="md:ml-auto p-4 bg-slate-50 hover:bg-slate-100 rounded-2xl transition-all">
          <span class="text-xl">⚙️</span>
        </button>
      </div>

      <div class="grid grid-cols-2 lg:grid-cols-4 gap-6">
        <div class="bg-white p-6 rounded-[2rem] border border-slate-100 shadow-xl flex flex-col items-center text-center space-y-2">
          <span class="text-2xl mb-2">🚀</span>
          <p class="text-xs font-bold text-slate-400 uppercase tracking-widest">Tasks Done</p>
          <p class="text-3xl font-black text-slate-900">{{ user.tasksDone }}</p>
        </div>

        <div class="bg-white p-6 rounded-[2rem] border border-slate-100 shadow-xl flex flex-col items-center text-center space-y-2">
          <span class="text-2xl mb-2">🏆</span>
          <p class="text-xs font-bold text-slate-400 uppercase tracking-widest">Elo Rating</p>
          <p class="text-3xl font-black text-indigo-600">{{ user.elo }}</p>
        </div>

        <div class="bg-white p-6 rounded-[2rem] border border-slate-100 shadow-xl flex flex-col items-center text-center space-y-2">
          <span class="text-2xl mb-2">📈</span>
          <p class="text-xs font-bold text-slate-400 uppercase tracking-widest">Win Rate</p>
          <p class="text-3xl font-black text-green-500">{{ user.winRate }}</p>
        </div>

        <div class="bg-white p-6 rounded-[2rem] border border-slate-100 shadow-xl flex flex-col items-center text-center space-y-2">
          <span class="text-2xl mb-2">🎯</span>
          <p class="text-xs font-bold text-slate-400 uppercase tracking-widest">Total Wins</p>
          <p class="text-3xl font-black text-slate-900">{{ user.wins }}</p>
        </div>
      </div>

      <div class="bg-white p-8 md:p-10 rounded-[2.5rem] border border-slate-100 shadow-xl">
        <div class="flex items-center justify-between mb-8">
          <h2 class="text-2xl font-black text-slate-900 tracking-tight">Активность</h2>
          <select class="bg-slate-50 border-none rounded-xl px-4 py-2 text-xs font-bold text-slate-500 outline-none">
            <option>За последний месяц</option>
            <option>За год</option>
          </select>
        </div>

        <div class="h-64 bg-slate-50 rounded-[2rem] border-2 border-dashed border-slate-200 flex flex-col items-center justify-center text-slate-400">
          <div class="text-4xl mb-2">📊</div>
          <p class="text-sm font-bold uppercase tracking-widest">График прогресса будет здесь</p>
          <p class="text-xs font-medium opacity-60">Подключите библиотеку Chart.js для визуализации</p>
        </div>
      </div>

    </div>
  </div>
</template>
