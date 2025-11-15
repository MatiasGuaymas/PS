<template>
  <footer class="footer shadow-lg">
    <div class="container">
      <div class="footer-content">
        <div class="footer-logo">
          <img src="/Logo.jpg" alt="Logo" class="logo" />
          <span class="brand-name">
            <span class="gradient-text-1">Puff</span>
            <span class="gradient-text-2">-</span>
            <span class="gradient-text-3">Tóricos</span>
          </span>
        </div>
        <div class="footer-text">
          <p>&copy; {{ currentYear }} Sitios Históricos. Todos los derechos reservados.</p>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue'

const currentYear = computed(() => new Date().getFullYear())
</script>

<style scoped>
.footer {
  background-color: var(--bg-header-footer);
  color: var(--text-primary);
  padding: 2rem 0;
  margin-top: auto;
  border-top: 1px solid var(--border-color);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.footer-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  text-align: center;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo {
  height: 40px;
  width: auto;
  border-radius: 8px;
}

.brand-name {
  font-size: 1.25rem;
  font-weight: 600;
}

/* Gradiente en el logo (igual que el header) */
.gradient-text-1 {
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.gradient-text-2 {
  background: var(--gradient-secondary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.gradient-text-3 {
  background: var(--gradient-accent);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.footer-text {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.footer-text p {
  margin: 0;
}

@media (min-width: 768px) {
  .footer-content {
    flex-direction: row;
    justify-content: space-between;
  }

  .footer-text {
    text-align: right;
  }
}
</style>