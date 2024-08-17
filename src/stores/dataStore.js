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
  }),

  actions: {
    async fetchData() {
      const result = await axios.get("http://127.0.0.1:5000/");
      this.data = result.data;
    },

    async addNewUser(name) {
      try {
        const response = await axios.post("http://127.0.0.1:5000/addnewuser", {
          name: name,
          balance: 170.0,
        });
        console.log("User created with ID:", response.data.user_id);
      } catch (error) {
        console.error("Error creating user:", error);
      }
    },
  },
});
