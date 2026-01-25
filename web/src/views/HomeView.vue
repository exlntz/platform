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
        <!-- Основной контент -->
        <div class="hero-section">
          <h1 class="hero-title">Платформа для будущих чемпионов</h1>
          
          <p class="hero-description">
            Готовься к олимпиадам на новом уровне. Решай сложные задачи,
            участвуй в PvP-схватках с другими участниками и отслеживай свой прогресс
            в реальном времени. Мы собрали всё необходимое для твоей победы.
          </p>

          <div class="features-grid">
            <div class="feature-item">
              <div class="feature-icon-wrapper">
                <span class="feature-icon">✓</span>
              </div>
              <span class="feature-text">База актуальных задач</span>
            </div>
            <div class="feature-item">
              <div class="feature-icon-wrapper">
                <span class="feature-icon">✓</span>
              </div>
              <span class="feature-text">PvP-дуэли на скорость</span>
            </div>
          </div>
        </div>

        <!-- Блок регистрации/входа -->
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

            <div class="version-info">
              <p class="version-text">
                Версия платформы 1.0.0
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* ==================== БАЗОВЫЕ СТИЛИ ==================== */

.home-container {
  min-height: 100vh;
  background-color: #f9fafb;
  color: #111827;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  line-height: 1.5;
}

.home-main {
  max-width: 1280px;
  margin: 0 auto;
  padding: 16px;
}

.home-content {
  display: flex;
  flex-direction: column;
  gap: 48px;
}

.hero-section {
  flex: 1;
}

.hero-title {
  font-size: 32px;
  font-weight: 800;
  letter-spacing: -0.025em;
  color: #4f46e5;
  margin-bottom: 20px;
  line-height: 1.2;
}

.hero-description {
  font-size: 16px;
  color: #4b5563;
  line-height: 1.6;
  margin-bottom: 24px;
}

.features-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
  padding-top: 16px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: white;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.feature-icon-wrapper {
  flex-shrink: 0;
}

.feature-icon {
  display: inline-block;
  background-color: #d1fae5;
  color: #059669;
  padding: 8px;
  border-radius: 50%;
  font-size: 14px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.feature-text {
  font-weight: 500;
  color: #374151;
  font-size: 14px;
}

.cta-section {
  flex: 1;
}

.cta-card {
  background-color: white;
  padding: 24px;
  border-radius: 20px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
  border: 1px solid #f3f4f6;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 20px;
}

.cta-title {
  font-size: 24px;
  font-weight: 900;
  color: #1f2937;
  letter-spacing: -0.025em;
  line-height: 1.3;
}

.cta-description {
  color: #6b7280;
  font-weight: 500;
  line-height: 1.6;
  font-size: 15px;
}

.auth-buttons {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.btn-register,
.btn-login,
.btn-profile {
  width: 100%;
  padding: 14px;
  font-weight: 600;
  border-radius: 12px;
  text-align: center;
  text-decoration: none;
  transition: all 0.2s ease;
  display: inline-block;
  font-size: 15px;
  border: none;
  cursor: pointer;
}

.btn-register {
  background-color: #22c55e;
  color: white;
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.15);
}

.btn-register:hover {
  background-color: #16a34a;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(34, 197, 94, 0.25);
}

.btn-login {
  background-color: white;
  border: 2px solid #4f46e5;
  color: #4f46e5;
}

.btn-login:hover {
  background-color: #f8fafc;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.1);
}

.btn-profile {
  background-color: #22c55e;
  color: white;
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.15);
}

.btn-profile:hover {
  background-color: #16a34a;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(34, 197, 94, 0.25);
}

.version-info {
  width: 100%;
  padding-top: 16px;
  border-top: 1px solid #f3f4f6;
}

.version-text {
  font-size: 12px;
  color: #9ca3af;
  font-weight: 500;
}

/* ==================== АДАПТИВНЫЕ СТИЛИ ==================== */

@media (min-width: 380px) {
  .hero-title {
    font-size: 28px;
  }
  
  .hero-description {
    font-size: 15px;
  }
  
  .cta-card {
    padding: 20px;
  }
  
  .cta-title {
    font-size: 22px;
  }
  
  .btn-register,
  .btn-login,
  .btn-profile {
    padding: 12px;
    font-size: 14px;
  }
}


@media (min-width: 640px) {
  .home-main {
    padding: 24px;
  }
  
  .hero-title {
    font-size: 40px;
  }
  
  .hero-description {
    font-size: 18px;
    line-height: 1.7;
  }
  
  .feature-text {
    font-size: 16px;
  }
  
  .cta-card {
    padding: 32px;
    border-radius: 24px;
    gap: 24px;
  }
  
  .cta-title {
    font-size: 28px;
  }
  
  .cta-description {
    font-size: 16px;
    line-height: 1.75;
  }
  
  .auth-buttons {
    gap: 16px;
  }
  
  .btn-register,
  .btn-login,
  .btn-profile {
    padding: 16px;
    border-radius: 16px;
    font-size: 16px;
  }
}


@media (min-width: 768px) {
  .home-main {
    padding: 32px 24px;
  }
  
  .hero-title {
    font-size: 48px;
    margin-bottom: 24px;
  }
  
  .hero-description {
    font-size: 20px;
    line-height: 1.75;
  }
  
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
  }
  
  .feature-item {
    padding: 16px;
  }
  
  .cta-title {
    font-size: 30px;
  }
}


@media (min-width: 1024px) {
  .home-main {
    padding: 64px 24px;
  }
  
  .home-content {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    gap: 48px;
  }
  
  .hero-section {
    width: 60%;
  }
  
  .hero-title {
    font-size: 56px;
  }
  
  .cta-section {
    width: 33.333%;
  }
  
  .cta-card {
    border-radius: 32px;
  }
}


@media (min-width: 1280px) {
  .home-main {
    padding: 96px 24px;
  }
  
  .hero-title {
    font-size: 72px;
  }
}


@media (min-width: 1536px) {
  .home-main {
    max-width: 1400px;
    padding: 120px 48px;
  }
  
  .hero-title {
    font-size: 80px;
  }
  
  .hero-description {
    font-size: 22px;
  }
  
  .cta-card {
    padding: 40px;
  }
}
</style>