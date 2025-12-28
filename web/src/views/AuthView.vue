<script>
import axios from "axios";

export default {
  name: "AuthView",
  data() {
    return {
      loginUsername: '',
      loginPassword: '',
    }
  },
  methods: {
    async login() {
      try {
        // Создаем объект для передачи параметров формы
        const params = new URLSearchParams();
        params.append('username', this.loginUsername);
        params.append('password', this.loginPassword);

        const response = await axios.post('http://127.0.0.1:8000/auth/login', params);

        console.log('Log in success', response.data);
        const token = response.data.access_token;
        localStorage.setItem('user-token', token);

        // Перенаправляем пользователя на главную или в личный кабинет
        this.$router.push('/profile');
      } catch(err) {
        alert("Ошибка авторизации: " + err);
      }
    }
  }
}

</script>

<template>
  <div class="reg">
    <h1>Auth Page</h1>
    <form @submit.prevent="login">
    <div>
      <label for="loginUsername">Username:</label>
      <input
        type="text"
        id="loginUsername"
        v-model="loginUsername"
        required
      >
    </div>
    <div>
      <label for="loginPassword">Пассворд:</label>
      <input
        type="password"
        id="loginPassword"
        v-model="loginPassword"
        required
      >
    </div>
    <button type="submit">login</button>
    </form>
    <router-link to="/auth/register">Reg now</router-link>
  </div>
</template>

<style scoped>

</style>
