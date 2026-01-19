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
  <div class="register-container">
    <div class="register-card">
      <div class="register-header">
        <h2>Регистрация</h2>
        <p class="register-subtitle">Создайте аккаунт, чтобы начать решать задачи</p>
      </div>

      <form class="register-form" @submit.prevent="register">
        <div class="form-fields">
          <div class="form-group">
            <label class="form-label">Имя пользователя</label>
            <input
              v-model="regUsername"
              type="text"
              required
              placeholder="Имя пользователя"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label class="form-label">Email адрес</label>
            <input
              v-model="regEmail"
              type="email"
              required
              placeholder="example@mail.com"
              class="form-input"
            />
          </div>

          <div class="password-grid">
            <div class="form-group">
              <label class="form-label">Пароль</label>
              <input
                v-model="regPassword"
                type="password"
                required
                placeholder="Пароль"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label class="form-label">Повтор</label>
              <input
                v-model="regPasswordRepeat"
                type="password"
                required
                placeholder="Повтор пароля"
                class="form-input"
              />
            </div>
          </div>
        </div>

        <div class="submit-section">
          <button
            type="submit"
            :disabled="loading"
            class="register-btn"
            :class="{ disabled: loading }"
          >
            <span v-if="loading">Обработка...</span>
            <span v-else>Зарегистрироваться</span>
          </button>
        </div>
      </form>

      <div class="register-footer">
        <p class="footer-text">
          Уже есть профиль?
          <router-link to="/auth" class="footer-link">
            Войти
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 16px;
  background-color: #f8fafc;
  font-family: sans-serif;
}
.register-card {
  max-width: 448px;
  width: 100%;
  background-color: white;
  padding: 40px;
  border-radius: 24px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  border: 1px solid #f1f5f9;
}
.register-header {
  text-align: center;
  margin-bottom: 32px;
}
.register-header h2 {
  font-size: 30px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.025em;
  margin-bottom: 8px;
}
.register-subtitle {
  color: #64748b;
  font-weight: 500;
  font-size: 14px;
}
.register-form {
  margin-top: 32px;
}
.form-fields {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.form-group {
  display: flex;
  flex-direction: column;
}
.form-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 8px;
  margin-left: 4px;
}
.form-input {
  width: 100%;
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 16px;
  color: #0f172a;
  outline: none;
  transition: all 0.2s ease;
  background-color: white;
}
.form-input:focus {
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}
.form-input::placeholder {
  color: #cbd5e1;
}
.password-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}
@media (min-width: 640px) {
  .password-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
.submit-section {
  margin-top: 24px;
}
.register-btn {
  width: 100%;
  display: flex;
  justify-content: center;
  padding: 16px;
  border: 1px solid transparent;
  border-radius: 16px;
  font-size: 14px;
  font-weight: 700;
  color: white;
  background-color: #4f46e5;
  cursor: pointer;
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.1);
  transition: all 0.2s ease;
  text-align: center;
}
.register-btn:hover {
  background-color: #4338ca;
}
.register-btn:active {
  transform: scale(0.98);
}
.register-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.register-footer {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #f1f5f9;
  text-align: center;
}
.footer-text {
  font-size: 14px;
  color: #64748b;
}
.footer-link {
  font-weight: 700;
  color: #4f46e5;
  text-decoration: none;
  transition: color 0.2s ease;
}
.footer-link:hover {
  color: #4338ca;
}
</style>
