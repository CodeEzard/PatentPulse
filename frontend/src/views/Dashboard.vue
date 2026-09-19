<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import api from '../services/api'
import TrendChart from '../components/TrendChart.vue'

const domains = ref([])
const selectedDomain = ref('')
const points = ref([])
const activeMetric = ref('both') // 'both' | 'filings' | 'citations'
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
const avgCitationsPerPatent = computed(() =>
  totalFilings.value ? Math.round(totalCitations.value / totalFilings.value) : 0
)

const domainBreakdown = computed(() => {
  if (selectedDomain.value) return []
  const map = {}
  for (const p of points.value) {
    if (!map[p.technology_domain]) {
      map[p.technology_domain] = {
        domain: p.technology_domain,
        filings: 0,
        citations: 0,
      }
    }
    map[p.technology_domain].filings += p.filing_count
    map[p.technology_domain].citations += p.total_citations
  }
  return Object.values(map).sort((a, b) => b.filings - a.filings)
})

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
</script>

<template>
  <section>
    <div class="panel-header">
      <div>
        <h1>Technology Trend Dashboard</h1>
        <p class="page-subhead">
          Velocity, filing distributions, and citation momentum across core innovation sectors (2018–2026).
        </p>
      </div>

      <div class="filter-pills">
        <button
          type="button"
          class="pill-btn"
          :class="{ active: selectedDomain === '' }"
          @click="selectedDomain = ''"
        >
          All Domains
        </button>
        <button
          v-for="d in domains"
          :key="d"
          type="button"
          class="pill-btn"
          :class="{ active: selectedDomain === d }"
          @click="selectedDomain = d"
        >
          {{ d }}
        </button>
      </div>
    </div>

    <div v-if="error" class="error-banner">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <line x1="12" y1="16" x2="12.01" y2="16" />
      </svg>
      <span>{{ error }}</span>
    </div>

    <div v-else>
      <div class="stat-row">
        <div class="stat-card">
          <div class="stat-card-header">
            <span class="stat-label">Filings In View</span>
            <div class="stat-icon" style="color: #60a5fa;">📈</div>
          </div>
          <span class="stat-value">{{ totalFilings }}</span>
          <span class="stat-subtext">Published patent specifications</span>
        </div>

        <div class="stat-card">
          <div class="stat-card-header">
            <span class="stat-label">Total Citations</span>
            <div class="stat-icon" style="color: #fbbf24;">⭐</div>
          </div>
          <span class="stat-value">{{ totalCitations.toLocaleString() }}</span>
          <span class="stat-subtext">Prior art &amp; forward citations</span>
        </div>

        <div class="stat-card">
          <div class="stat-card-header">
            <span class="stat-label">Avg Citations / Doc</span>
            <div class="stat-icon" style="color: #34d399;">⚡</div>
          </div>
          <span class="stat-value">{{ avgCitationsPerPatent }}</span>
          <span class="stat-subtext">Citation velocity indicator</span>
        </div>

        <div class="stat-card">
          <div class="stat-card-header">
            <span class="stat-label">Domain Scope</span>
            <div class="stat-icon" style="color: #a78bfa;">🌐</div>
          </div>
          <span class="stat-value">{{ selectedDomain ? 1 : domains.length }}</span>
          <span class="stat-subtext">{{ selectedDomain ? selectedDomain : 'High-growth tech clusters' }}</span>
        </div>
      </div>

      <div class="card">
        <div class="card-header-flex">
          <div>
            <h2>Filings &amp; Citation Momentum</h2>
            <span class="stat-subtext">Annual trajectories spanning 2018 through 2026</span>
          </div>
          <div class="filter-pills">
            <button
              type="button"
              class="pill-btn"
              :class="{ active: activeMetric === 'both' }"
              @click="activeMetric = 'both'"
            >
              Both Metrics
            </button>
            <button
              type="button"
              class="pill-btn"
              :class="{ active: activeMetric === 'filings' }"
              @click="activeMetric = 'filings'"
            >
              Filings Only
            </button>
            <button
              type="button"
              class="pill-btn"
              :class="{ active: activeMetric === 'citations' }"
              @click="activeMetric = 'citations'"
            >
              Citations Only
            </button>
          </div>
        </div>

        <div v-if="loading" style="height: 340px; display: flex; align-items: center; justify-content: center; color: var(--text-muted);">
          <div style="text-align: center;">
            <div class="pulse-dot" style="margin: 0 auto 0.75rem auto; width: 12px; height: 12px;"></div>
            <span>Aggregating patent trend metrics…</span>
          </div>
        </div>
        <TrendChart v-else :points="points" :active-metric="activeMetric" />
      </div>

      <!-- Domain Breakdown Cards when viewing All Domains -->
      <div v-if="!selectedDomain && domainBreakdown.length && !loading" style="margin-top: 2rem;">
        <div style="margin-bottom: 1rem;">
          <h2 style="font-size: 1.15rem; font-weight: 700; color: #ffffff; margin: 0 0 0.25rem 0;">
            Domain Sector Comparison
          </h2>
          <span class="stat-subtext">Click any domain to focus the trajectory and inspection view</span>
        </div>

        <div class="domain-matrix-grid">
          <div
            v-for="item in domainBreakdown"
            :key="item.domain"
            class="domain-matrix-card"
            @click="selectedDomain = item.domain"
          >
            <div class="domain-matrix-header">
              <span class="domain-tag" :class="getDomainClass(item.domain)">
                {{ item.domain }}
              </span>
              <span style="font-size: 0.75rem; color: var(--accent-hover);">Focus ↗</span>
            </div>
            <div class="domain-matrix-stats">
              <div>
                <span>Filings: </span>
                <strong>{{ item.filings }}</strong>
              </div>
              <div>
                <span>Citations: </span>
                <strong>{{ item.citations.toLocaleString() }}</strong>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
