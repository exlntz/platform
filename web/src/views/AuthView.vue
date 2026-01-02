<script>
import axios from "axios";

export default {
  name: "AuthView",
  data() {
    return {
      loginUsername: '',
      loginPassword: '',
      loading: false
    }
  },
  methods: {
    async login() {
      this.loading = true;
      try {
        // Логика передачи параметров формы для FastAPI
        const params = new URLSearchParams();
        params.append('username', this.loginUsername);
        params.append('password', this.loginPassword);

        const response = await axios.post('http://127.0.0.1:8000/auth/login', params);

        console.log('Log in success', response.data);
        const token = response.data.access_token;
        localStorage.setItem('user-token', token);

        // Перенаправление в профиль после успешного входа
        this.$router.push('/profile');
      } catch(err) {
        alert("Ошибка авторизации: " + (err.response?.data?.detail || err.message));
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-50 p-4">

    <div class="max-w-md w-full bg-white rounded-[2rem] shadow-2xl border border-slate-100 p-10 space-y-8">

      <div class="text-center">
        <h1 class="text-4xl font-black text-slate-900 tracking-tight">Вход</h1>
        <p class="mt-3 text-slate-500 font-medium text-sm">Введите свои данные, чтобы продолжить обучение</p>
      </div>

      <form @submit.prevent="login" class="space-y-6">
        <div class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-slate-700 uppercase tracking-widest mb-2 ml-1">Имя пользователя</label>
            <input
              type="text"
              v-model="loginUsername"
              required
              placeholder="vash_login"
              class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-5 py-4 focus:ring-2 focus:ring-indigo-500 focus:bg-white outline-none transition-all placeholder:text-slate-300"
            >
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-700 uppercase tracking-widest mb-2 ml-1">Пароль</label>
            <input
              type="password"
              v-model="loginPassword"
              required
              placeholder="••••••••"
              class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-5 py-4 focus:ring-2 focus:ring-indigo-500 focus:bg-white outline-none transition-all"
            >
          </div>
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full py-5 bg-indigo-600 hover:bg-indigo-700 text-white font-black rounded-2xl shadow-xl shadow-indigo-100 transition-all active:scale-[0.98] disabled:opacity-50"
        >
          {{ loading ? 'Вход в систему...' : 'Войти' }}
        </button>
      </form>

      <div class="pt-6 border-t border-slate-50 text-center">
        <p class="text-sm text-slate-500 font-medium">
          Нет аккаунта?
          <router-link to="/auth/register" class="text-indigo-600 font-bold hover:text-indigo-500 transition-colors">
            Зарегистрироваться
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Все стили применяются через Tailwind классы в шаблоне */
</style>
