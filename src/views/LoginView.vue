<script setup lang="ts">
import { ref } from "vue";
import { useDataStore } from "../stores/dataStore";
import { useRouter } from "vue-router";

const dataStore = useDataStore();
const router = useRouter();

function login() {
  dataStore.login();
  router.push({ name: "dashboard" });
}
</script>

<template>
  <div>
    <input
      type="text"
      placeholder="Gib deinen Usernamen ein"
      class="input input-bordered w-full max-w-xs"
      v-model="dataStore.userName"
    />
    <button class="btn btn-primary" @click="login">Login</button>
  </div>
  <div>
    <button class="btn btn-ghost" @click="router.push({ name: 'addUser' })">
      Neuen Account erstellen
    </button>
  </div>
</template>
