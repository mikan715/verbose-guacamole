<script setup lang="ts">
import { ref } from "vue";
import { useDataStore } from "../stores/dataStore";

const dataStore = useDataStore();

function addUser() {
  dataStore.addNewUser(dataStore.newUser);
}
</script>

<template>
  <div>
    <input
      type="text"
      placeholder="Gib deinen Usernamen ein"
      class="input input-bordered w-full max-w-xs"
      v-model="dataStore.newUser"
    />
    <button class="btn btn-primary" @click="addUser()">Add new user</button>
  </div>
</template>
