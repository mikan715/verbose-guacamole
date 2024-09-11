<script setup lang="ts">
import { useDataStore } from "../stores/dataStore";
import { RouterView, useRouter } from "vue-router";

const dataStore = useDataStore();
const router = useRouter();
</script>

<template>
  <div>
    <div>Fixture: {{ dataStore.item.fixture.id }}</div>
    <div>{{ dataStore.item.teams.home.name }}</div>
    <div>{{ dataStore.item.teams.away.name }}</div>
    <div>{{ dataStore.oddQuote }}</div>
    <div>{{ dataStore.oddValue }}</div>
    <div>Aktueller Kontostand: {{ dataStore.kontostand }}</div>
    <div>Wetteinsatz: {{ dataStore.oddValue * dataStore.wettgeld }}</div>
    <input
      type="text"
      placeholder="dein wettgeld"
      class="input input-bordered w-full max-w-xs"
      v-model="dataStore.wettgeld"
    />
    <button class="btn btn-primary" @click="dataStore.addBet()">Bet</button>
    <button class="btn" @click="router.push({ name: 'dashboard' })">
      Close
    </button>
  </div>
</template>
