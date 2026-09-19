<script setup>
import { computed } from 'vue'

const props = defineProps({
  domains: { type: Array, required: true },
})
const filters = defineModel('filters', { required: true })

const availableYears = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]

const activeFilterCount = computed(() => {
  let count = 0
  if (filters.value.search) count++
  if (filters.value.domain) count++
  if (filters.value.yearFrom) count++
  if (filters.value.yearTo) count++
  return count
})

function clear() {
  filters.value = { domain: '', yearFrom: '', yearTo: '', search: '' }
}

function clearSearch() {
  filters.value.search = ''
}
</script>

<template>
  <div class="search-panel-container">
    <div class="search-panel">
      <!-- Search Input with Icon -->
      <div class="search-input-wrapper">
        <span class="search-icon">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.3-4.3" />
          </svg>
        </span>
        <input
          v-model="filters.search"
          type="text"
          placeholder="Search patent title, assignee or keyword (e.g. transformer, solid-state, crisp)…"
        />
        <button
          v-if="filters.search"
          type="button"
          class="clear-search-btn"
          title="Clear search"
          @click="clearSearch"
        >
          ✕
        </button>
      </div>

      <!-- Domain Selector -->
      <select v-model="filters.domain">
        <option value="">All domains (5)</option>
        <option v-for="d in domains" :key="d" :value="d">{{ d }}</option>
      </select>

      <!-- Year Range -->
      <select v-model="filters.yearFrom">
        <option value="">From year (Any)</option>
        <option v-for="y in availableYears" :key="'from-' + y" :value="y">
          From: {{ y }}
        </option>
      </select>

      <select v-model="filters.yearTo">
        <option value="">To year (Any)</option>
        <option v-for="y in availableYears.slice().reverse()" :key="'to-' + y" :value="y">
          To: {{ y }}
        </option>
      </select>

      <!-- Reset / Clear Button -->
      <button
        type="button"
        class="btn-reset"
        :disabled="activeFilterCount === 0"
        :style="{ opacity: activeFilterCount === 0 ? '0.4' : '1', cursor: activeFilterCount === 0 ? 'not-allowed' : 'pointer' }"
        @click="clear"
      >
        Reset {{ activeFilterCount > 0 ? `(${activeFilterCount})` : '' }}
      </button>
    </div>
  </div>
</template>
