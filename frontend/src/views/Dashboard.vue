<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import api from '../services/api'
import TrendChart from '../components/TrendChart.vue'

const domains = ref([])
const selectedDomain = ref('')
const points = ref([])
const loading = ref(true)
const error = ref(null)

async function loadDomains() {
  try {
    domains.value = await api.getDomains()
  } catch (e) {
    // Non-fatal, domain dropdown will remain empty or default
  }
}

async function loadSummary() {
  loading.value = true
  error.value = null
  try {
    points.value = await api.getTrendSummary(selectedDomain.value || null)
  } catch (e) {
    error.value = 'Could not load trend data. Is the API running?'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadDomains()
  await loadSummary()
})

watch(selectedDomain, loadSummary)

const totalFilings = computed(() =>
  points.value.reduce((sum, p) => sum + (p.filing_count || 0), 0)
)
const totalCitations = computed(() =>
  points.value.reduce((sum, p) => sum + (p.total_citations || 0), 0)
)
</script>

<template>
  <section>
    <div class="panel-header">
      <h1>Technology trend dashboard</h1>
      <select v-model="selectedDomain">
        <option value="">All domains</option>
        <option v-for="d in domains" :key="d" :value="d">{{ d }}</option>
      </select>
    </div>

    <div v-if="error" class="error-banner">{{ error }}</div>

    <div v-else>
      <div class="stat-row">
        <div class="stat-card">
          <span class="stat-value">{{ totalFilings }}</span>
          <span class="stat-label">Filings in view</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ totalCitations }}</span>
          <span class="stat-label">Total citations</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ domains.length }}</span>
          <span class="stat-label">Tracked domains</span>
        </div>
      </div>

      <div class="card">
        <h2>Filings &amp; citations by year</h2>
        <p v-if="loading">Loading…</p>
        <TrendChart v-else :points="points" />
      </div>
    </div>
  </section>
</template>
