<script setup>
import { ref, reactive, watch, onMounted, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import axios from 'axios'; // Используем axios, как и в твоем сторе
import { useConstantsStore } from '@/pinia/ConstantsStore';
import { shallowRef } from 'vue';

// --- Config ---
// Если у тебя axios настроен глобально (baseURL), можно убрать /api, 
// но для надежности оставлю относительный путь или используй импорт инстанса
const API_URL = '/tasks/'; 

// --- Store & Router ---
const constantsStore = useConstantsStore();
const router = useRouter();
const route = useRoute();

// --- State ---


const tasks = shallowRef([]);
const totalTasks = ref(0);
const isLoading = ref(false);
const error = ref(null);

// --- Filters State ---
// Используем названия полей как в сторе: subject (вместо category)
const filters = reactive({
  search: route.query.search || '',
  subject: route.query.subject || '',
  difficulty: route.query.difficulty || '',
});

// --- Pagination ---
const pagination = reactive({
  page: Number(route.query.page) || 1,
  limit: 20,
});

// --- Utils ---
let searchTimeout = null;     // Для debounce поиска
let abortController = null;   // Для отмены старых запросов

// --- Actions ---

/**
 * Основная функция получения задач с сервера
 */
const fetchTasks = async () => {
  // 1. Отмена предыдущего запроса (Race condition protection)
  if (abortController) abortController.abort();
  abortController = new AbortController();

  isLoading.value = true;
  error.value = null;

  try {
    // 2. Формируем параметры запроса
    const params = {
      skip: (pagination.page - 1) * pagination.limit,
      limit: pagination.limit,
      // Добавляем фильтры только если они выбраны
      ...(filters.search && { search: filters.search }),
      ...(filters.subject && { subject: filters.subject }),
      ...(filters.difficulty && { difficulty: filters.difficulty }),
    };

    // 3. Запрос через Axios
    const response = await axios.get(API_URL, {
      params,
      signal: abortController.signal, // Связываем с контроллером отмены
    });

    // 4. Обработка ответа
    // Предполагаем формат { items: [], total: 100 } или просто []
    const data = response.data;
    
    if (Array.isArray(data)) {
      tasks.value = data;
      totalTasks.value = data.length; // Или запросить count отдельным запросом
    } else {
      tasks.value = data.items || data.data || [];
      totalTasks.value = data.total || data.count || 0;
    }

    // 5. Синхронизация URL (чтобы можно было скинуть ссылку другу)
    updateUrl();

  } catch (err) {
    if (axios.isCancel(err)) {
      // Запрос был отменен (нормальное поведение при быстром вводе)
      return;
    }
    console.error('Ошибка при загрузке задач:', err);
    error.value = 'Не удалось загрузить список задач.';
  } finally {
    isLoading.value = false;
  }
};

const updateUrl = () => {
  router.replace({
    query: {
      ...filters,
      page: pagination.page > 1 ? pagination.page : undefined, // Не мусорим в URL
    }
  });
};

const handlePageChange = (newPage) => {
  pagination.page = newPage;
  fetchTasks();
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

// --- Watchers ---

// 1. При изменении выпадающих списков — сразу грузим (сбрасывая на 1 страницу)
watch(
  () => [filters.subject, filters.difficulty],
  () => {
    pagination.page = 1;
    fetchTasks();
  }
);

// 2. При поиске — ждем (Debounce), чтобы не DDOS-ить сервер
watch(
  () => filters.search,
  () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      pagination.page = 1;
      fetchTasks();
    }, 400); // 400ms задержка
  }
);

// --- Lifecycle ---
onMounted(async () => {
  // Запускаем параллельно: загрузку задач и загрузку справочников (если их нет)
  const tasksPromise = fetchTasks();
  
  if (!constantsStore.isLoaded) {
    await constantsStore.fetchConstants();
  }
  
  await tasksPromise;
});

