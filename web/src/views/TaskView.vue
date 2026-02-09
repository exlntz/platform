<script setup>
import { ref, onMounted, computed, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api/axios'
import { useTimerStore } from '@/pinia/TimerStore.js'

const timer = useTimerStore()
const router = useRouter()
const route = useRoute()

const showHint = ref(false)
const task = ref(null)
const loading = ref(true)
const answer = ref('')
const checkLoading = ref(false)
const checkResult = ref(null)
const isSolved = ref(false)

const screenSize = ref('mobile')

const updateScreenSize = () => {
  const width = window.innerWidth
  if (width < 640) screenSize.value = 'mobile'
  else if (width < 768) screenSize.value = 'sm'
  else if (width < 1024) screenSize.value = 'tablet'
  else screenSize.value = 'desktop'
}

const getAuthHeader = () => {
  const token = localStorage.getItem('user-token')
  return token ? { headers: { Authorization: `Bearer ${token}` } } : {}
}

const fetchTask = async () => {
  try {
    const response = await api.get(`/tasks/${route.params.id}`, getAuthHeader())
    task.value = response.data
  } catch (err) {
    console.error('Ошибка:', err)
  } finally {
    loading.value = false
  }
}

const submitAnswer = async () => {
  if (!answer.value.trim()) return
  checkLoading.value = true
  checkResult.value = null

  try {
    const response = await api.post(
      `/tasks/${task.value.id}/check`,
      { answer: answer.value, time_spent: timer.elapsedSeconds },
      getAuthHeader(),
    )
    checkResult.value = response.data
    if (response.data.is_correct) {
      isSolved.value = true
      timer.stopTimer()
    }
  } catch (err) {
    checkResult.value = { is_correct: false, message: 'Ошибка сервера.' }
  } finally {
    checkLoading.value = false
  }
}

const backToTasks = () => {
  const query = { ...route.query }
  delete query.id
  router.push({ path: '/tasks', query })
}

const resultMessageClass = computed(() => {
  if (!checkResult.value) return ''
  return checkResult.value.is_correct ? 'success' : 'error'
})

onMounted(() => {
  updateScreenSize()
  window.addEventListener('resize', updateScreenSize)
  fetchTask()
  timer.startTask()
})

onUnmounted(() => {
  window.removeEventListener('resize', updateScreenSize)
  if (!isSolved.value) timer.pauseTimer()
})

watch(
  () => route.params.id,
  () => {
    loading.value = true
    task.value = null
    answer.value = ''
    checkResult.value = null
    isSolved.value = false
    showHint.value = false
    fetchTask()
    timer.resetTimer()
    timer.startTask()
  },
)
</script>

<template>
  <div class="task-container">
    <div v-if="loading" class="loading-state">
      <div class="loading-title" :class="{ mobile: screenSize === 'mobile' }"></div>
      <div class="loading-subtitle" :class="{ mobile: screenSize === 'mobile' }"></div>
    </div>

    <div v-else-if="task" class="task-layout">
      <div class="top-nav">
        <button @click="backToTasks" class="back-link">
          <span class="back-icon">←</span>
          <span class="back-text">К списку</span>
        </button>
        <div v-if="!isSolved" class="timer-badge">⏱️ {{ timer.elapsedSeconds }} сек</div>
      </div>

      <div class="task-card-scroll-area">
        <div class="task-card">
          <div class="task-header">
            <div class="task-header-overlay"></div>
            <div class="task-header-content">
              <div class="header-tags">
                <span class="subject-tag" :class="{ mobile: screenSize === 'mobile' }">{{
                  task.subject
                }}</span>
                <span class="difficulty-tag" :class="{ mobile: screenSize === 'mobile' }">{{
                  task.difficulty
                }}</span>
              </div>
              <h1 class="task-title" :class="{ mobile: screenSize === 'mobile' }">
                {{ task.title }}
              </h1>
            </div>
          </div>

          <div class="task-body">
            <div class="task-section">
              <h3 class="section-title" :class="{ mobile: screenSize === 'mobile' }">
                Условие задачи
              </h3>
              <p class="task-description" :class="{ mobile: screenSize === 'mobile' }">
                {{ task.description }}
              </p>
            </div>

            <div v-if="task.hint" class="hint-section">
              <button
                @click="showHint = !showHint"
                class="hint-btn"
                :class="{ active: showHint, mobile: screenSize === 'mobile' }"
              >
                <span class="hint-icon">💡</span>
                <span class="hint-text-content">
                  {{ showHint ? 'Скрыть подсказку' : 'Показать подсказку' }}
                </span>
              </button>

              <div v-if="showHint" class="hint-content">
                <div class="hint-badge">Подсказка</div>
                <p class="hint-text">{{ task.hint }}</p>
              </div>
            </div>

            <hr class="divider" :class="{ mobile: screenSize === 'mobile' }" />

            <div class="answer-section">
              <div
                v-if="checkResult"
                class="result-message"
                :class="[resultMessageClass, { mobile: screenSize === 'mobile' }]"
              >
                <div class="result-icon">
                  <span v-if="checkResult.is_correct">🎉</span>
                  <span v-else>❌</span>
                </div>
                <span class="result-text">{{ checkResult.message }}</span>
              </div>

              <div class="answer-input-group">
                <label class="input-label" :class="{ mobile: screenSize === 'mobile' }"
                  >Ваш ответ</label
                >
                <textarea
                  v-model="answer"
                  @keydown.enter.exact.prevent="submitAnswer"
                  :rows="screenSize === 'mobile' ? 3 : 3"
                  :disabled="isSolved"
                  placeholder="Введите решение..."
                  class="answer-textarea"
                  :class="{
                    mobile: screenSize === 'mobile',
                    'correct-answer': isSolved,
                    'wrong-answer': checkResult && !checkResult.is_correct,
                  }"
                ></textarea>
              </div>

              <div class="submit-section">
                <button
                  v-if="isSolved"
                  @click="backToTasks"
                  class="back-to-tasks-btn"
                  :class="{ mobile: screenSize === 'mobile' }"
                >
                  <span class="btn-text">← Вернуться ко всем задачам</span>
                </button>

                <button
                  v-else
                  @click="submitAnswer"
                  :disabled="checkLoading || !answer"
                  class="submit-btn"
                  :class="{
                    mobile: screenSize === 'mobile',
                    disabled: checkLoading || !answer,
                  }"
                >
                  <span v-if="checkLoading" class="spinner"></span>
                  <span class="btn-text">
                    {{ checkLoading ? 'Проверка...' : 'Отправить решение' }}
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="timer.isAfkAlertVisible" class="afk-modal-overlay">
      <div class="afk-modal" :class="{ mobile: screenSize === 'mobile' }">
        <div class="afk-icon">⏰</div>
        <h3 class="afk-title">Вы все еще здесь?</h3>
        <p class="afk-message">Таймер приостановлен из-за неактивности.</p>
        <button @click="timer.confirmAfk" class="afk-confirm-btn">Да, продолжить</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ==================== НОВЫЙ ЛЭЙАУТ (БЕЗ СКРОЛЛА СТРАНИЦЫ) ==================== */

