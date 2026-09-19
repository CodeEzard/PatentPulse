<script setup>
import { onMounted, onBeforeUnmount, watch, ref } from 'vue'
import Chart from 'chart.js/auto'

const props = defineProps({
  points: { type: Array, required: true },
  activeMetric: { type: String, default: 'both' }, // 'both' | 'filings' | 'citations'
})

const canvasRef = ref(null)
let chartInstance = null

function buildChart() {
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
  if (!canvasRef.value || !props.points || props.points.length === 0) {
    return
  }

  const yearlyMap = new Map()
  for (const p of props.points) {
    const existing = yearlyMap.get(p.filing_year) || { filing_count: 0, total_citations: 0 }
    existing.filing_count += p.filing_count
    existing.total_citations += p.total_citations
    yearlyMap.set(p.filing_year, existing)
  }

  const sortedYears = Array.from(yearlyMap.keys()).sort((a, b) => a - b)
  const years = sortedYears
  const filings = sortedYears.map((y) => yearlyMap.get(y).filing_count)
  const citations = sortedYears.map((y) => yearlyMap.get(y).total_citations)

  const ctx = canvasRef.value.getContext('2d')

  // Gradients for line area fills
  const blueGradient = ctx.createLinearGradient(0, 0, 0, 320)
  blueGradient.addColorStop(0, 'rgba(59, 130, 246, 0.28)')
  blueGradient.addColorStop(1, 'rgba(59, 130, 246, 0.01)')

  const amberGradient = ctx.createLinearGradient(0, 0, 0, 320)
  amberGradient.addColorStop(0, 'rgba(245, 158, 11, 0.24)')
  amberGradient.addColorStop(1, 'rgba(245, 158, 11, 0.01)')

  const datasets = []

  if (props.activeMetric === 'both' || props.activeMetric === 'filings') {
    datasets.push({
      label: 'Filings',
      data: filings,
      borderColor: '#3b82f6',
      backgroundColor: blueGradient,
      fill: true,
      borderWidth: 2.5,
      tension: 0.35,
      pointRadius: 4,
      pointHoverRadius: 7,
      pointBackgroundColor: '#3b82f6',
      pointBorderColor: '#ffffff',
      pointBorderWidth: 1.5,
      yAxisID: 'y',
    })
  }

  if (props.activeMetric === 'both' || props.activeMetric === 'citations') {
    datasets.push({
      label: 'Total citations',
      data: citations,
      borderColor: '#f59e0b',
      backgroundColor: amberGradient,
      fill: true,
      borderWidth: 2.5,
      tension: 0.35,
      pointRadius: 4,
      pointHoverRadius: 7,
      pointBackgroundColor: '#f59e0b',
      pointBorderColor: '#ffffff',
      pointBorderWidth: 1.5,
      yAxisID: props.activeMetric === 'both' ? 'y1' : 'y',
    })
  }

  const scales = {
    x: {
      grid: {
        color: 'rgba(255, 255, 255, 0.05)',
      },
      ticks: {
        color: '#94a3b8',
        font: { family: "'Plus Jakarta Sans', sans-serif" },
      },
    },
    y: {
      position: 'left',
      grid: {
        color: 'rgba(255, 255, 255, 0.05)',
      },
      ticks: {
        color: '#94a3b8',
        font: { family: "'Plus Jakarta Sans', sans-serif" },
      },
      title: {
        display: true,
        text: props.activeMetric === 'citations' ? 'Citations' : 'Filings',
        color: '#94a3b8',
        font: { family: "'Plus Jakarta Sans', sans-serif", weight: '600' },
      },
    },
  }

  if (props.activeMetric === 'both') {
    scales.y1 = {
      position: 'right',
      title: {
        display: true,
        text: 'Citations',
        color: '#94a3b8',
        font: { family: "'Plus Jakarta Sans', sans-serif", weight: '600' },
      },
      grid: { drawOnChartArea: false },
      ticks: {
        color: '#94a3b8',
        font: { family: "'Plus Jakarta Sans', sans-serif" },
      },
    }
  }

  chartInstance = new Chart(canvasRef.value, {
    type: 'line',
    data: {
      labels: years,
      datasets,
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: {
          labels: {
            color: '#e2e8f0',
            font: { family: "'Plus Jakarta Sans', sans-serif", weight: '500' },
            usePointStyle: true,
            boxWidth: 8,
          },
        },
        tooltip: {
          backgroundColor: 'rgba(15, 23, 42, 0.95)',
          borderColor: 'rgba(255, 255, 255, 0.12)',
          borderWidth: 1,
          padding: 12,
          boxPadding: 6,
          usePointStyle: true,
          cornerRadius: 8,
          titleFont: { size: 13, weight: 'bold', family: "'Plus Jakarta Sans', sans-serif" },
          bodyFont: { size: 12, family: "'Plus Jakarta Sans', sans-serif" },
          callbacks: {
            title: (items) => `Filing Year: ${items[0].label}`,
          },
        },
      },
      scales,
    },
  })
}

onMounted(buildChart)
watch([() => props.points, () => props.activeMetric], buildChart, { deep: true })
onBeforeUnmount(() => chartInstance && chartInstance.destroy())
</script>

<template>
  <div class="chart-wrap">
    <canvas ref="canvasRef"></canvas>
  </div>
</template>

<style scoped>
.chart-wrap {
  position: relative;
  height: 350px;
  width: 100%;
}
</style>