onUnmounted(() => {
  if (abortController) abortController.abort();
  clearTimeout(searchTimeout);
});
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    
    <div class="flex flex-col md:flex-row justify-between items-center mb-8 gap-4">
      <h1 class="text-3xl font-bold text-gray-800 dark:text-white">Все задачи</h1>
      <div v-if="!isLoading" class="text-sm text-gray-500 bg-gray-100 dark:bg-gray-700 px-3 py-1 rounded-full">
        Найдено: {{ totalTasks }}
      </div>
    </div>

    <div class="bg-white dark:bg-gray-800 p-5 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 mb-8 grid gap-4 md:grid-cols-4 items-end">
      
      <div class="col-span-1 md:col-span-2">
        <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">Поиск</label>
        <div class="relative">
          <input 
            v-model="filters.search"
            type="text" 
            placeholder="Название, тег или ключевое слово..." 
            class="w-full pl-10 pr-4 py-2.5 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all"
          />
          <span class="absolute left-3 top-3 text-gray-400">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
          </span>
        </div>
      </div>

      <div>
        <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">Предмет</label>
        <div class="relative">
          <select 
            v-model="filters.subject" 
            class="w-full appearance-none pl-4 pr-10 py-2.5 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none transition-all cursor-pointer"
            :disabled="constantsStore.loading"
          >
            <option value="">Все предметы</option>
            <option 
              v-for="subj in constantsStore.subjects" 
              :key="subj.key" 
              :value="subj.key"
            >
              {{ subj.label }}
            </option>
          </select>
          <div class="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none text-gray-500">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
          </div>
        </div>
      </div>

      <div>
        <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">Сложность</label>
        <div class="relative">
          <select 
            v-model="filters.difficulty"
            class="w-full appearance-none pl-4 pr-10 py-2.5 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none transition-all cursor-pointer"
            :disabled="constantsStore.loading"
          >
            <option value="">Любая</option>
            <option 
              v-for="diff in constantsStore.difficulty" 
              :key="diff.key" 
              :value="diff.key"
            >
              {{ diff.label }}
            </option>
          </select>
           <div class="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none text-gray-500">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
          </div>
        </div>
      </div>
    </div>

    <div v-if="error" class="bg-red-50 text-red-600 p-4 rounded-lg mb-6 border border-red-100 flex items-center gap-3">
      <svg class="w-6 h-6 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
      <span>{{ error }}</span>
    </div>

    <div v-if="isLoading && !tasks.length" class="grid grid-cols-1 md:grid-cols-3 gap-6 animate-pulse">
       <div v-for="i in 6" :key="i" class="h-48 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
    </div>

    <div v-else-if="tasks.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <article 
        v-for="task in tasks" 
        :key="task.id" 
        class="bg-white dark:bg-gray-800 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300 p-6 flex flex-col border border-gray-100 dark:border-gray-700"
      >
        <div class="flex flex-wrap gap-2 mb-3">
          <span class="px-2.5 py-0.5 text-xs font-semibold rounded-md bg-indigo-50 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300">
            {{ constantsStore.getSubjectLabel(task.subject) }}
          </span>
          <span 
            class="px-2.5 py-0.5 text-xs font-semibold rounded-md"
            :class="{
              'bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-300': task.difficulty === 'EASY',
              'bg-yellow-50 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300': task.difficulty === 'MEDIUM',
              'bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-300': task.difficulty === 'HARD'
            }"
          >
            {{ constantsStore.getDifficultyLabel(task.difficulty) }}
          </span>
        </div>
        
        <h3 class="text-xl font-bold mb-2 text-gray-900 dark:text-white leading-tight">
          {{ task.title }}
        </h3>
        
        <p class="text-gray-600 dark:text-gray-400 text-sm mb-5 line-clamp-3 flex-grow">
          {{ task.description || 'Описание отсутствует' }}
        </p>

        <router-link 
          :to="`/tasks/${task.id}`" 
          class="mt-auto block text-center w-full py-2.5 px-4 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-lg hover:bg-gray-800 dark:hover:bg-gray-100 transition font-medium"
        >
          Перейти к задаче
        </router-link>
      </article>
      <BasePagination 
        :current="pagination.page" 
        :total="totalTasks" 
        :limit="pagination.limit"
        @change="handlePageChange"
      />
    </div>

    <div v-else-if="!isLoading && !error" class="flex flex-col items-center justify-center py-16 text-center">
        <div class="bg-gray-100 dark:bg-gray-700 p-4 rounded-full mb-4">
           <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
        </div>
        <h3 class="text-lg font-medium text-gray-900 dark:text-white">Ничего не найдено</h3>
        <p class="text-gray-500 mt-1 max-w-sm">
          Попробуйте изменить параметры поиска или сбросить фильтры.
        </p>
        <button 
          @click="filters.search = ''; filters.subject = ''; filters.difficulty = ''" 
          class="mt-4 text-indigo-600 hover:text-indigo-700 font-medium"
        >
            Очистить фильтры
        </button>
    </div>

    <div v-if="tasks.length > 0" class="mt-10 flex justify-center items-center gap-3 select-none">
      <button 
        :disabled="pagination.page === 1 || isLoading"
        @click="handlePageChange(pagination.page - 1)"
        class="p-2 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed transition"
      >
        <svg class="w-5 h-5 text-gray-600 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
      </button>
      
      <span class="text-sm font-medium text-gray-700 dark:text-gray-300 min-w-[3rem] text-center">
        {{ pagination.page }}
      </span>

      <button 
        :disabled="(tasks.length < pagination.limit) || isLoading" 
        @click="handlePageChange(pagination.page + 1)"
        class="p-2 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed transition"
      >
         <svg class="w-5 h-5 text-gray-600 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
      </button>
    </div>

  </div>
</template>

<style scoped>
/* Утилита для обрезки текста */
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>