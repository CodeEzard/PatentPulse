<script setup>
const props = defineProps({
  domains: { type: Array, required: true },
})
const filters = defineModel('filters', { required: true })

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
    <input v-model="filters.yearFrom" type="number" placeholder="Year from" />
    <input v-model="filters.yearTo" type="number" placeholder="Year to" />
    <button type="button" @click="clear">Clear</button>
  </div>
</template>
