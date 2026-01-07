<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const loading = ref(true)
const profile = ref(null)
const error = ref(null)
const fileInput = ref(null) // Ссылка на скрытый инпут для выбора файла

// --- ЛОГИКА РАНГОВ ---
const getRankInfo = (elo) => {
  if (elo < 1200) return { name: 'Новичок', color: 'text-slate-500', bg: 'bg-slate-100', next: 1200 }
  if (elo < 1500) return { name: 'Ученик', color: 'text-green-600', bg: 'bg-green-50', next: 1500 }
  if (elo < 1800) return { name: 'Специалист', color: 'text-blue-600', bg: 'bg-blue-50', next: 1800 }
  if (elo < 2200) return { name: 'Мастер', color: 'text-purple-600', bg: 'bg-purple-50', next: 2200 }
  return { name: 'Легенда', color: 'text-amber-500', bg: 'bg-amber-50', next: 3000 }
}

const rank = computed(() => {
  if (!profile.value) return {}
  return getRankInfo(profile.value.user.rating)
})

const progressToNextRank = computed(() => {
  if (!profile.value) return 0
  const currentElo = profile.value.user.rating
  const { next } = getRankInfo(currentElo)
  const percent = Math.min((currentElo / next) * 100, 100)
  return percent
})

// --- ЛОГИКА АВАТАРКИ ---
const triggerAvatarUpload = () => {
  fileInput.value.click() // Симулируем клик по скрытому инпуту
}

const handleFileChange = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  const formData = new FormData()
  formData.append('file', file)

  try {
    const token = localStorage.getItem('user-token')
    const response = await axios.post('http://127.0.0.1:8000/profile/avatar', formData, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'multipart/form-data'
      }
    })

    // Обновляем ссылку на аватар в текущем состоянии профиля
    profile.value.user.avatar_url = response.data.url
  } catch (err) {
    console.error('Ошибка загрузки аватара:', err)
    alert('Не удалось загрузить изображение')
  }
}

// --- API ---
const fetchProfile = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('user-token')
    if (!token) {
      router.push('/auth')
      return
    }

    const response = await axios.get('http://127.0.0.1:8000/profile/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    profile.value = response.data
  } catch (err) {
    console.error('Ошибка профиля:', err)
    error.value = 'Не удалось загрузить профиль'
  } finally {
    setTimeout(() => { loading.value = false }, 400)
  }
}

