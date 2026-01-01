<script>
import axios from 'axios'
import router from '../router/index.js'
export default {
  name: "RegisterView",
  data(){
    return {
      regUsername:'',
      regEmail:'',
      regPassword:'',
      regPasswordRepeat:''
    }
  },
  methods:{
    async register(){
      if (this.regPassword===this.regPasswordRepeat) {
        try {
          const response = await axios.post('http://127.0.0.1:8000/auth/register', {
            username: this.regUsername,
            email: this.regEmail,
            password: this.regPassword,
            password_repeat: this.regPasswordRepeat
          });
          console.log('Register succes' + response.data)} catch(err){alert(err)}
          router.push('/auth')
      }else{
        alert('Password is incorrect')
      }
    }
  }
}
</script>

<template>
  <div class="register">
    <h1>Registration</h1>
    <form @submit.prevent="register">
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
      </div>
      <div>
        <label for="regPasswordRepeat">repeat password:</label>
        <input type="text" id="regPasswordRepeat" v-model="regPasswordRepeat">
      </div>
      <button type="submit">reg in</button>
    </form>
  </div>
</template>

<style scoped>

</style>
