<script>
import axios from "axios";
export default {
  name: "TasksView",
  data(){
    return {
      selectedSubj: '',
      selectedDiff: '',
      tasks: []
    }
  },
  methods: {
    async tasksSearch() {
      try {
        const response = await axios.get('http://127.0.0.1:8000/tasks/', {
          params: {
            subject: this.selectedSubj,
            difficulty: this.selectedDiff,
          }
        });

        this.tasks = response.data;
        console.log("Задачи загружены:", this.tasks);
      } catch (error) {
        console.error("Ошибка при загрузке:", error);
      }
    }
  }
}
</script>

<template>
  <div class="Tasks">
    <h1>Tasks list</h1>
    <div class = 'filter-list'>
      <select v-model="selectedSubj">
        <option value="">Все предметы</option>
        <option value="математика">Математика</option>
        <option value="информатика">Информатика</option>
      </select>
      <select v-model="selectedDiff">
        <option value="">Любая сложность</option>
        <option value="легко">Легкая</option>
        <option value="нормально">Нормальная</option>
        <option value="сложно">Сложная</option>
      </select>
      <button @click="tasksSearch" class="search-btn"> Найти </button>
    </div>
    <div class="task-list">
        <div
          v-for="task in tasks"
          :key="task.id"
          class="task-card"
        >
          <div class="card-header">
            <h3>{{ task.title }}</h3>
            <span :class="['badge', task.difficulty]">
              {{ task.difficulty }}
            </span>
          </div>

          <p class="description">{{ task.description }}</p>

          <div class="meta-info">
            <small>Predmet: <b>{{ task.subject }}</b></small>
            <small>Tema: {{ task.theme }}</small>
          </div>

          <button class="btn-solve">Решать</button>
        </div>

        <div v-if="tasks.length === 0" class="empty-state">
          <p>Задачи не найдены или вы еще не нажали кнопку "Найти"</p>
        </div>
      </div>
    </div>
</template>

<style scoped>

</style>
