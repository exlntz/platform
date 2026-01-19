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
  <div class="home-container">
    <main class="home-main">
      <div class="home-content">
        <div class="hero-section">
          <h1 class="hero-title">Платформа для будущих чемпионов</h1>
          <p class="hero-description">
            Готовься к олимпиадам на новом уровне. Решай сложные задачи,
            участвуй в PvP-схватках с другими участниками и отслеживай свой прогресс
            в реальном времени. Мы собрали всё необходимое для твоей победы.
          </p>

          <div class="features-grid">
            <div class="feature-item">
              <span class="feature-icon">✓</span>
              <span class="feature-text">База актуальных задач</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">✓</span>
              <span class="feature-text">PvP-дуэли на скорость</span>
            </div>
          </div>
        </div>

        <div class="cta-section">
          <div class="cta-card">
            <h2 class="cta-title">Начни путь к успеху</h2>
            <p class="cta-description">
              Создай аккаунт, чтобы сохранять свои решения и подниматься в рейтинге.
            </p>

            <div v-if="!isLoggedIn" class="auth-buttons">
              <router-link
                to="/auth/register"
                class="btn-register"
              >
                Зарегистрироваться
              </router-link>

              <router-link
                to="/auth"
                class="btn-login"
              >
                Войти
              </router-link>
            </div>

            <router-link
              v-else
              to="/profile"
              class="btn-profile"
            >
              Перейти в профиль
            </router-link>

            <p class="version-text">
              Версия платформы 1.0.0
            </p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.home-container {
  min-height: 100vh;
  background-color: #f9fafb;
  color: #111827;
  font-family: sans-serif;
}
.home-main {
  max-width: 1280px;
  margin: 0 auto;
  padding: 64px 24px;
}
@media (min-width: 1024px) {
  .home-main {
    padding: 96px 24px;
  }
}
.home-content {
  display: flex;
  flex-direction: column;
  gap: 48px;
}
@media (min-width: 1024px) {
  .home-content {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    gap: 48px;
  }
}
.hero-section {
  flex: 1;
}
@media (min-width: 1024px) {
  .hero-section {
    width: 60%;
  }
}
.hero-title {
  font-size: 48px;
  font-weight: 800;
  letter-spacing: -0.025em;
  color: #4f46e5;
  margin-bottom: 24px;
}
@media (min-width: 1024px) {
  .hero-title {
    font-size: 72px;
  }
}
.hero-description {
  font-size: 20px;
  color: #4b5563;
  line-height: 1.75;
  margin-bottom: 24px;
}
.features-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 16px;
  padding-top: 16px;
}
@media (min-width: 768px) {
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
}
.feature-icon {
  background-color: #d1fae5;
  color: #059669;
  padding: 8px;
  border-radius: 50%;
}
.feature-text {
  font-weight: 500;
  color: #374151;
}
.cta-section {
  flex: 1;
}
@media (min-width: 1024px) {
  .cta-section {
    width: 33.333%;
  }
}
.cta-card {
  background-color: white;
  padding: 32px;
  border-radius: 32px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  border: 1px solid #f3f4f6;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 24px;
}
.cta-title {
  font-size: 30px;
  font-weight: 900;
  color: #1f2937;
  letter-spacing: -0.025em;
}
.cta-description {
  color: #6b7280;
  font-weight: 500;
  line-height: 1.75;
}
.auth-buttons {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.btn-register,
.btn-login,
.btn-profile {
  width: 100%;
  padding: 16px;
  font-weight: 900;
  border-radius: 16px;
  text-align: center;
  text-decoration: none;
  transition: all 0.2s ease;
  display: inline-block;
}
.btn-register {
  background-color: #22c55e;
  color: white;
  box-shadow: 0 10px 15px -3px rgba(34, 197, 94, 0.1);
}
.btn-register:hover {
  background-color: #16a34a;
  transform: scale(1.03);
}
.btn-login {
  background-color: white;
  border: 2px solid #4f46e5;
  color: #4f46e5;
}
.btn-login:hover {
  background-color: #e0e7ff;
  transform: scale(1.03);
}
.btn-profile {
  background-color: #22c55e;
  color: white;
  box-shadow: 0 10px 15px -3px rgba(34, 197, 94, 0.1);
}
.btn-profile:hover {
  background-color: #16a34a;
  transform: scale(1.03);
}
.version-text {
  font-size: 12px;
  color: #9ca3af;
  font-weight: 500;
}
</style>
