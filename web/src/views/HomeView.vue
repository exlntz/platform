<script>
export default {
  name: "HomeView",
  data() {
    return {
      // Проверяем наличие токена для управления отображением кнопок
      isLoggedIn: !!localStorage.getItem('user-token')
    }
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 text-gray-900 font-sans">
    <main class="max-w-7xl mx-auto px-6 py-16 lg:py-24">
      <div class="flex flex-col lg:flex-row items-center justify-between gap-12">

        <div class="lg:w-3/5 space-y-6">
          <h1 class="text-5xl lg:text-7xl font-extrabold tracking-tight text-indigo-600">
            Платформа для будущих чемпионов
          </h1>
          <p class="text-xl text-gray-600 leading-relaxed">
            Готовься к олимпиадам на новом уровне. Решай сложные задачи,
            участвуй в PvP-схватках с другими участниками и отслеживай свой прогресс
            в реальном времени. Мы собрали всё необходимое для твоей победы.
          </p>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4">
            <div class="flex items-center space-x-3">
              <span class="bg-green-100 text-green-600 p-2 rounded-full">✓</span>
              <span class="font-medium">База актуальных задач</span>
            </div>
            <div class="flex items-center space-x-3">
              <span class="bg-green-100 text-green-600 p-2 rounded-full">✓</span>
              <span class="font-medium">PvP-дуэли на скорость</span>
            </div>
          </div>
        </div>

        <div class="lg:w-1/3 w-full">
          <div class="bg-white p-8 rounded-[2rem] shadow-2xl border border-gray-100 flex flex-col items-center text-center space-y-6">
            <h2 class="text-3xl font-black text-slate-800 tracking-tight">Начни путь к успеху</h2>
            <p class="text-slate-500 font-medium leading-relaxed">
              Создай аккаунт, чтобы сохранять свои решения и подниматься в рейтинге.
            </p>

            <div v-if="!isLoggedIn" class="w-full flex flex-col gap-4">
              <router-link
                to="/auth/register"
                class="w-full py-4 bg-[#1fb141] hover:bg-[#199435] text-white font-black rounded-2xl shadow-xl shadow-green-100 transition-all transform hover:scale-[1.03] text-center"
              >
                Зарегистрироваться
              </router-link>

              <router-link
                to="/auth"
                class="w-full py-4 bg-white border-2 border-indigo-600 text-indigo-600 font-black rounded-2xl transition-all hover:bg-indigo-50 transform hover:scale-[1.03] text-center"
              >
                Войти
              </router-link>
            </div>

            <router-link
              v-else
              to="/profile"
              class="w-full py-4 bg-[#1fb141] hover:bg-[#199435] text-white font-black rounded-2xl shadow-xl shadow-green-100 transition-all transform hover:scale-[1.03] text-center"
            >
              Перейти в профиль
            </router-link>

            <p class="text-xs text-gray-400 font-medium">
              Версия платформы 1.0.0
            </p>
          </div>
        </div>

      </div>
    </main>
  </div>
</template>

<style scoped>
/* Дополнительные стили не требуются благодаря Tailwind */
</style>
