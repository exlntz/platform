<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goRegister = () => router.push('/register')
const goTasks = () => router.push('/tasks')
</script>

<template>
  <div class="min-h-screen bg-white font-sans overflow-x-hidden">

    <section class="relative pt-10 pb-16 lg:pt-16 lg:min-h-[80vh] flex items-center overflow-hidden">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 w-full">
        <div class="grid lg:grid-cols-2 gap-12 items-center">

          <div class="space-y-6 animate-fade-in-up">
            <div class="inline-flex items-center space-x-2 bg-indigo-50 rounded-full px-4 py-1.5 border border-indigo-100">
              <span class="flex h-2 w-2 rounded-full bg-indigo-600"></span>
              <span class="text-xs font-bold text-indigo-700 uppercase tracking-wide">Платформа v1.0</span>
            </div>

            <h1 class="text-4xl lg:text-6xl font-black text-slate-900 tracking-tight leading-[1.1]">
              Готовься к победам <br>
              <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600">
                на новом уровне
              </span>
            </h1>

            <p class="text-lg text-slate-500 max-w-xl leading-relaxed font-medium">
              Единое пространство для подготовки к олимпиадам. Решай сложные задачи, сражайся в PvP-дуэлях и отслеживай свой прогресс в реальном времени.
            </p>

            <div class="flex flex-col sm:flex-row gap-4 pt-2">
              <button
                @click="goRegister"
                class="px-8 py-4 bg-indigo-600 text-white rounded-2xl font-bold text-lg shadow-xl shadow-indigo-200 hover:bg-indigo-700 hover:scale-[1.02] transition-all active:scale-95"
              >
                Начать бесплатно
              </button>
              <button
                @click="goTasks"
                class="px-8 py-4 bg-white text-slate-700 border-2 border-slate-100 rounded-2xl font-bold text-lg hover:border-indigo-100 hover:text-indigo-600 hover:bg-indigo-50 transition-all"
              >
                Посмотреть задачи
              </button>
            </div>

            <p class="text-xs text-slate-400 font-medium">
              * Не требует установки. Работает в браузере.
            </p>
          </div>

          <div class="relative hidden lg:block animate-fade-in">
            <div class="absolute top-0 right-0 -mr-20 -mt-20 w-80 h-80 bg-indigo-100 rounded-full blur-3xl opacity-50 mix-blend-multiply animate-blob"></div>
            <div class="absolute bottom-0 left-10 w-80 h-80 bg-violet-100 rounded-full blur-3xl opacity-50 mix-blend-multiply animate-blob animation-delay-2000"></div>

            <div class="relative bg-white/60 backdrop-blur-xl border border-white/50 rounded-[2.5rem] p-6 shadow-2xl transform rotate-[-2deg] hover:rotate-0 transition-transform duration-500">
              <div class="flex justify-between items-center mb-6">
                <div class="flex gap-2">
                  <div class="w-2.5 h-2.5 rounded-full bg-red-400"></div>
                  <div class="w-2.5 h-2.5 rounded-full bg-amber-400"></div>
                  <div class="w-2.5 h-2.5 rounded-full bg-green-400"></div>
                </div>
                <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">PvP Arena</div>
              </div>

              <div class="space-y-4">
                <div class="flex items-center justify-between bg-white p-4 rounded-2xl shadow-sm border border-slate-100">
                  <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center text-lg">👨‍💻</div>
                    <div>
                      <div class="font-bold text-slate-900 text-sm">Ты</div>
                      <div class="text-xs text-slate-400">Rating: 1200</div>
                    </div>
                  </div>
                  <span class="font-black text-indigo-600 text-lg">VS</span>
                  <div class="flex items-center gap-3 text-right">
                    <div>
                      <div class="font-bold text-slate-900 text-sm">Оппонент</div>
                      <div class="text-xs text-slate-400">Rating: 1180</div>
                    </div>
                    <div class="w-10 h-10 rounded-full bg-rose-100 flex items-center justify-center text-lg">🥷</div>
                  </div>
                </div>

                <div class="space-y-1">
                    <div class="flex justify-between text-[10px] font-bold text-slate-400 uppercase">
                        <span>Прогресс решения</span>
                        <span>80%</span>
                    </div>
                    <div class="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                        <div class="h-full bg-gradient-to-r from-indigo-500 to-violet-500 w-4/5"></div>
                    </div>
                </div>

                <div class="flex justify-between text-xs font-bold text-slate-400 pt-2 border-t border-slate-50">
                  <span>Задача #45: Динамика</span>
                  <span class="text-indigo-600">04:59</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <div class="border-y border-slate-100 bg-slate-50/50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          <div v-for="(stat, index) in stats" :key="index">
            <div class="text-2xl md:text-4xl font-black text-slate-900 mb-1">{{ stat.value }}</div>
            <div class="text-xs md:text-sm font-bold text-slate-500 uppercase tracking-wide">{{ stat.label }}</div>
          </div>
        </div>
      </div>
    </div>

    <section class="py-20 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center max-w-3xl mx-auto mb-16">
          <h2 class="text-3xl font-black text-slate-900 mb-4">Всё для эффективной учебы</h2>
          <p class="text-slate-500 text-lg">Мы убрали лишнее и оставили только то, что реально помогает выигрывать олимпиады.</p>
        </div>

        <div class="grid md:grid-cols-3 gap-8">
          <div class="group p-8 rounded-[2rem] bg-slate-50 border border-slate-100 hover:bg-white hover:shadow-xl hover:shadow-indigo-100 hover:-translate-y-2 transition-all duration-300">
            <div class="w-14 h-14 bg-blue-100 text-blue-600 rounded-2xl flex items-center justify-center text-2xl mb-6 group-hover:scale-110 transition-transform">📚</div>
            <h3 class="text-xl font-bold text-slate-900 mb-3">Банк задач</h3>
            <p class="text-slate-500 leading-relaxed">Сотни задач по алгоритмам и математике. Фильтрация по темам и автоматическая проверка.</p>
          </div>

          <div class="group p-8 rounded-[2rem] bg-slate-50 border border-slate-100 hover:bg-white hover:shadow-xl hover:shadow-indigo-100 hover:-translate-y-2 transition-all duration-300">
            <div class="w-14 h-14 bg-violet-100 text-violet-600 rounded-2xl flex items-center justify-center text-2xl mb-6 group-hover:scale-110 transition-transform">⚔️</div>
            <h3 class="text-xl font-bold text-slate-900 mb-3">PvP Дуэли</h3>
            <p class="text-slate-500 leading-relaxed">Вызови друга или случайного соперника. Решай на скорость, повышай рейтинг ELO и становись лидером.</p>
          </div>

          <div class="group p-8 rounded-[2rem] bg-slate-50 border border-slate-100 hover:bg-white hover:shadow-xl hover:shadow-indigo-100 hover:-translate-y-2 transition-all duration-300">
            <div class="w-14 h-14 bg-emerald-100 text-emerald-600 rounded-2xl flex items-center justify-center text-2xl mb-6 group-hover:scale-110 transition-transform">📈</div>
            <h3 class="text-xl font-bold text-slate-900 mb-3">Аналитика</h3>
            <p class="text-slate-500 leading-relaxed">Подробная статистика прогресса. Мы покажем твои слабые места и подскажем, какие темы подтянуть.</p>
          </div>
        </div>
      </div>
    </section>

  </div>
</template>

<script>
export default {
  data() {
    return {
      stats: [
        { value: '500+', label: 'Задач в базе' },
        { value: '1.2k', label: 'Пользователей' },
        { value: '24/7', label: 'Аптайм' },
        { value: 'Free', label: 'Доступ' }
      ]
    }
  }
}
</script>

<style scoped>
.animate-fade-in-up { animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1); }
.animate-fade-in { animation: fadeIn 1.5s ease-out; }
.animate-blob { animation: blob 7s infinite; }
.animation-delay-2000 { animation-delay: 2s; }

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes blob {
  0% { transform: translate(0px, 0px) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
  100% { transform: translate(0px, 0px) scale(1); }
}
</style>
