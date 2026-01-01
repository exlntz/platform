<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8 bg-white p-8 rounded-2xl shadow-xl border border-gray-100">

      <div class="text-center">
        <h2 class="text-3xl font-extrabold text-gray-900 tracking-tight">
          Создать аккаунт
        </h2>
        <p class="mt-2 text-sm text-gray-500">
          Присоединяйтесь к платформе и начните решать задачи
        </p>
      </div>

      <form class="mt-8 space-y-5" @submit.prevent="handleRegister">
        <div class="space-y-4">

          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1">Имя пользователя</label>
            <input
              v-model="form.username"
              type="text"
              required
              class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all"
              placeholder="Например: alex_dev"
            />
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1">Email</label>
            <input
              v-model="form.email"
              type="email"
              required
              class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all"
              placeholder="name@example.com"
            />
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1">Пароль</label>
            <input
              v-model="form.password"
              type="password"
              required
              class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all"
              placeholder="••••••••"
            />
          </div>
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-lg shadow-indigo-200 transition-all active:scale-[0.98] disabled:opacity-70"
        >
          <span v-if="loading" class="flex items-center justify-center">
            <svg class="animate-spin h-5 w-5 mr-3 text-white" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Загрузка...
          </span>
          <span v-else>Зарегистрироваться</span>
        </button>

        <p v-if="error" class="text-center text-sm font-medium text-red-500 mt-4 p-2 bg-red-50 rounded-lg">
          {{ error }}
        </p>
      </form>

      <div class="mt-6 text-center">
        <span class="text-sm text-gray-500">Уже есть профиль? </span>
        <router-link to="/auth" class="text-sm font-bold text-indigo-600 hover:underline">
          Войти
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(false)
const error = ref('')

const form = reactive({
  username: '',
  email: '',
  password: ''
})

const handleRegister = async () => {
  loading.value = true
  error.value = ''

  try {
    // ВАЖНО: Укажите ваш базовый URL API (бэкенда)
    await axios.post('http://localhost:8000/auth/register', form)
    router.push('/auth') // Переход на страницу логина после успеха
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка при регистрации'
  } finally {
    loading.value = false
  }
}
</script>
