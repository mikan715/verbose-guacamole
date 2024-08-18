<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useDataStore } from "../stores/dataStore";
import { RouterView, useRouter } from "vue-router";

const dataStore = useDataStore();
const router = useRouter();
const modalRef = ref<null | HTMLDialogElement>(null);

onMounted(() => {
  loadData();
});

const loadData = async () => {
  await dataStore.fetchData();
  console.log("load data");
};

function openModal(value, quote) {
  dataStore.oddValue = value;
  dataStore.oddQuote = quote;
  if (modalRef.value) {
    modalRef.value.showModal();
  }
}
function wetteSetzen() {
  /* Kontostand berechnen */
  const neuerKontostand = dataStore.kontostand - dataStore.wettgeld;
  dataStore.kontostand = neuerKontostand;

  /* Wette speichern */
  if (modalRef.value) {
    modalRef.value.close();
  }
}

function convertTimeReadable(date) {
  const dateObj = new Date(date);
  const day = String(dateObj.getUTCDate()).padStart(2, "0"); // Tag
  const month = String(dateObj.getUTCMonth() + 1).padStart(2, "0"); // Monat (getUTCMonth() gibt 0-basiert zurück)
  const year = dateObj.getUTCFullYear(); // Jahr
  const hours = String(dateObj.getUTCHours()).padStart(2, "0"); // Stunden
  const minutes = String(dateObj.getUTCMinutes()).padStart(2, "0"); // Minuten
  const seconds = String(dateObj.getUTCSeconds()).padStart(2, "0"); // Sekunden
  const readableDate = `${day}.${month}.${year} ${hours}:${minutes} Uhr`;

  return readableDate;
}
</script>

<template>
  <div class="flex flex-row gap-2">
    <button class="btn btn-secondary" @click="checkBets()">Check bets</button>
    <button class="btn btn-secondary" @click="showBets()">Show bets</button>
    <button class="btn btn-tertiary" @click="router.push({ name: 'addUser' })">
      Add new user
    </button>
    <div>Kontostand: {{ dataStore.kontostand }}</div>
  </div>

  <div class="flex flex-row flex-wrap m-8">
    <div
      v-for="item in dataStore.data"
      class="card bg-neutral-700 shadow-xl m-2 p-2"
    >
      <h2 class="card-title">{{ item.fixture.id }}</h2>
      <p>{{ item.league.round }}</p>
      <p>{{ convertTimeReadable(item.fixture.date) }}</p>
      <div class="card-body">
        <div>
          <h3>{{ item.teams.home.name }}</h3>
          <h4>{{ item.goals.home }}</h4>

          <img
            class="h-8"
            :src="item.teams.home.logo"
            alt="image description"
          />
        </div>
        <div>
          <h3>{{ item.teams.away.name }}</h3>
          <h4>{{ item.goals.away }}</h4>
          <img
            class="h-8"
            :src="item.teams.away.logo"
            alt="image description"
          />
        </div>
      </div>
      <div v-for="bets in item.bookmakers">
        <div v-for="odds in bets.bets" class="card-actions">
          <div v-for="item in odds.values">
            <p>{{ item.value }}</p>
            <button
              class="btn btn-primary"
              @click="openModal(item.value, item.odd)"
            >
              {{ item.odd }}
            </button>
          </div>
        </div>
      </div>
    </div>
    <dialog ref="myModal" class="modal">
      <div class="modal-box">
        <h3 class="text-lg font-bold">Hello!</h3>
        <p>Quote: {{ dataStore.oddValue }} {{ dataStore.oddQuote }}</p>
        <p>Kontostand: {{ dataStore.kontostand }}</p>
        <input
          type="text"
          placeholder="dein wettgeld"
          class="input input-bordered w-full max-w-xs"
          v-model="dataStore.wettgeld"
        />
        <form method="dialog">
          <button class="btn" @click="wetteSetzen()">Close</button>
        </form>
      </div>
    </dialog>
  </div>
</template>
