<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <header class="app-header">
    <nav>
      <RouterLink to="/">主页</RouterLink>
      <RouterLink to="/chat">智慧助手</RouterLink>
      
    </nav>
  </header>
  <main class="app-content">
    <RouterView />
  </main>
</template>

<style scoped>
.app-header {
  background-color: #f8f9fa;
  padding: 0 2rem;
  border-bottom: 1px solid #dee2e6;
  box-shadow: 0 2px 4px rgba(0,0,0,.08);
}
nav {
  display: flex;
  align-items: center;
  height: 4rem;
}
nav a {
  color: #495057;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}
nav a.router-link-exact-active {
  color: #0056b3;
  font-weight: bold;
  background-color: #e9ecef;
}
nav a:hover {
  background-color: #e9ecef;
}
.app-content {
  padding: 1rem;
}
</style>
