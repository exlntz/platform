<script>
export default {
  name: "AuthView"
}
</script>

<template>
  <div class="reg">
    <h1>Auth Page</h1>
    <form @submit.prevent="login"></form>
    <div>
      <label for="loginEmail">email:</label>
      <input type="text" id="loginEmail" v-model="loginEmail">
    </div>
    <div>
      <label for="loginPassword">email:</label>
      <input type="text" id="loginPassword" v-model="loginPassword">
    </div>
    <button type="submit">login</button>
    <router-link to="/auth/register">Reg now</router-link>
  </div>
</template>

<style scoped>

</style>
