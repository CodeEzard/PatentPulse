<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import api from '../services/api'
import SearchPanel from '../components/SearchPanel.vue'

const domains = ref([])
const results = ref([])
const count = ref(0)
const page = ref(1)
const pageSize = 25
const loading = ref(true)
const error = ref(null)
const filters = ref({ domain: '', yearFrom: '', yearTo: '', search: '' })

let debounceHandle = null

const totalPages = computed(() => Math.ceil(count.value / pageSize) || 1)

async function loadDomains() {
  try {
    domains.value = await api.getDomains()
  } catch (e) {
    // Non-fatal, domain dropdown will remain empty or default
  }
}

async function loadResults() {
  loading.value = true
  error.value = null
  const params = { page: page.value }
  if (filters.value.domain) params.domain = filters.value.domain
  if (filters.value.yearFrom) params.year_from = filters.value.yearFrom
  if (filters.value.yearTo) params.year_to = filters.value.yearTo
  if (filters.value.search) params.search = filters.value.search

  try {
    const data = await api.getPatents(params)
    results.value = data.results ?? data
    count.value = data.count ?? results.value.length
  } catch (e) {
    error.value = 'Could not load patents. Is the API running?'
  } finally {
    loading.value = false
  }
}

function goToPage(newPage) {
  if (newPage >= 1 && newPage <= totalPages.value) {
    page.value = newPage
    loadResults()
  }
}

onMounted(async () => {
  await loadDomains()
  await loadResults()
})

watch(
  filters,
  () => {
    page.value = 1
    clearTimeout(debounceHandle)
    debounceHandle = setTimeout(loadResults, 300)
  },
  { deep: true }
)
</script>

<template>
  <section>
    <h1>Explore patents</h1>
    <SearchPanel :domains="domains" v-model:filters="filters" />

    <div v-if="error" class="error-banner">{{ error }}</div>

    <div v-else>
      <p class="result-count">{{ count }} result{{ count === 1 ? '' : 's' }}</p>

      <table v-if="!loading && results.length">
        <thead>
          <tr>
            <th>Title</th>
            <th>Domain</th>
            <th>Assignee</th>
            <th>Year</th>
            <th>Citations</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in results" :key="p.id">
            <td>{{ p.title }}</td>
            <td><span class="domain-tag">{{ p.technology_domain }}</span></td>
            <td>{{ p.assignee }}</td>
            <td>{{ p.filing_year }}</td>
            <td>{{ p.citation_count }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else-if="!loading">No patents match those filters.</p>
      <p v-else>Loading…</p>

      <div v-if="totalPages > 1" class="pagination">
        <button type="button" :disabled="page <= 1" @click="goToPage(page - 1)">Previous</button>
        <span>Page {{ page }} of {{ totalPages }}</span>
        <button type="button" :disabled="page >= totalPages" @click="goToPage(page + 1)">Next</button>
      </div>
    </div>
  </section>
</template>
