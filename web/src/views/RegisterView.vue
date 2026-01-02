<script>
import axios from 'axios'
import router from '../router/index.js'

export default {
  name: "RegisterView",
  data() {
    return {
      regUsername: '',
      regEmail: '',
      regPassword: '',
      regPasswordRepeat: '',
      loading: false // Состояние для кнопки
    }
  },
  methods: {
    async register() {
      if (this.regPassword === this.regPasswordRepeat) {
        this.loading = true;
        try {
          // Отправка данных на бэкенд согласно вашей схеме
          const response = await axios.post('http://127.0.0.1:8000/auth/register', {
            username: this.regUsername,
            email: this.regEmail,
            password: this.regPassword,
            password_repeat: this.regPasswordRepeat
          });
          console.log('Register success', response.data);
          router.push('/auth');
        } catch (err) {
          // Обработка ошибок валидации или занятого логина
          alert('Ошибка регистрации: ' + (err.response?.data?.detail || err.message));
        } finally {
          this.loading = false;
        }
      } else {
        alert('Пароли не совпадают');
      }
    }
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8 bg-white p-10 rounded-3xl shadow-xl border border-slate-100">

      <div class="text-center">
        <h2 class="text-3xl font-extrabold text-slate-900 tracking-tight">Регистрация</h2>
        <p class="mt-2 text-sm text-slate-500 font-medium">Создайте аккаунт, чтобы начать решать задачи</p>
      </div>

      <form class="mt-8 space-y-6" @submit.prevent="register">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1 ml-1">Имя пользователя</label>
            <input
              v-model="regUsername"
              type="text"
              required
              placeholder="ivan_dev"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all placeholder:text-slate-300"
            />
          </div>

          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1 ml-1">Email адрес</label>
            <input
              v-model="regEmail"
              type="email"
              required
              placeholder="example@mail.com"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all placeholder:text-slate-300"
            />
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-1 ml-1">Пароль</label>
              <input
                v-model="regPassword"
                type="password"
                required
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all"
              />
            </div>
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-1 ml-1">Повтор</label>
              <input
                v-model="regPasswordRepeat"
                type="password"
                required
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all"
              />
            </div>
          </div>
        </div>

        <div>
          <button
            type="submit"
            :disabled="loading"
            class="w-full flex justify-center py-4 px-4 border border-transparent text-sm font-bold rounded-2xl text-white bg-indigo-600 hover:bg-indigo-700 shadow-lg shadow-indigo-200 transition-all active:scale-[0.98] disabled:opacity-50"
          >
            <span v-if="loading">Обработка...</span>
            <span v-else>Зарегистрироваться</span>
          </button>
        </div>
      </form>

      <div class="mt-6 text-center border-t border-slate-50 pt-6">
        <p class="text-sm text-slate-600">
          Уже есть профиль?
          <router-link to="/auth" class="font-bold text-indigo-600 hover:text-indigo-500 transition-colors">
            Войти
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Специфические стили больше не требуются, всё решается классами Tailwind */
</style>
