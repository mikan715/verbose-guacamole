<template>
  <div class="flex flex-row gap-2">
    <button class="btn btn-secondary" @click="checkBets()">Check bets</button>
    <button class="btn btn-secondary" @click="showBets()">Show bets</button>
    <div>Kontostand: {{ kontostand }}</div>
    <div>hi</div>
  </div>

  <div class="flex flex-row flex-wrap m-8">
    <div
      v-for="item in jsonData.response"
      class="card bg-neutral-700 shadow-xl m-2 p-2"
    >
      <h2 class="card-title">{{ item.fixture.id }}</h2>
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
      <div v-for="bets in item.bets" class="card-actions justify-end">
        <div v-for="odd in bets.values">
          <p>{{ odd.value }}</p>
          <button
            class="btn btn-primary"
            @click="openModal(odd.value, odd.odd)"
          >
            {{ odd.odd }}
          </button>
        </div>
      </div>
    </div>
    <dialog ref="myModal" class="modal">
      <div class="modal-box">
        <h3 class="text-lg font-bold">Hello!</h3>
        <p>Quote: {{ oddValue }} {{ oddQuote }}</p>
        <p>Kontostand: {{ kontostand }}</p>
        <input
          type="text"
          placeholder="dein wettgeld"
          class="input input-bordered w-full max-w-xs"
          v-model="wettgeld"
        />
        <form method="dialog">
          <!-- if there is a button in form, it will close the modal -->
          <button class="btn" @click="wetteSetzen()">Close</button>
        </form>
      </div>
    </dialog>
  </div>
</template>