.task-container {
  /* Фиксируем контейнер на весь экран */
  width: 100%;
  height: 100vh;
  height: 100dvh; /* Для мобильных браузеров */
  background-color: #f8fafc;
  font-family:
    -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  line-height: 1.5;
  overflow: hidden; /* Убираем скролл body */
  display: flex;
  flex-direction: column;
}

/* Обертка для контента */
.task-layout {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  max-width: 900px; /* Ограничиваем ширину на десктопе */
  margin: 0 auto;
}

/* Верхняя панель */
.top-nav {
  flex-shrink: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #f8fafc; /* Цвет фона страницы */
  z-index: 10;
}

/* Таймер в шапке */
.timer-badge {
  font-size: 14px;
  font-weight: 700;
  color: #475569;
  background: #e2e8f0;
  padding: 6px 12px;
  border-radius: 20px;
}

/* Область скролла для карточки */
.task-card-scroll-area {
  flex: 1; /* Занимает все доступное место */
  overflow-y: auto; /* Скролл только здесь */
  padding: 0 16px 16px 16px; /* Отступы для карточки */

  /* Скрываем скроллбар для красоты, но оставляем функционал */
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 transparent;
}

/* Кастомизация скроллбара */
.task-card-scroll-area::-webkit-scrollbar {
  width: 6px;
}
.task-card-scroll-area::-webkit-scrollbar-track {
  background: transparent;
}
.task-card-scroll-area::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 10px;
}

/* ==================== ВАШИ СТИЛИ (НЕ ТРОНУТЫ) ==================== */

