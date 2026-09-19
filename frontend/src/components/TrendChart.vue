<script setup>
import { onMounted, onBeforeUnmount, watch, ref } from 'vue'
import Chart from 'chart.js/auto'

const props = defineProps({
  points: { type: Array, required: true },
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

  chartInstance = new Chart(canvasRef.value, {
    type: 'line',
    data: {
      labels: years,
      datasets: [
        {
          label: 'Filings',
          data: filings,
          borderColor: '#3b7dd8',
          backgroundColor: 'rgba(59,125,216,0.15)',
          tension: 0.3,
          yAxisID: 'y',
        },
        {
          label: 'Total citations',
          data: citations,
          borderColor: '#d88a3b',
          backgroundColor: 'rgba(216,138,59,0.12)',
          tension: 0.3,
          yAxisID: 'y1',
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      scales: {
        y: { position: 'left', title: { display: true, text: 'Filings' } },
        y1: {
          position: 'right',
          title: { display: true, text: 'Citations' },
          grid: { drawOnChartArea: false },
        },
      },
    },
  })
}

onMounted(buildChart)
watch(() => props.points, buildChart, { deep: true })
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
  height: 340px;
  width: 100%;
}
</style>
