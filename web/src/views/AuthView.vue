<script>
import api from '@/api/axios' // Наш настроенный инстанс

export default {
  name: 'AuthView',
  data() {
    return {
      loginUsername: '',
      loginPassword: '',
      loading: false,
      showPassword: false,
    }
  },
  methods: {
    async login() {
      this.loading = true
      try {
        const params = new URLSearchParams()
        params.append('username', this.loginUsername)
        params.append('password', this.loginPassword)

        const response = await api.post('/auth/login', params)
        const token = response.data.access_token
        localStorage.setItem('user-token', token)
        localStorage.setItem('refresh-token', response.data.refresh_token)

        this.$router.push('/profile')
      } catch (err) {
        console.error('Ошибка входа:', err);
      } finally {
        this.loading = false
      }
    },
    togglePasswordVisibility() {
      this.showPassword = !this.showPassword
    },
  },
}
</script>

<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <router-link to="/" class="back-link">
          <span class="back-icon">←</span>
          На главную
        </router-link>

        <div class="logo-container">
          <div class="logo">L</div>
          <h1 class="auth-title">Вход в Platform</h1>
        </div>

        <p class="auth-subtitle">Введите свои данные, чтобы продолжить обучение</p>
      </div>

      <form @submit.prevent="login" class="auth-form">
        <div class="form-fields">
          <div class="form-group">
            <label class="form-label">Имя пользователя</label>
            <div class="input-wrapper">
              <input
                type="text"
                v-model="loginUsername"
                required
                placeholder="Введите логин"
                class="form-input"
                :disabled="loading"
              />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Пароль</label>
            <div class="input-wrapper">
              <input
                :type="showPassword ? 'text' : 'password'"
                v-model="loginPassword"
                required
                placeholder="Введите пароль"
                class="form-input"
                :disabled="loading"
              />
              <button
                type="button"
                class="password-toggle"
                @click="togglePasswordVisibility"
                :disabled="loading"
              >
                <span class="toggle-icon" v-if="showPassword">👁️</span>
                <span class="toggle-icon" v-else>👁️‍🗨️</span>
              </button>
            </div>
          </div>
        </div>

        <button type="submit" :disabled="loading" class="submit-btn">
          <span class="btn-text" v-if="!loading">Войти</span>
          <span class="loading-text" v-if="loading">Вход в систему...</span>
        </button>
      </form>

      <div class="divider">
        <span class="divider-text">или</span>
      </div>

      <div class="alternative-actions">
        <p class="alternative-text">Нет аккаунта?</p>
        <router-link to="/auth/register" class="alternative-btn"> Создать аккаунт </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ==================== БАЗОВЫЕ СТИЛИ ==================== */

.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f8fafc 0%, #f0f9ff 100%);
  padding: 16px;
  font-family:
    -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  line-height: 1.5;
}

.auth-card {
  width: 100%;
  max-width: 480px;
  background-color: white;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  border: 1px solid #f1f5f9;
  padding: 24px;
}

/* Заголовок */
.back-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #64748b;
  text-decoration: none;
  font-weight: 500;
  margin-bottom: 20px;
  padding: 8px 0;
  transition: color 0.2s ease;
}

.back-link:hover {
  color: #4f46e5;
}

