<script>
export default {
  name: "TasksView"
}
</script>

<template>
  <div class="Tasks">
    <h1>Tasks list</h1>
    <div class="filters">
      <select>
        <option value="">Все предметы</option>
        <option value="math">Математика</option>
        <option value="it">Информатика</option>
      </select>
      <select>
        <option value="">Любая сложность</option>
        <option value="easy">Легкая</option>
        <option value="hard">Сложная</option>
      </select>
    </div>
    <div class="task-list">
        <div v-for="task in filteredTasks" :key="task.id" class="task-card">
          <h3>{{ task.title }}</h3>
          <p>Тема: {{ task.topic }} | Сложность: {{ task.difficulty }}</p>
          <button @click="startTask(task.id)">Решать</button>
        </div>
    </div>
  </div>

</template>

<style scoped>

</style>