.task-card {
  background-color: white;
  border-radius: 24px;
  box-shadow: 0 10px 25px -5px rgba(148, 163, 184, 0.3);
  border: 1px solid #f1f5f9;
  overflow: hidden;
  /* Убрал margin-bottom, так как отступ теперь в scroll-area */
}

/* ==================== СОСТОЯНИЕ ЗАГРУЗКИ ==================== */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%; /* Центрируем по вертикали */
  animation: pulse 2s infinite;
}

.loading-title {
  height: 32px;
  width: 256px;
  background-color: #e2e8f0;
  border-radius: 9999px;
  margin-bottom: 16px;
}

.loading-title.mobile {
  height: 24px;
  width: 200px;
}

.loading-subtitle {
  height: 16px;
  width: 128px;
  background-color: #e2e8f0;
  border-radius: 9999px;
}

.loading-subtitle.mobile {
  height: 12px;
  width: 100px;
}

/* ==================== ССЫЛКА НАЗАД ==================== */
.back-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #64748b;
  text-decoration: none;
  /* padding убран, так как он задается в top-nav */
  transition: color 0.2s ease;
  background: none;
  border: none;
  cursor: pointer;
  font-family: inherit;
}

.back-link:hover {
  color: #4f46e5;
}

.back-icon {
  font-size: 18px;
  font-weight: bold;
}

.back-text {
  font-weight: 500;
}

/* ==================== ОСТАЛЬНЫЕ ВАШИ СТИЛИ ==================== */

.task-header {
  background-color: #0f172a;
  padding: 0;
  color: white;
  position: relative;
  overflow: hidden;
}

.task-header-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.1) 0%, rgba(124, 58, 237, 0.1) 100%);
}

.task-header-content {
  position: relative;
  z-index: 10;
  padding: 24px;
}

.header-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.subject-tag {
  padding: 6px 12px;
  background-color: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(12px);
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #a5b4fc;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.subject-tag.mobile {
  padding: 4px 8px;
  font-size: 11px;
}

.difficulty-tag {
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background-color: rgba(255, 255, 255, 0.05);
}

.difficulty-tag.mobile {
  padding: 4px 8px;
  font-size: 11px;
}

.task-title {
  font-size: 32px;
  font-weight: 900;
  letter-spacing: -0.025em;
  line-height: 1.3;
  margin: 0;
}

.task-title.mobile {
  font-size: 20px;
}

.task-body {
  padding: 24px;
}

.task-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 12px;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 12px;
}

.section-title.mobile {
  font-size: 11px;
  margin-bottom: 8px;
}

.task-description {
  font-size: 16px;
  color: #334155;
  font-weight: 500;
  line-height: 1.6;
  white-space: pre-wrap;
}

.task-description.mobile {
  font-size: 15px;
  line-height: 1.5;
}

.divider {
  border: none;
  border-top: 1px solid #f1f5f9;
  margin: 24px 0;
}

.divider.mobile {
  margin: 20px 0;
}

.answer-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.result-message {
  padding: 16px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  display: flex;
  align-items: center;
  animation: fadeInUp 0.4s ease-out;
}

.result-message.mobile {
  padding: 12px;
  font-size: 13px;
}

.result-message.success {
  background-color: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.result-message.error {
  background-color: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.result-icon {
  font-size: 20px;
  margin-right: 12px;
  flex-shrink: 0;
}

.result-text {
  flex: 1;
}

.answer-input-group {
  display: flex;
  flex-direction: column;
}

.input-label {
  font-size: 12px;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
  margin-left: 4px;
}

.input-label.mobile {
  font-size: 11px;
  margin-bottom: 6px;
}

.answer-textarea {
  width: 100%;
  background-color: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px;
  font-size: 15px;
  color: #0f172a;
  font-weight: 500;
  outline: none;
  transition: all 0.2s ease;
  resize: vertical;
  font-family: inherit;
  min-height: 100px;
}

.answer-textarea.mobile {
  padding: 12px;
  font-size: 14px;
  min-height: 80px;
}

.answer-textarea:focus {
  border-color: #4f46e5;
  background-color: white;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.answer-textarea:disabled {
  background-color: #f8fafc;
  color: #64748b;
  border-color: #f1f5f9;
  cursor: not-allowed;
}

.answer-textarea.correct-answer {
  border-color: #10b981;
  background-color: rgba(16, 185, 129, 0.05);
}

.answer-textarea.wrong-answer {
  border-color: #f87171;
  background-color: rgba(248, 113, 113, 0.05);
}

.answer-textarea::placeholder {
  color: #94a3b8;
}

.submit-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-top: 8px;
}

.timer-display {
  /* Стили для таймера внутри блока отправки (если вернем туда) */
  font-size: 14px;
  color: #64748b;
  font-weight: 600;
  padding: 8px 12px;
  background-color: #f1f5f9;
  border-radius: 8px;
  text-align: center;
}

.back-to-tasks-btn,
.submit-btn {
  width: 100%;
  padding: 16px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 16px;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  font-family: inherit;
}

.back-to-tasks-btn.mobile,
.submit-btn.mobile {
  padding: 14px;
  font-size: 15px;
}

.back-to-tasks-btn {
  background-color: #0f172a;
  color: white;
  box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.1);
}

.back-to-tasks-btn:hover {
  background-color: #1e293b;
  transform: translateY(-1px);
  box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.1);
}

