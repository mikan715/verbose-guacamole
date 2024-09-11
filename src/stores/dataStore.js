import { defineStore } from "pinia";
import axios from "axios";

export const useDataStore = defineStore({
  id: "dataStore",
  state: () => ({
    data: [],
    showModal: false,
    kontostand: 100,
    oddValue: "",
    oddQuote: 0,
    wettgeld: 0,
    userName: "",
    newUser: "",
    userData: "",
    item: [],
  }),

  actions: {
    async fetchData() {
      const result = await axios.get("http://127.0.0.1:5000/dashboard");
      this.data = result.data;
    },

    async addNewUser(name) {
      try {
        const response = await axios.post("http://127.0.0.1:5000/addnewuser", {
          name: name,
          balance: 100.0,
          bets: [],
        });
        console.log("User created with ID:", response.data.user_id);
      } catch (error) {
        console.error("Error creating user:", error);
      }
    },

    async login() {
      try {
        const response = await axios.get("http://127.0.0.1:5000/login", {
          params: { username: this.userName },
        });
        console.log(this.userName);
        this.userData = response.data;
        console.log("User created with ID:", this.userData);
      } catch (error) {
        console.error("Error creating user:", error);
      }
    },
    async addBet() {
      console.log(this.userData.name);
      console.log(this.item.fixture.id);
      console.log(this.wettgeld);
      console.log(this.oddQuote);
      console.log(this.oddValue);
      try {
        const response = await axios.post("http://127.0.0.1:5000/add_bet", {
          user_id: "Anne",
          fixture: this.item.fixture.id,
          wettgeld: this.wettgeld,
          odd: this.oddQuote,
          value: this.oddValue,
        });
        this.message = response.data.message; // Erfolgsnachricht anzeigen
      } catch (err) {
        if (err.response && err.response.data) {
          this.message = err.response.data.error; // Fehlermeldung anzeigen
        } else {
          this.message = "Ein Fehler ist aufgetreten";
        }
      }
    },
  },
});
