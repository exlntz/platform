import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'

import App from './App.vue'
import router from './router'

import {
  Chart as ChartJS,
  BarElement,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(
  BarElement,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
)

axios.defaults.baseURL = '/api'
const app = createApp(App)




const darkThemeStyles = `
  :root.dark body {
    background-color: #0f172a;
    color: #f1f5f9;
  }

  :root.dark a {
    color: #60a5fa;
  }

  :root.dark a:hover {
    color: #93c5fd;
  }

  :root.dark button {
    transition: background-color 0.2s ease, color 0.2s ease;
  }

  * {
    transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
  }
`

const styleElement = document.createElement('style')
styleElement.textContent = darkThemeStyles
document.head.appendChild(styleElement)


const initTheme = () => {
  const savedTheme = localStorage.getItem('dark-theme')

  if (savedTheme !== null) {
    if (savedTheme === 'true') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  } else {
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      document.documentElement.classList.add('dark')
    }
  }
}


window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
  if (localStorage.getItem('dark-theme') === null) {
    if (e.matches) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }
})

app.use(createPinia())
app.use(router)
app.mount('#app')
