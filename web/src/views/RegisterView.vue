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
      loading: false,
      showPassword: false,
      showPasswordRepeat: false
    }
  },
  computed: {
    isFormValid() {
      // Проверка всех полей формы
      return (
        this.regUsername.trim() !== '' &&
        this.regEmail.trim() !== '' &&
        this.isValidEmail(this.regEmail) &&
        this.regPassword.length >= 8 &&
        /[A-Z]/.test(this.regPassword) &&
        /\d/.test(this.regPassword) &&
        this.regPassword === this.regPasswordRepeat
      );
    }
  },
  methods: {
    isValidEmail(email) {
      // Простая проверка email
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(email);
    },

    async register() {
      // Проверка перед отправкой
      if (!this.isFormValid) {
        alert('Пожалуйста, заполните все поля корректно');
        return;
      }

      if (this.regPassword !== this.regPasswordRepeat) {
        alert('Пароли не совпадают');
        return;
      }

      this.loading = true;
      try {
        const response = await axios.post('/api/auth/register', {
          username: this.regUsername,
          email: this.regEmail,
          password: this.regPassword,
          password_repeat: this.regPasswordRepeat
        });
        console.log('Register success', response.data);
        router.push('/auth');
      } catch (err) {
        alert('Ошибка регистрации: ' + (err.response?.data?.detail || err.message));
      } finally {
        this.loading = false;
      }
    },
    togglePasswordVisibility(field) {
      if (field === 'password') {
        this.showPassword = !this.showPassword;
      } else {
        this.showPasswordRepeat = !this.showPasswordRepeat;
      }
    }
  }
}
</script>

<template>
  <div class="register-container">
    <div class="register-card">
      <!-- Заголовок -->
      <div class="register-header">
        <router-link to="/auth" class="back-link">
          <span class="back-icon">←</span>
          Назад к входу
        </router-link>

        <div class="logo-container">
          <div class="logo">L</div>
          <h2 class="register-title">Регистрация в Platform</h2>
        </div>

        <p class="register-subtitle">Создайте аккаунт, чтобы начать решать задачи</p>
      </div>

      <!-- Форма -->
      <form class="register-form" @submit.prevent="register">
        <div class="form-fields">
          <div class="form-group">
            <label class="form-label">Имя пользователя</label>
            <div class="input-wrapper">
              <input
                v-model="regUsername"
                type="text"
                required
                placeholder="Введите имя пользователя"
                class="form-input"
                :disabled="loading"
              />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Email адрес</label>
            <div class="input-wrapper">
              <input
                v-model="regEmail"
                type="email"
                required
                placeholder="example@mail.com"
                class="form-input"
                :disabled="loading"
              />
            </div>
          </div>

          <div class="password-grid">
            <div class="form-group">
              <label class="form-label">Пароль</label>
              <div class="input-wrapper">
                <input
                  v-model="regPassword"
                  :type="showPassword ? 'text' : 'password'"
                  required
                  placeholder="Введите пароль"
                  class="form-input"
                  :disabled="loading"
                />
                <button
                  type="button"
                  class="password-toggle"
                  @click="togglePasswordVisibility('password')"
                  :disabled="loading"
                >
                  <span class="toggle-icon" v-if="showPassword">👁️</span>
                  <span class="toggle-icon" v-else>👁️‍🗨️</span>
                </button>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Повторите пароль</label>
              <div class="input-wrapper">
                <input
                  v-model="regPasswordRepeat"
                  :type="showPasswordRepeat ? 'text' : 'password'"
                  required
                  placeholder="Повторите пароль"
                  class="form-input"
                  :disabled="loading"
                />
                <button
                  type="button"
                  class="password-toggle"
                  @click="togglePasswordVisibility('repeat')"
                  :disabled="loading"
                >
                  <span class="toggle-icon" v-if="showPasswordRepeat">👁️</span>
                  <span class="toggle-icon" v-else>👁️‍🗨️</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="password-requirements">
          <p class="requirements-title">Требования к паролю:</p>
          <ul class="requirements-list">
            <li :class="{ 'valid': regPassword.length >= 8 }">Не менее 8 символов</li>
            <li :class="{ 'valid': /[A-Z]/.test(regPassword) }">Хотя бы одна заглавная буква</li>
            <li :class="{ 'valid': /\d/.test(regPassword) }">Хотя бы одна цифра</li>
            <li :class="{ 'valid': regPassword === regPasswordRepeat && regPassword !== '' }">Пароли совпадают</li>
          </ul>
        </div>

        <div class="submit-section">
          <button
            type="submit"
            :disabled="loading"
            class="register-btn"
            :class="{ 'disabled': !isFormValid }"
          >
            <span class="btn-text" v-if="!loading">Зарегистрироваться</span>
            <span class="loading-text" v-if="loading">Создание аккаунта...</span>
          </button>

          <!-- Сообщение о невалидной форме -->
          <div v-if="!isFormValid && !loading" class="validation-message">
            <p>Заполните все поля правильно для регистрации</p>
          </div>
        </div>
      </form>

      <!-- Футер -->
      <div class="register-footer">
        <p class="footer-text">
          Уже есть профиль?
          <router-link to="/auth" class="footer-link">
            Войти в аккаунт
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ==================== БАЗОВЫЕ СТИЛИ ==================== */

