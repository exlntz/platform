<script setup>
import { defineAsyncComponent, onMounted } from 'vue'
import { useChartsStore } from '@/pinia/charts.store'
import { storeToRefs } from 'pinia'

const Pie = defineAsyncComponent(() =>
  import('vue-chartjs').then(m => m.Pie)
)

const Line = defineAsyncComponent(() =>
  import('vue-chartjs').then(m => m.Line)
)

const chartsStore = useChartsStore()
const { pieData, lineData, ready } = storeToRefs(chartsStore)

onMounted(() => {
  // lazy render графиков
  setTimeout(() => {
    chartsStore.enableCharts()
  }, 300)
})

const options = {
  responsive: true,
  animation: false,
  maintainAspectRatio: false
}
</script>

<template>
  <div class="stats-grid">
    <div class="stat-card">
      <p class="stat-label">Распределение решений</p>
      <div style="height: 220px">
        <Pie v-if="ready && pieData" :data="pieData" :options="options" />
      </div>
    </div>

    <div class="stat-card">
      <p class="stat-label">Рост рейтинга</p>
      <div style="height: 220px">
        <Line v-if="ready && lineData" :data="lineData" :options="options" />
      </div>
    </div>
  </div>
</template>
