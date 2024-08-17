import { createRouter, createWebHistory } from "vue-router";

const DashboardView = () => import("../views/DashboardView.vue");
const AddUserView = () => import("../views/AddUserView.vue");

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "dashboard",
      component: DashboardView,
    },
    {
      path: "/addUser",
      name: "addUser",
      component: AddUserView,
    },
  ],
});

export default router;