.back-icon {
  font-size: 18px;
  font-weight: bold;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.logo {
  width: 50px;
  height: 50px;
  background-color: #4f46e5;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 900;
  font-size: 24px;
  flex-shrink: 0;
}

.auth-title {
  font-size: 24px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.025em;
  margin: 0;
  line-height: 1.2;
}

.auth-subtitle {
  color: #64748b;
  font-size: 14px;
  font-weight: 500;
  line-height: 1.5;
  margin-top: 0;
  margin-bottom: 28px;
}

/* Форма */
.auth-form {
  margin: 28px 0;
}

.form-fields {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-label {
  font-size: 13px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 8px;
  letter-spacing: 0.02em;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.form-input {
  width: 100%;
  background-color: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 14px;
  font-size: 15px;
  color: #0f172a;
  outline: none;
  transition: all 0.2s ease;
  font-family: inherit;
  line-height: 1.5;
}

.form-input:focus {
  background-color: white;
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.form-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background-color: #f1f5f9;
}

.form-input::placeholder {
  color: #94a3b8;
}

.password-toggle {
  position: absolute;
  right: 14px;
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s ease;
  font-size: 16px;
  line-height: 1;
}

.password-toggle:hover:not(:disabled) {
  color: #4f46e5;
}

.password-toggle:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.toggle-icon {
  display: inline-block;
  font-size: 18px;
}

.submit-btn {
  width: 100%;
  padding: 16px;
  background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
  color: white;
  font-weight: 700;
  font-size: 16px;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  box-shadow: 0 8px 20px -6px rgba(79, 70, 229, 0.3);
  transition: all 0.2s ease;
  margin-top: 28px;
  font-family: inherit;
  min-height: 52px;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 15px 30px -10px rgba(79, 70, 229, 0.4);
  background: linear-gradient(90deg, #4338ca 0%, #6d28d9 100%);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
  background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
}

.btn-text,
.loading-text {
  display: block;
}

.form-helper {
  text-align: center;
  margin-top: 18px;
}

/* Разделитель */
.divider {
  display: flex;
  align-items: center;
  margin: 28px 0;
  color: #94a3b8;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background-color: #e2e8f0;
}

.divider-text {
  padding: 0 14px;
  font-size: 13px;
  font-weight: 500;
}

/* Альтернативные действия */
.alternative-actions {
  text-align: center;
}

.alternative-text {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 16px;
}

.alternative-btn {
  display: inline-block;
  width: 100%;
  padding: 16px;
  background-color: white;
  color: #4f46e5;
  font-weight: 700;
  font-size: 15px;
  border-radius: 12px;
  border: 2px solid #4f46e5;
  text-decoration: none;
  transition: all 0.2s ease;
  text-align: center;
}

.alternative-btn:hover {
  background-color: #f8fafc;
  transform: translateY(-2px);
}

/* Футер */
.auth-footer {
  padding-top: 28px;
  margin-top: 28px;
  border-top: 1px solid #f1f5f9;
  text-align: center;
}

.footer-text {
  font-size: 12px;
  color: #94a3b8;
  line-height: 1.5;
}

/* ==================== ТЁМНАЯ ТЕМА ==================== */

:root.dark .auth-container {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

:root.dark .auth-card {
  background-color: #1e293b;
  border-color: #334155;
  color: #f1f5f9;
}

:root.dark .auth-title {
  color: #f8fafc;
}

:root.dark .auth-subtitle {
  color: #cbd5e1;
}

:root.dark .back-link {
  color: #94a3b8;
}

:root.dark .back-link:hover {
  color: #60a5fa;
}

:root.dark .logo {
  background-color: #3b82f6;
}

:root.dark .form-input {
  background-color: #334155;
  border-color: #475569;
  color: #f1f5f9;
}

:root.dark .form-input:focus {
  background-color: #334155;
  border-color: #3b82f6;
}

:root.dark .form-input::placeholder {
  color: #64748b;
}

:root.dark .form-label {
  color: #cbd5e1;
}

:root.dark .password-toggle {
  color: #94a3b8;
}

:root.dark .password-toggle:hover:not(:disabled) {
  color: #60a5fa;
}

:root.dark .submit-btn {
  background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
}

:root.dark .submit-btn:hover:not(:disabled) {
  background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%);
}

:root.dark .divider::before,
:root.dark .divider::after {
  background-color: #475569;
}

:root.dark .alternative-text {
  color: #94a3b8;
}

:root.dark .alternative-btn {
  background-color: #334155;
  color: #60a5fa;
  border-color: #475569;
}

:root.dark .alternative-btn:hover {
  background-color: #475569;
}

:root.dark .auth-footer {
  border-top-color: #334155;
}

:root.dark .footer-text {
  color: #64748b;
}

/* ==================== АДАПТИВНЫЕ СТИЛИ ==================== */

@media (max-width: 320px) {
  .auth-container {
    padding: 12px;
  }

  .auth-card {
    padding: 20px 16px;
    border-radius: 16px;
  }

  .logo {
    width: 44px;
    height: 44px;
    font-size: 20px;
  }

  .auth-title {
    font-size: 22px;
  }

  .auth-subtitle {
    font-size: 13px;
  }

  .form-input {
    padding: 12px;
    font-size: 14px;
  }

  .password-toggle {
    right: 12px;
    padding: 4px;
  }

  .submit-btn {
    padding: 14px;
    font-size: 15px;
    min-height: 48px;
  }
}

@media (min-width: 321px) and (max-width: 375px) {
  .auth-card {
    padding: 22px 18px;
  }

  .logo {
    width: 46px;
    height: 46px;
    font-size: 22px;
  }

  .auth-title {
    font-size: 23px;
  }
}

@media (min-width: 376px) {
  .auth-card {
    padding: 24px;
  }
}

@media (min-width: 640px) {
  .auth-container {
    padding: 24px;
  }

  .auth-card {
    padding: 32px;
    border-radius: 24px;
    max-width: 520px;
  }

  .logo {
    width: 56px;
    height: 56px;
    font-size: 28px;
  }

  .auth-title {
    font-size: 28px;
  }

  .auth-subtitle {
    font-size: 15px;
  }

  .form-input {
    padding: 16px;
    font-size: 16px;
  }

  .password-toggle {
    font-size: 18px;
    padding: 8px;
  }

  .toggle-icon {
    font-size: 20px;
  }

  .submit-btn {
    padding: 18px;
    font-size: 17px;
    min-height: 56px;
  }
}

@media (min-width: 768px) {
  .auth-card {
    max-width: 560px;
    padding: 40px;
  }

  .auth-title {
    font-size: 32px;
  }

  .auth-subtitle {
    font-size: 16px;
  }

  .back-link {
    font-size: 15px;
  }

  .back-icon {
    font-size: 20px;
  }
}

@media (min-width: 1024px) {
  .auth-container {
    padding: 32px;
  }

  .auth-card {
    max-width: 600px;
    padding: 48px;
  }

  .auth-title {
    font-size: 36px;
  }

  .logo {
    width: 64px;
    height: 64px;
    font-size: 32px;
  }
}

@media (min-width: 1280px) {
  .auth-card {
    max-width: 640px;
  }

  .auth-title {
    font-size: 40px;
  }

  .form-fields {
    gap: 24px;
  }

  .form-input {
    padding: 18px;
  }
}

@media (min-width: 1536px) {
  .auth-card {
    max-width: 680px;
    padding: 56px;
  }

  .auth-title {
    font-size: 44px;
  }

  .auth-subtitle {
    font-size: 18px;
  }

  .form-input {
    font-size: 17px;
    padding: 20px;
  }

  .submit-btn {
    font-size: 18px;
    padding: 20px;
    min-height: 60px;
  }
}
</style>
