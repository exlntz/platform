<script>
import axios from "axios";
export default {
  name: "TasksView",
  data() {
    return {
      selectedSubj: '',
      selectedDiff: '',
      tasks: [],
      loading: false
    }
  },
  methods: {
    async tasksSearch() {
      this.loading = true;
      try {
        const response = await axios.get('http://127.0.0.1:8000/tasks/', {
          params: {
            subject: this.selectedSubj,
            difficulty: this.selectedDiff,
          }
        });
        this.tasks = response.data;
      } catch (error) {
        console.error("Ошибка при загрузке:", error);
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 py-12 px-6">
    <div class="max-w-6xl mx-auto">

      <div class="mb-12 space-y-8">
        <div class="text-left">
          <h1 class="text-4xl font-black text-slate-900 tracking-tight">Банк задач</h1>
          <p class="text-slate-500 mt-2 font-medium">Выбирай интересные темы и прокачивай свой рейтинг</p>
        </div>

        <div class="bg-white p-4 rounded-3xl shadow-xl shadow-slate-200/50 border border-slate-100 flex flex-wrap gap-4 items-center">
          <div class="flex-1 min-w-[200px]">
            <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1 ml-2">Предмет</label>
            <select v-model="selectedSubj" class="w-full bg-slate-50 border-none rounded-2xl px-4 py-3 text-sm font-bold text-slate-700 focus:ring-2 focus:ring-indigo-500 outline-none transition-all cursor-pointer">
              <option value="">Все предметы</option>
              <option value="математика">Математика</option>
              <option value="информатика">Информатика</option>
            </select>
          </div>

          <div class="flex-1 min-w-[200px]">
            <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1 ml-2">Сложность</label>
            <select v-model="selectedDiff" class="w-full bg-slate-50 border-none rounded-2xl px-4 py-3 text-sm font-bold text-slate-700 focus:ring-2 focus:ring-indigo-500 outline-none transition-all cursor-pointer">
              <option value="">Любая сложность</option>
              <option value="легко">Легкая</option>
              <option value="нормально">Нормальная</option>
              <option value="сложно">Сложная</option>
            </select>
          </div>

          <button
            @click="tasksSearch"
            :disabled="loading"
            class="px-8 py-4 bg-indigo-600 hover:bg-indigo-700 text-white font-black rounded-2xl shadow-lg shadow-indigo-100 transition-all active:scale-95 disabled:opacity-50 self-end"
          >
            {{ loading ? 'Поиск...' : 'Найти задачи' }}
          </button>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="task in tasks"
          :key="task.id"
          class="bg-white rounded-[2rem] p-8 border border-slate-100 shadow-xl hover:shadow-2xl transition-all group flex flex-col justify-between"
        >
          <div>
            <div class="flex justify-between items-start mb-6">
              <span
                :class="{
                  'bg-green-100 text-green-600': task.difficulty === 'легко',
                  'bg-blue-100 text-blue-600': task.difficulty === 'нормально',
                  'bg-red-100 text-red-600': task.difficulty === 'сложно'
                }"
                class="px-4 py-1 rounded-full text-[10px] font-black uppercase tracking-widest"
              >
                {{ task.difficulty }}
              </span>
              <span class="text-slate-300 font-bold text-xs">#{{ task.id }}</span>
            </div>

            <h3 class="text-xl font-black text-slate-900 mb-3 group-hover:text-indigo-600 transition-colors">
              {{ task.title }}
            </h3>

            <p class="text-slate-500 text-sm leading-relaxed mb-6 line-clamp-3">
              {{ task.description }}
            </p>
          </div>

          <div class="space-y-4">
            <div class="flex items-center gap-4 py-4 border-t border-slate-50">
              <div class="text-[10px] font-bold">
                <p class="text-slate-400 uppercase">Предмет</p>
                <p class="text-slate-900">{{ task.subject }}</p>
              </div>
              <div class="text-[10px] font-bold">
                <p class="text-slate-400 uppercase">Тема</p>
                <p class="text-slate-900">{{ task.theme }}</p>
              </div>
            </div>

            <button class="w-full py-4 bg-slate-900 hover:bg-indigo-600 text-white font-black rounded-2xl transition-all active:scale-95">
              Решать задачу
            </button>
          </div>
        </div>
      </div>

      <div v-if="tasks.length === 0 && !loading" class="text-center py-20 bg-white rounded-[3rem] border-2 border-dashed border-slate-100">
        <div class="text-5xl mb-4">🔍</div>
        <h3 class="text-xl font-bold text-slate-900">Задачи не найдены</h3>
        <p class="text-slate-400 mt-2">Попробуй изменить фильтры или нажми кнопку поиска</p>
      </div>

    </div>
  </div>
</template>
