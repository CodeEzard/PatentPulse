<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="app-shell">
    <header class="app-header">
      <div class="brand">
        <span class="brand-mark">PP</span>
        <span class="brand-name">PatentPulse</span>
      </div>
      <nav>
        <RouterLink to="/" active-class="active">Dashboard</RouterLink>
        <RouterLink to="/explore" active-class="active">Explorer</RouterLink>
      </nav>
    </header>
    <main class="app-main">
      <RouterView />
    </main>
    <footer class="app-footer">
      PatentPulse · Technology Trend Analytics
    </footer>
  </div>
</template>
