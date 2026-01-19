<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const task = ref(null)
const loading = ref(true)
const answer = ref('')
const checkLoading = ref(false)
const checkResult = ref(null)
const isSolved = ref(false) // НОВОЕ: Локальный флаг решения (сбрасывается при обновлении страницы)

const getAuthHeader = () => {
  return { headers: { Authorization: `Bearer ${localStorage.getItem('user-token')}` } }
}

// Загрузка задачи
const fetchTask = async () => {
  try {
    const response = await axios.get(`http://127.0.0.1:8000/tasks/${route.params.id}`, getAuthHeader())
    task.value = response.data
  } catch (err) {
    console.error('Ошибка:', err)
  } finally {
    loading.value = false
  }
}

// Отправка ответа
const submitAnswer = async () => {
  if (!answer.value.trim()) return

  checkLoading.value = true
  checkResult.value = null

  try {
    const response = await axios.post(
      `http://127.0.0.1:8000/tasks/${task.value.id}/check`,
      { answer: answer.value },
      getAuthHeader()
    )

    checkResult.value = response.data

    if (response.data.is_correct) {
      isSolved.value = true // БЛОКИРУЕМ интерфейс (только до перезагрузки)
    }
    // Если ответ неверный, isSolved остается false, можно пробовать дальше
  } catch (err) {
    checkResult.value = {
      is_correct: false,
      message: 'Ошибка сервера. Попробуйте позже.'
    }
  } finally {
    checkLoading.value = false
  }
}

onMounted(() => {
  fetchTask()
})
</script>

<template>
  <div class="task-container">
    <div v-if="loading" class="loading-state">
      <div class="loading-title"></div>
      <div class="loading-subtitle"></div>
    </div>

    <div v-else-if="task" class="task-content">
      <router-link to="/tasks" class="back-link">
        ← Вернуться к списку
      </router-link>

      <div class="task-card">
        <div class="task-header">
          <div class="header-tags">
            <span class="subject-tag">{{ task.subject }}</span>
            <span class="difficulty-tag">{{ task.difficulty }}</span>
          </div>
          <h1 class="task-title">{{ task.title }}</h1>
        </div>

        <div class="task-body">
          <div class="task-section">
            <h3 class="section-title">Условие задачи</h3>
            <p class="task-description">
              {{ task.description }}
            </p>
          </div>

          <hr class="divider">

          <div class="answer-section">
            <div v-if="checkResult"
                 class="result-message"
                 :class="resultMessageClass">
              <div class="result-icon">
                <span v-if="checkResult.is_correct">🎉</span>
                <span v-else>❌</span>
              </div>
              <span class="result-text">{{ checkResult.message }}</span>
            </div>

            <div class="answer-input-group">
              <label class="input-label">Ваш ответ</label>
              <textarea
                v-model="answer"
                rows="3"
                :disabled="isSolved"
                placeholder="Введите решение..."
                class="answer-textarea"
                :class="{
                  'correct-answer': isSolved,
                  'wrong-answer': checkResult && !checkResult.is_correct
                }"
              ></textarea>
            </div>

            <div class="submit-section">
              <router-link
                v-if="isSolved"
                to="/tasks"
                class="back-to-tasks-btn"
              >
                <span class="btn-text">← Вернуться ко всем задачам</span>
              </router-link>

              <button
                v-else
                @click="submitAnswer"
                :disabled="checkLoading || !answer"
                class="submit-btn"
                :class="{ disabled: checkLoading || !answer }"
              >
                <span v-if="checkLoading" class="spinner"></span>
                <span class="btn-text">{{ checkLoading ? 'Проверка...' : 'Отправить решение' }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.task-container {
  min-height: 100vh;
  background-color: #f8fafc;
  padding: 48px 24px;
  display: flex;
  justify-content: center;
  font-family: sans-serif;
}
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 80px;
  animation: pulse 2s infinite;
}
.loading-title {
  height: 32px;
  width: 256px;
  background-color: #e2e8f0;
  border-radius: 9999px;
  margin-bottom: 16px;
}
.loading-subtitle {
  height: 16px;
  width: 128px;
  background-color: #e2e8f0;
  border-radius: 9999px;
}
.task-content {
  width: 100%;
  max-width: 768px;
}
.back-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 700;
  color: #64748b;
  text-decoration: none;
  margin-bottom: 24px;
  transition: color 0.2s ease;
}
.back-link:hover {
  color: #4f46e5;
}
.task-card {
  background-color: white;
  border-radius: 40px;
  box-shadow: 0 25px 50px -12px rgba(148, 163, 184, 0.5);
  border: 1px solid #f1f5f9;
  overflow: hidden;
}
.task-header {
  background-color: #0f172a;
  padding: 32px;
  color: white;
  position: relative;
  overflow: hidden;
}
.task-header::before {
  content: '📝';
  position: absolute;
  top: 0;
  right: 0;
  font-size: 144px;
  opacity: 0.1;
  transform: translate(20%, -20%);
}
.header-tags {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}
.subject-tag {
  padding: 8px 12px;
  background-color: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(12px);
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #a5b4fc;
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.difficulty-tag {
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background-color: rgba(255, 255, 255, 0.05);
}
.task-title {
  font-size: 32px;
  font-weight: 900;
  letter-spacing: -0.025em;
  line-height: 1.2;
  position: relative;
  z-index: 10;
}
@media (min-width: 768px) {
  .task-title {
    font-size: 36px;
  }
}
.task-body {
  padding: 32px;
}
@media (min-width: 768px) {
  .task-body {
    padding: 40px;
  }
}
.task-section {
  margin-bottom: 32px;
}
.section-title {
  font-size: 12px;
  font-weight: 900;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 16px;
}
.task-description {
  font-size: 18px;
  color: #334155;
  font-weight: 500;
  line-height: 1.75;
  white-space: pre-wrap;
}
.divider {
  border: none;
  border-top: 1px solid #f1f5f9;
  margin: 32px 0;
}
.answer-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.result-message {
  padding: 20px;
  border-radius: 16px;
  font-size: 14px;
  font-weight: 900;
  display: flex;
  align-items: center;
  justify-content: space-between;
  animation: fadeInUp 0.4s ease-out;
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
  font-size: 24px;
}
.result-text {
  flex: 1;
  margin-left: 12px;
}
.answer-input-group {
  display: flex;
  flex-direction: column;
}
.input-label {
  font-size: 12px;
  font-weight: 900;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 8px;
  margin-left: 4px;
}
.answer-textarea {
  width: 100%;
  background-color: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 16px;
  padding: 20px;
  font-size: 16px;
  color: #0f172a;
  font-weight: 500;
  outline: none;
  transition: all 0.2s ease;
  resize: none;
  font-family: inherit;
}
.answer-textarea:focus {
  border-color: #4f46e5;
  background-color: white;
  box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.1);
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
  padding-top: 8px;
}
.back-to-tasks-btn,
.submit-btn {
  width: 100%;
  padding: 16px;
  border-radius: 16px;
  font-weight: 900;
  font-size: 16px;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
}
.back-to-tasks-btn {
  background-color: #0f172a;
  color: white;
  text-decoration: none;
  box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.1);
}
.back-to-tasks-btn:hover {
  background-color: #1e293b;
  transform: scale(1.02);
}
.back-to-tasks-btn:active {
  transform: scale(0.98);
}
.submit-btn {
  background-color: #4f46e5;
  color: white;
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.1);
}
.submit-btn:hover:not(.disabled) {
  background-color: #4338ca;
  transform: scale(1.02);
}
.submit-btn:active:not(.disabled) {
  transform: scale(0.98);
}
.submit-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
