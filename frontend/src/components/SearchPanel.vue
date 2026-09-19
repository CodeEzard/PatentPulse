<script setup>
const props = defineProps({
  domains: { type: Array, required: true },
})
const filters = defineModel('filters', { required: true })

const availableYears = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]

function clear() {
  filters.value = { domain: '', yearFrom: '', yearTo: '', search: '' }
}
</script>

<template>
  <div class="search-panel">
    <input
      v-model="filters.search"
      type="text"
      placeholder="Search title, assignee or keyword…"
    />
    <select v-model="filters.domain">
      <option value="">All domains</option>
      <option v-for="d in domains" :key="d" :value="d">{{ d }}</option>
    </select>
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
    <button type="button" @click="clear">Clear</button>
  </div>
</template>
