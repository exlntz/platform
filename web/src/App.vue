<script setup>
import { RouterLink, RouterView } from 'vue-router'

</script>

<template>
  <header>
      <nav>
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/tasks">Tasks</RouterLink>
        <RouterLink to="/pvp">PvP</RouterLink>
        <RouterLink to="/profile">Profile</RouterLink>
        <RouterLink to="/auth">Auth</RouterLink>
      </nav>
  </header>

  <RouterView />
</template>

<style scoped>

</style>
