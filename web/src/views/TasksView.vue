<script setup>
import { ref, reactive, watch, onMounted, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useConstantsStore } from '@/pinia/ConstantsStore';

// --- State & Stores ---
const constantsStore = useConstantsStore();
const router = useRouter();
const route = useRoute();

// --- Data State ---
const tasks = ref([]);
const totalTasks = ref(0);
const isLoading = ref(false);
const error = ref(null);

// --- Filters State ---
// Инициализируем из query параметров URL для сохранения состояния при перезагрузке
const filters = reactive({
  search: route.query.search || '',
  category: route.query.category || '',
  difficulty: route.query.difficulty || '',
});

// --- Pagination State ---
const pagination = reactive({
  page: Number(route.query.page) || 1,
  limit: 20, // Размер страницы
});

// --- Debounce Logic for Search ---
let searchTimeout = null;

// --- Abort Controller (для отмены старых запросов) ---
let abortController = null;

// --- API Interaction ---
const fetchTasks = async () => {
  // Отменяем предыдущий запрос, если он еще идет
  if (abortController) {
    abortController.abort();
  }
  abortController = new AbortController();

  isLoading.value = true;
  error.value = null;

  try {
    // Формируем Query Parameters
    const params = new URLSearchParams({
      skip: (pagination.page - 1) * pagination.limit,
      limit: pagination.limit,
    });

    if (filters.search) params.append('search', filters.search);
    if (filters.category) params.append('category', filters.category);
    if (filters.difficulty) params.append('difficulty', filters.difficulty);

    // Выполняем запрос
    const response = await fetch(`/api/tasks/?${params.toString()}`, {
      signal: abortController.signal,
      headers: {
        'Content-Type': 'application/json',
        // Добавь Authorization заголовок, если нужно (обычно берется из AuthStore или http-interceptor)
      }
    });

    if (!response.ok) throw new Error(`Error: ${response.statusText}`);

    const data = await response.json();
    
    // Адаптация под формат ответа (предполагая { items: [], total: ... } или просто [])
    // Если бекенд возвращает просто массив:
    if (Array.isArray(data)) {
      tasks.value = data;
      // Если API не возвращает total, считаем по факту (но лучше просить бекенд вернуть count)
      totalTasks.value = data.length; 
    } else {
      // Если формат пагинации { items: [...], total: 100 }
      tasks.value = data.items || data.data || [];
      totalTasks.value = data.total || data.count || 0;
    }

    // Синхронизация URL с фильтрами (Clean URL)
    updateUrl();

  } catch (err) {
    if (err.name === 'AbortError') {
      // Игнорируем ошибку отмены запроса
      return;
    }
    console.error('Failed to fetch tasks:', err);
    error.value = 'Не удалось загрузить задачи. Попробуйте позже.';
  } finally {
    isLoading.value = false;
  }
};

// --- Helpers ---
const updateUrl = () => {
  router.replace({
    query: {
      ...filters,
      page: pagination.page > 1 ? pagination.page : undefined, // Не пишем page=1 в URL для чистоты
    }
  });
};

const handlePageChange = (newPage) => {
  pagination.page = newPage;
  fetchTasks();
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

// --- Watchers ---

// Следим за фильтрами (кроме поиска, для него отдельная логика с debounce)
watch(
  () => [filters.category, filters.difficulty],
  () => {
    pagination.page = 1; // Сброс на первую страницу при смене фильтров
    fetchTasks();
  }
);

// Специальный вотчер для поиска с Debounce (задержка ввода)
watch(
  () => filters.search,
  (newVal) => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      pagination.page = 1;
      fetchTasks();
    }, 400); // Ждем 400мс после последнего нажатия
  }
);

// --- Lifecycle ---
onMounted(() => {
  fetchTasks();
});

onUnmounted(() => {
  if (abortController) abortController.abort();
  clearTimeout(searchTimeout);
});
</script>
<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8 text-gray-800 dark:text-white">Все задачи</h1>

    <div class="bg-white dark:bg-gray-800 p-4 rounded-lg shadow mb-6 grid gap-4 md:grid-cols-4 items-end">
      
      <div class="col-span-1 md:col-span-2">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Поиск</label>
        <input 
          v-model="filters.search"
          type="text" 
          placeholder="Название задачи или тег..." 
          class="w-full px-4 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-indigo-500 outline-none transition"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Категория</label>
        <select 
          v-model="filters.category" 
          class="w-full px-4 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-indigo-500 outline-none"
        >
          <option value="">Все категории</option>
          <option 
            v-for="cat in constantsStore.TASK_CATEGORIES" 
            :key="cat.value || cat" 
            :value="cat.value || cat"
          >
            {{ cat.label || cat }}
          </option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Сложность</label>
        <select 
          v-model="filters.difficulty"
          class="w-full px-4 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-indigo-500 outline-none"
        >
          <option value="">Любая сложность</option>
          <option 
            v-for="diff in constantsStore.TASK_DIFFICULTIES" 
            :key="diff.value || diff" 
            :value="diff.value || diff"
          >
            {{ diff.label || diff }}
          </option>
        </select>
      </div>
    </div>

    <div v-if="error" class="bg-red-100 text-red-700 p-4 rounded mb-6">
      {{ error }}
    </div>

    <div v-if="isLoading && !tasks.length" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="task in tasks" 
        :key="task.id" 
        class="bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-lg transition duration-300 p-6 flex flex-col"
      >
        <div class="flex justify-between items-start mb-4">
          <span 
            class="px-2 py-1 text-xs font-semibold rounded bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
          >
            {{ task.category }}
          </span>
          <span 
            class="text-sm font-medium"
            :class="{
              'text-green-500': task.difficulty === 'Easy',
              'text-yellow-500': task.difficulty === 'Medium',
              'text-red-500': task.difficulty === 'Hard'
            }"
          >
            {{ task.difficulty }}
          </span>
        </div>
        
        <h3 class="text-xl font-bold mb-2 text-gray-900 dark:text-white">{{ task.title }}</h3>
        <p class="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-3 flex-grow">
          {{ task.description || 'Нет описания' }}
        </p>

        <router-link 
          :to="`/tasks/${task.id}`" 
          class="mt-auto block text-center w-full py-2 px-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded transition"
        >
          Решить задачу
        </router-link>
      </div>
    </div>

    <div v-if="!isLoading && tasks.length === 0 && !error" class="text-center py-12 text-gray-500">
      Задачи не найдены. Попробуйте изменить параметры поиска.
    </div>

    <div v-if="tasks.length && !isLoading" class="mt-8 flex justify-center items-center gap-4">
      <button 
        :disabled="pagination.page === 1"
        @click="handlePageChange(pagination.page - 1)"
        class="px-4 py-2 bg-white dark:bg-gray-800 border rounded disabled:opacity-50 hover:bg-gray-50 dark:hover:bg-gray-700 transition"
      >
        Назад
      </button>
      <span class="text-gray-700 dark:text-gray-300">
        Страница {{ pagination.page }}
      </span>
      <button 
        :disabled="tasks.length < pagination.limit" 
        @click="handlePageChange(pagination.page + 1)"
        class="px-4 py-2 bg-white dark:bg-gray-800 border rounded disabled:opacity-50 hover:bg-gray-50 dark:hover:bg-gray-700 transition"
      >
        Вперед
      </button>
    </div>
  </div>
</template>

<style scoped>
/* Scoped styles if needed, but we rely on Tailwind */
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>