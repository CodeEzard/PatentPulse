<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="app-shell">
    <header class="app-header">
      <RouterLink to="/" class="brand">
        <span class="brand-mark">PP</span>
        <span class="brand-name">PatentPulse</span>
      </RouterLink>

      <div class="header-right">
        <nav class="nav-links">
          <RouterLink to="/" active-class="active">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 3v18h18" />
              <path d="m19 9-5 5-4-4-3 3" />
            </svg>
            Dashboard
          </RouterLink>
          <RouterLink to="/explore" active-class="active">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.3-4.3" />
            </svg>
            Explorer
          </RouterLink>
        </nav>

        <div class="live-indicator" title="Repository updated through 2026">
          <span class="pulse-dot"></span>
          <span>166 Patents Indexed</span>
        </div>
      </div>
    </header>

    <main class="app-main">
      <RouterView />
    </main>

    <footer class="app-footer">
      <div>
        <span>PatentPulse</span> · Technology Trend Intelligence &amp; Prior Art Analytics
      </div>
      <div>
        <span>Coverage: 2018–2026 · USPTO CPC Classifications</span>
      </div>
    </footer>
  </div>
</template>