.back-to-tasks-btn:active {
  transform: translateY(0);
}

.submit-btn {
  background-color: #4f46e5;
  color: white;
  box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.1);
}

.submit-btn:hover:not(.disabled) {
  background-color: #4338ca;
  transform: translateY(-1px);
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.1);
}

.submit-btn:active:not(.disabled) {
  transform: translateY(0);
}

.submit-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.submit-btn.disabled:hover {
  transform: none;
  box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.1);
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.btn-text {
  text-align: center;
}

/* AFK Modal */
.afk-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}

.afk-modal {
  background-color: white;
  border-radius: 20px;
  padding: 32px;
  max-width: 400px;
  width: 100%;
  text-align: center;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  animation: fadeInUp 0.3s ease-out;
}

.afk-modal.mobile {
  padding: 24px;
  border-radius: 16px;
}

.afk-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.afk-title {
  font-size: 24px;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 12px;
}

.afk-modal.mobile .afk-title {
  font-size: 20px;
}

.afk-message {
  color: #64748b;
  font-size: 16px;
  line-height: 1.5;
  margin-bottom: 24px;
}

.afk-modal.mobile .afk-message {
  font-size: 14px;
}

.afk-confirm-btn {
  background-color: #4f46e5;
  color: white;
  border: none;
  border-radius: 12px;
  padding: 14px 32px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.1);
  font-family: inherit;
}

.afk-confirm-btn:hover {
  background-color: #4338ca;
  transform: translateY(-1px);
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.1);
}

.afk-confirm-btn:active {
  transform: translateY(0);
}

/* Animations */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* Hint */
.hint-section {
  margin-bottom: 24px;
}

.hint-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: none;
  border: 1px solid #e2e8f0;
  padding: 8px 16px;
  border-radius: 12px;
  cursor: pointer;
  color: #64748b;
  font-weight: 600;
  font-size: 13px;
  transition: all 0.2s ease;
  width: 100%;
  font-family: inherit;
}

@media (min-width: 640px) {
  .hint-btn {
    width: auto;
    display: inline-flex;
  }
}

.hint-btn:hover {
  background-color: #f8fafc;
  color: #4f46e5;
  border-color: #c7d2fe;
}

.hint-btn.active {
  background-color: #eef2ff;
  color: #4f46e5;
  border-color: #a5b4fc;
}

.hint-content {
  margin-top: 12px;
  background-color: #fffbeb;
  border: 1px solid #fcd34d;
  border-radius: 12px;
  padding: 16px;
  position: relative;
  overflow: hidden;
}

.hint-badge {
  display: inline-block;
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
  color: #b45309;
  background-color: #fef3c7;
  padding: 2px 6px;
  border-radius: 4px;
  margin-bottom: 8px;
}

.hint-text {
  font-size: 14px;
  color: #92400e;
  line-height: 1.5;
  font-weight: 500;
}