const logout = () => {
  if(confirm('Вы уверены, что хотите выйти?')) {
    localStorage.removeItem('user-token')
    router.push('/')
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('ru-RU', {
    month: 'long', year: 'numeric'
  })
}

onMounted(() => {
  fetchProfile()
})
</script>

<template>
  <div class="min-h-screen bg-slate-50 py-12 px-6 font-sans">

    <div v-if="loading" class="max-w-5xl mx-auto space-y-8 animate-pulse">
      <div class="bg-slate-200 h-64 rounded-[2.5rem]"></div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-slate-200 h-40 rounded-[2rem]"></div>
        <div class="bg-slate-200 h-40 rounded-[2rem]"></div>
        <div class="bg-slate-200 h-40 rounded-[2rem]"></div>
      </div>
    </div>

    <div v-else-if="profile" class="max-w-5xl mx-auto space-y-8">

      <div class="bg-white rounded-[2.5rem] p-8 md:p-12 shadow-2xl shadow-slate-200/50 border border-slate-100 relative overflow-hidden group">
        <div class="absolute top-0 right-0 w-64 h-64 bg-indigo-50 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 opacity-50 group-hover:opacity-100 transition-opacity duration-700"></div>

        <div class="relative z-10 flex flex-col md:flex-row items-center gap-8 md:gap-12 text-center md:text-left">

          <div class="relative shrink-0 group cursor-pointer" @click="triggerAvatarUpload">
            <input
              type="file"
              ref="fileInput"
              class="hidden"
              accept="image/*"
              @change="handleFileChange"
            >
            <div class="w-32 h-32 md:w-40 md:h-40 bg-indigo-600 rounded-[2.5rem] flex items-center justify-center text-white text-5xl font-black shadow-2xl shadow-indigo-200 rotate-3 group-hover:rotate-0 transition-all duration-500 overflow-hidden relative">
              <img
                v-if="profile.user.avatar_url"
                :src="`http://127.0.0.1:8000${profile.user.avatar_url}`"
                class="w-full h-full object-cover"
                alt="Avatar"
              />
              <span v-else>{{ profile.user.username.charAt(0).toUpperCase() }}</span>

              <div class="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                <span class="text-2xl">📷</span>
              </div>
            </div>
            <div class="absolute -bottom-2 -right-2 bg-emerald-500 border-4 border-white w-8 h-8 rounded-full shadow-lg"></div>
          </div>

          <div class="flex-1 space-y-2">
            <div class="flex flex-col md:flex-row items-center gap-3">
              <h1 class="text-3xl md:text-4xl font-black text-slate-900 tracking-tight">
                {{ profile.user.username }}
              </h1>
              <span
                class="px-3 py-1 rounded-full text-xs font-black uppercase tracking-widest border"
                :class="[rank.bg, rank.color, `border-${rank.color.split('-')[1]}-100`]"
              >
                {{ rank.name }}
              </span>
            </div>

            <p class="text-slate-500 font-medium flex items-center justify-center md:justify-start gap-2">
              <span>📧 {{ profile.user.email }}</span>
              <span class="w-1 h-1 bg-slate-300 rounded-full"></span>
              <span>В клубе с {{ formatDate(profile.user.created_at) }}</span>
            </p>

            <div class="pt-4 max-w-sm mx-auto md:mx-0">
              <div class="flex justify-between text-xs font-bold text-slate-400 mb-1">
                <span>Рейтинг: {{ profile.user.rating }}</span>
                <span>Следующий ранг: {{ rank.next }}</span>
              </div>
              <div class="h-3 w-full bg-slate-100 rounded-full overflow-hidden">
                <div
                  class="h-full bg-indigo-500 rounded-full transition-all duration-1000 ease-out"
                  :style="{ width: `${progressToNextRank}%` }"
                ></div>
              </div>
            </div>
          </div>

          <div class="flex flex-col gap-3 min-w-[140px]">
            <button @click="triggerAvatarUpload" class="px-6 py-3 bg-slate-900 text-white font-bold rounded-2xl shadow-lg hover:bg-slate-800 transition-all active:scale-95">
              📷 Сменить фото
            </button>
            <button
              @click="logout"
              class="px-6 py-3 bg-white text-red-500 border border-red-100 font-bold rounded-2xl hover:bg-red-50 transition-all active:scale-95"
            >
              🚪 Выйти
            </button>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-xl shadow-slate-200/40 hover:-translate-y-1 transition-transform duration-300">
          <div class="flex items-center justify-between mb-6">
            <div class="w-12 h-12 rounded-2xl bg-indigo-50 flex items-center justify-center text-2xl">📈</div>
            <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Активность</span>
          </div>
          <div class="space-y-5">
            <div>
              <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Задач решено</p>
              <p class="text-4xl font-black text-slate-900 tracking-tight">{{ profile.stats.correct_attempts }}</p>
            </div>
            <div class="pt-4 border-t border-slate-50">
              <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Всего попыток</p>
              <p class="text-2xl font-black text-slate-700 tracking-tight">{{ profile.stats.total_attempts }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-xl shadow-slate-200/40 hover:-translate-y-1 transition-transform duration-300">
          <div class="flex items-center justify-between mb-6">
            <div class="w-12 h-12 rounded-2xl bg-emerald-50 flex items-center justify-center text-2xl">🎯</div>
            <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Точность</span>
          </div>
          <div class="space-y-2">
            <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Процент успеха</p>
            <p class="text-4xl font-black text-emerald-600 tracking-tight">{{ profile.stats.success_rate }}%</p>
            <p class="text-xs font-bold text-slate-400 pt-2">эффективность решений</p>
          </div>
        </div>

        <div class="bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-xl shadow-slate-200/40 hover:-translate-y-1 transition-transform duration-300">
          <div class="flex items-center justify-between mb-6">
            <div class="w-12 h-12 rounded-2xl bg-amber-50 flex items-center justify-center text-2xl">🏆</div>
            <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Мастерство</span>
          </div>
          <div class="space-y-2">
            <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Рейтинг ELO</p>
            <p class="text-4xl font-black text-amber-500 tracking-tight">{{ profile.user.rating }}</p>
            <p class="text-xs font-bold text-slate-400 pt-2">сила твоего аккаунта</p>
          </div>
        </div>
      </div>

    </div>

    <div v-else-if="error" class="text-center py-20">
      <div class="text-4xl mb-4">😕</div>
      <h3 class="text-xl font-bold text-slate-900">{{ error }}</h3>
      <button @click="fetchProfile" class="mt-4 px-6 py-2 bg-indigo-600 text-white rounded-xl font-bold">Попробовать снова</button>
    </div>

  </div>
</template>
