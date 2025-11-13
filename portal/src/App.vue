<script setup>
import { RouterView } from 'vue-router'
import AppHeader from './components/AppHeader.vue'
</script>

<template>
  <AppHeader />
  <RouterView />
</template>

<style>
/* Siempre Poppins */
body {
  font-family: 'Poppins', sans-serif;
  margin: 0;
  padding: 0;
}
</style>