/* DARK MODE */
:root.dark .task-container {
  background-color: #0f172a;
  color: #f1f5f9;
}
:root.dark .top-nav {
  background-color: #0f172a;
}
:root.dark .back-link {
  color: #94a3b8;
}
:root.dark .back-link:hover {
  color: #60a5fa;
}
:root.dark .timer-badge {
  background: #1e293b;
  color: #cbd5e1;
}
:root.dark .task-card {
  background-color: #1e293b;
  border-color: #334155;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
}
:root.dark .task-card-scroll-area::-webkit-scrollbar-thumb {
  background-color: #475569;
}
:root.dark .task-header {
  background-color: #334155;
}
:root.dark .task-header-overlay {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(37, 99, 235, 0.15) 100%);
}
:root.dark .subject-tag {
  background-color: rgba(255, 255, 255, 0.15);
  color: #93c5fd;
  border-color: rgba(255, 255, 255, 0.2);
}
:root.dark .difficulty-tag {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  color: #cbd5e1;
}
:root.dark .task-title {
  color: #f8fafc;
}
:root.dark .section-title {
  color: #94a3b8;
}
:root.dark .task-description {
  color: #cbd5e1;
}
:root.dark .divider {
  border-top-color: #334155;
}
:root.dark .answer-textarea {
  background-color: #334155;
  border-color: #475569;
  color: #f1f5f9;
}
:root.dark .answer-textarea:focus {
  background-color: #334155;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}
:root.dark .answer-textarea::placeholder {
  color: #94a3b8;
}
:root.dark .answer-textarea:disabled {
  background-color: #334155;
  color: #94a3b8;
  border-color: #475569;
}
:root.dark .answer-textarea.correct-answer {
  border-color: #10b981;
  background-color: rgba(16, 185, 129, 0.15);
}
:root.dark .answer-textarea.wrong-answer {
  border-color: #f87171;
  background-color: rgba(248, 113, 113, 0.15);
}
:root.dark .back-to-tasks-btn {
  background-color: #334155;
  color: #f1f5f9;
}
:root.dark .back-to-tasks-btn:hover {
  background-color: #475569;
}
:root.dark .submit-btn {
  background-color: #3b82f6;
}
:root.dark .submit-btn:hover:not(.disabled) {
  background-color: #2563eb;
}
:root.dark .afk-modal {
  background-color: #1e293b;
  color: #f1f5f9;
}
:root.dark .afk-title {
  color: #f8fafc;
}
:root.dark .afk-message {
  color: #cbd5e1;
}
:root.dark .afk-confirm-btn {
  background-color: #3b82f6;
}
:root.dark .afk-confirm-btn:hover {
  background-color: #2563eb;
}
:root.dark .loading-title,
:root.dark .loading-subtitle {
  background-color: #334155;
}
:root.dark .hint-btn {
  border-color: #475569;
  color: #94a3b8;
}
:root.dark .hint-btn:hover {
  background-color: #334155;
  color: #60a5fa;
  border-color: #3b82f6;
}
:root.dark .hint-btn.active {
  background-color: #1e3a8a;
  color: #93c5fd;
  border-color: #3b82f6;
}
:root.dark .hint-content {
  background-color: #78350f;
  border-color: #92400e;
}
:root.dark .hint-badge {
  color: #fbbf24;
  background-color: #92400e;
}
:root.dark .hint-text {
  color: #fde68a;
}
:root.dark .result-message.success {
  background-color: #065f46;
  color: #a7f3d0;
  border-color: #047857;
}
:root.dark .result-message.error {
  background-color: #7f1d1d;
  color: #fecaca;
  border-color: #991b1b;
}

/* ==================== АДАПТИВНОСТЬ ==================== */
@media (max-width: 320px) {
  .top-nav {
    padding: 10px;
  }
  .task-card-scroll-area {
    padding: 0 10px 10px 10px;
  }
  .task-header-content,
  .task-body {
    padding: 16px;
  }
  .task-title {
    font-size: 18px;
  }
  .task-description {
    font-size: 14px;
  }
  .back-to-tasks-btn,
  .submit-btn {
    padding: 12px;
    font-size: 14px;
  }
}

@media (min-width: 321px) and (max-width: 375px) {
  .task-title {
    font-size: 20px;
  }
}

@media (min-width: 640px) {
  .task-header-content,
  .task-body {
    padding: 24px;
  }
  .task-title {
    font-size: 24px;
  }
  .task-description {
    font-size: 16px;
    line-height: 1.6;
  }
}

@media (min-width: 768px) {
  .task-header-content,
  .task-body {
    padding: 32px;
  }
  .task-title {
    font-size: 28px;
  }
}

@media (min-width: 1024px) {
  .task-layout {
    padding-top: 20px;
    padding-bottom: 20px;
  }
  .top-nav {
    border-radius: 12px;
    margin-bottom: 10px;
    background: transparent;
    padding: 0;
  }
  .task-card-scroll-area {
    overflow-y: auto;
    padding-right: 8px;
  }
}
</style>
