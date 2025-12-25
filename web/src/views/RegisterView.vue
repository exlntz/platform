<script>
export default {
  name: "RegisterView"
}
</script>

<template>
  <div class="register">
    <h1>Registration</h1>
    <form @submit.prevent="register"></form>
    <div>
      <label for="regUsername">Username:</label>
      <input type="text" id="regUsername" v-model="regUsername">
    </div>
    <div>
      <label for="regEmail">email:</label>
      <input type="text" id="regEmail" v-model="regEmail">
    </div>
    <div>
      <label for="regPassword">password:</label>
      <input type="text" id="regPassword" v-model="regPassword">
    </div><div>
    <label for="regPasswordRepeat">repeat password:</label>
    <input type="text" id="regPasswordRepeat" v-model="regPasswordRepeat">
  </div>
    <button type="submit">reg in</button>
  </div>

</template>

<style scoped>

</style>
