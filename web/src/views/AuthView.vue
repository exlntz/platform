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
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h1 class="auth-title">Вход</h1>
        <p class="auth-subtitle">Введите свои данные, чтобы продолжить обучение</p>
      </div>

      <form @submit.prevent="login" class="auth-form">
        <div class="form-fields">
          <div class="form-group">
            <label class="form-label">Имя пользователя</label>
            <input
              type="text"
              v-model="loginUsername"
              required
              placeholder="Логин"
              class="form-input"
            >
          </div>

          <div class="form-group">
            <label class="form-label">Пароль</label>
            <input
              type="password"
              v-model="loginPassword"
              required
              placeholder="Пароль"
              class="form-input"
            >
          </div>
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="submit-btn"
          :class="{ disabled: loading }"
        >
          {{ loading ? 'Вход в систему...' : 'Войти' }}
        </button>
      </form>

      <div class="auth-footer">
        <p class="footer-text">
          Нет аккаунта?
          <router-link to="/auth/register" class="footer-link">
            Зарегистрироваться
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8fafc;
  padding: 16px;
  font-family: sans-serif;
}
.auth-card {
  max-width: 448px;
  width: 100%;
  background-color: white;
  border-radius: 32px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  border: 1px solid #f1f5f9;
  padding: 40px;
}
.auth-header {
  text-align: center;
}
.auth-title {
  font-size: 36px;
  font-weight: 900;
  color: #0f172a;
  letter-spacing: -0.025em;
  margin-bottom: 12px;
}
.auth-subtitle {
  color: #64748b;
  font-weight: 500;
  font-size: 14px;
  margin-top: 12px;
}
.auth-form {
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
  font-size: 12px;
  font-weight: 700;
  color: #334155;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 8px;
  margin-left: 4px;
}
.form-input {
  width: 100%;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 16px 20px;
  font-size: 16px;
  color: #0f172a;
  outline: none;
  transition: all 0.2s ease;
}
.form-input:focus {
  background-color: white;
  border-color: #4f46e5;
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.1);
}
.form-input::placeholder {
  color: #cbd5e1;
}
.submit-btn {
  width: 100%;
  padding: 20px;
  background-color: #4f46e5;
  color: white;
  font-weight: 900;
  border-radius: 16px;
  border: none;
  cursor: pointer;
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.1);
  transition: all 0.2s ease;
  margin-top: 24px;
  font-size: 16px;
}
.submit-btn:hover {
  background-color: #4338ca;
}
.submit-btn:active {
  transform: scale(0.98);
}
.submit-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.auth-footer {
  padding-top: 24px;
  margin-top: 24px;
  border-top: 1px solid #f1f5f9;
  text-align: center;
}
.footer-text {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
}
.footer-link {
  color: #4f46e5;
  font-weight: 700;
  text-decoration: none;
  transition: color 0.2s ease;
}
.footer-link:hover {
  color: #4338ca;
}
</style>
