<script setup>
import { RouterView } from 'vue-router'
import AppHeader from './components/AppHeader.vue'
import Footer from './components/Footer.vue'
</script>

<template>
  <AppHeader />
  <RouterView />
  <Footer />
</template>

<style>
/* Siempre Poppins */
body {
  font-family: 'Poppins', sans-serif;
  margin: 0;
  padding: 0;
}
</style>
