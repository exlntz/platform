<script>
import axios from 'axios'

export default {
  name: 'AuthComponent',

  data(){
    return {
      regUsername: '',
      regEmail: '',
      regPassword: '',
      regPasswordRepeat:'',
      loginUsername: '',
      loginEmail: '',
      loginPassword: ''

    }
  },
  methods: {
    async register(){
      const response = await axios.post('http://127.0.0.1:8000/auth/register',{
        username: this.regUsername,
        email: this.regEmail,
        password: this.regPassword,
        password_repeat: this.regPasswordRepeat,
      });
      console.log('reg success' + response.data);}
  }
}

</script>

<template>
  <div>
    <h2>registr</h2>
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


  <div>
    <h2>login</h2>
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
  </div>
</template>

<style scoped>

</style>