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

const startItem = computed(() => (count.value === 0 ? 0 : (page.value - 1) * pageSize + 1))
const endItem = computed(() => Math.min(page.value * pageSize, count.value))

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
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

function resetFilters() {
  filters.value = { domain: '', yearFrom: '', yearTo: '', search: '' }
}

function getDomainClass(domain) {
  const map = {
    'AI/ML': 'domain-aiml',
    'Biotech': 'domain-biotech',
    'Energy Storage': 'domain-energystorage',
    'IoT': 'domain-iot',
    'Cybersecurity': 'domain-cybersecurity',
  }
  return map[domain] || ''
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
    <div class="panel-header">
      <div>
        <h1>Patent Explorer &amp; Repository</h1>
        <p class="page-subhead">
          Search, cross-examine, and navigate USPTO &amp; international patent specifications across 5 technology sectors.
        </p>
      </div>
    </div>

    <SearchPanel :domains="domains" v-model:filters="filters" />

    <div v-if="error" class="error-banner">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <line x1="12" y1="16" x2="12.01" y2="16" />
      </svg>
      <span>{{ error }}</span>
    </div>

    <div v-else>
      <div class="result-count">
        <span>
          Showing <strong>{{ startItem }}</strong>–<strong>{{ endItem }}</strong> of <strong>{{ count }}</strong> patents
        </span>
        <span v-if="filters.domain || filters.search || filters.yearFrom || filters.yearTo" style="font-size: 0.8rem; color: var(--accent-hover);">
          ● Filters Active
        </span>
      </div>

      <div class="table-card">
        <div class="table-responsive">
          <table>
            <thead>
              <tr>
                <th style="min-width: 320px;">Patent &amp; Technology Tags</th>
                <th style="width: 140px;">Domain</th>
                <th style="width: 180px;">Assignee</th>
                <th style="width: 80px;">Year</th>
                <th style="width: 110px;">Citations</th>
                <th style="width: 80px; text-align: right;">Action</th>
              </tr>
            </thead>

            <!-- Skeleton Loading State -->
            <tbody v-if="loading">
              <tr v-for="i in 5" :key="'skel-' + i" class="skeleton-row">
                <td>
                  <div class="skeleton-box" style="width: 80%; margin-bottom: 0.5rem;"></div>
                  <div class="skeleton-box" style="width: 45%;"></div>
                </td>
                <td><div class="skeleton-box" style="width: 90px;"></div></td>
                <td><div class="skeleton-box" style="width: 120px;"></div></td>
                <td><div class="skeleton-box" style="width: 50px;"></div></td>
                <td><div class="skeleton-box" style="width: 60px;"></div></td>
                <td><div class="skeleton-box" style="width: 40px; margin-left: auto;"></div></td>
              </tr>
            </tbody>

            <!-- Results List -->
            <tbody v-else-if="results.length">
              <tr v-for="p in results" :key="p.id">
                <td>
                  <div class="patent-title-cell">
                    <a
                      :href="p.patent_url || ('https://patents.google.com/?q=' + encodeURIComponent(p.title + ' ' + p.assignee))"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="patent-link"
                      :title="'View full patent document on Google Patents: ' + p.title"
                    >
                      {{ p.title }}
                      <span class="external-icon" aria-hidden="true">↗</span>
                    </a>

                    <div v-if="p.keyword_list && p.keyword_list.length" class="keyword-chips">
                      <span v-for="kw in p.keyword_list" :key="kw" class="kw-tag">
                        {{ kw }}
                      </span>
                    </div>
                  </div>
                </td>

                <td>
                  <span class="domain-tag" :class="getDomainClass(p.technology_domain)">
                    {{ p.technology_domain }}
                  </span>
                </td>

                <td>
                  <span class="assignee-text">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="opacity: 0.6;">
                      <rect width="16" height="20" x="4" y="2" rx="2" ry="2" />
                      <path d="M9 22v-4h6v4" />
                      <path d="M8 6h.01" /><path d="M16 6h.01" /><path d="M8 10h.01" /><path d="M16 10h.01" /><path d="M8 14h.01" /><path d="M16 14h.01" />
                    </svg>
                    {{ p.assignee }}
                  </span>
                </td>

                <td>
                  <span class="year-mono">{{ p.filing_year }}</span>
                </td>

                <td>
                  <span
                    class="citation-badge"
                    :class="{ 'high-impact': p.citation_count >= 100 }"
                    :title="p.citation_count >= 100 ? 'High citation velocity (>100 citations)' : 'Total citations'"
                  >
                    <span v-if="p.citation_count >= 100">⭐</span>
                    {{ p.citation_count }}
                  </span>
                </td>

                <td style="text-align: right;">
                  <a
                    :href="p.patent_url || ('https://patents.google.com/?q=' + encodeURIComponent(p.title + ' ' + p.assignee))"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="pill-btn"
                    style="font-size: 0.75rem; text-decoration: none;"
                    title="View patent document"
                  >
                    Open ↗
                  </a>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Empty State -->
        <div v-if="!loading && !results.length" class="empty-state">
          <div class="empty-icon">🔍</div>
          <div class="empty-title">No patents matched your query</div>
          <div class="empty-desc">
            Try adjusting your search terms, broadening the filing year range, or resetting domain filters.
          </div>
          <button type="button" class="btn-reset" style="padding: 0.5rem 1.2rem;" @click="resetFilters">
            Clear all filters
          </button>
        </div>

        <!-- Pagination Bar -->
        <div v-if="totalPages > 1" class="pagination">
          <div>
            <span>Page <strong style="color: #ffffff;">{{ page }}</strong> of {{ totalPages }}</span>
          </div>

          <div class="pagination-controls">
            <button
              type="button"
              :disabled="page <= 1"
              @click="goToPage(1)"
              title="First page"
            >
              « First
            </button>
            <button
              type="button"
              :disabled="page <= 1"
              @click="goToPage(page - 1)"
            >
              ‹ Previous
            </button>
            <span class="page-indicator">[{{ page }} / {{ totalPages }}]</span>
            <button
              type="button"
              :disabled="page >= totalPages"
              @click="goToPage(page + 1)"
            >
              Next ›
            </button>
            <button
              type="button"
              :disabled="page >= totalPages"
              @click="goToPage(totalPages)"
              title="Last page"
            >
              Last »
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