.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f8fafc 0%, #f0f9ff 100%);
  padding: 16px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  line-height: 1.5;
}

.register-card {
  width: 100%;
  max-width: 520px;
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

.register-title {
  font-size: 24px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.025em;
  margin: 0;
  line-height: 1.2;
}

.register-subtitle {
  color: #64748b;
  font-size: 14px;
  font-weight: 500;
  line-height: 1.5;
  margin-top: 0;
  margin-bottom: 28px;
}

/* Форма */
.register-form {
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

/* Сетка паролей */
.password-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

/* Требования к паролю */
.password-requirements {
  margin-top: 24px;
  padding: 16px;
  background-color: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.requirements-title {
  font-size: 14px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 12px;
}

.requirements-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}

.requirements-list li {
  font-size: 13px;
  color: #94a3b8;
  display: flex;
  align-items: center;
  gap: 8px;
}

.requirements-list li::before {
  content: "○";
  font-size: 10px;
}

.requirements-list li.valid {
  color: #059669;
}

.requirements-list li.valid::before {
  content: "✓";
  color: #059669;
  font-weight: bold;
}

/* Кнопка регистрации */
.submit-section {
  margin-top: 24px;
}

.register-btn {
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
  font-family: inherit;
  min-height: 52px;
}

.register-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 15px 30px -10px rgba(79, 70, 229, 0.4);
  background: linear-gradient(90deg, #4338ca 0%, #6d28d9 100%);
}

.register-btn:active:not(:disabled) {
  transform: translateY(0);
}

.register-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-text, .loading-text {
  display: block;
}

/* Футер */
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
  margin-left: 4px;
}

.footer-link:hover {
  color: #4338ca;
  text-decoration: underline;
}

/* Сообщение о валидации */
.validation-message {
  margin-top: 12px;
  padding: 10px;
  background-color: #fef3c7;
  border: 1px solid #fde68a;
  border-radius: 8px;
  text-align: center;
}

.validation-message p {
  font-size: 13px;
  color: #d97706;
  font-weight: 500;
  margin: 0;
}

/* ==================== АДАПТИВНЫЕ СТИЛИ ==================== */

/* Очень маленькие экраны (до 320px) */
@media (max-width: 320px) {
  .register-container {
    padding: 12px;
  }

  .register-card {
    padding: 20px 16px;
    border-radius: 16px;
  }

  .logo {
    width: 44px;
    height: 44px;
    font-size: 20px;
  }

  .register-title {
    font-size: 22px;
  }

  .register-subtitle {
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

  .toggle-icon {
    font-size: 16px;
  }

  .register-btn {
    padding: 14px;
    font-size: 15px;
    min-height: 48px;
  }

  .requirements-list {
    font-size: 12px;
  }
}


@media (min-width: 321px) and (max-width: 375px) {
  .register-card {
    padding: 22px 18px;
  }

  .logo {
    width: 46px;
    height: 46px;
    font-size: 22px;
  }

  .register-title {
    font-size: 23px;
  }
}


@media (min-width: 376px) {
  .register-card {
    padding: 24px;
  }
}


@media (min-width: 640px) {
  .register-container {
    padding: 24px;
  }

  .register-card {
    padding: 32px;
    border-radius: 24px;
    max-width: 560px;
  }

  .logo {
    width: 56px;
    height: 56px;
    font-size: 28px;
  }

  .register-title {
    font-size: 28px;
  }

  .register-subtitle {
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

  .register-btn {
    padding: 18px;
    font-size: 17px;
    min-height: 56px;
  }

  .password-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
  }

  .requirements-list {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
}


@media (min-width: 768px) {
  .register-card {
    max-width: 600px;
    padding: 40px;
  }

  .register-title {
    font-size: 32px;
  }

  .register-subtitle {
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
  .register-container {
    padding: 32px;
  }

  .register-card {
    max-width: 640px;
    padding: 48px;
  }

  .register-title {
    font-size: 36px;
  }

  .logo {
    width: 64px;
    height: 64px;
    font-size: 32px;
  }
}


@media (min-width: 1280px) {
  .register-card {
    max-width: 680px;
  }

  .register-title {
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
  .register-card {
    max-width: 720px;
    padding: 56px;
  }

  .register-title {
    font-size: 44px;
  }

  .register-subtitle {
    font-size: 18px;
  }

  .form-input {
    font-size: 17px;
    padding: 20px;
  }

  .register-btn {
    font-size: 18px;
    padding: 20px;
    min-height: 60px;
  }
}
</style>
