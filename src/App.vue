<script>
import { RouterView, useRouter } from "vue-router";

const router = useRouter();
</script>

<template>
  <div>
    <main @keyup.esc="router.push({ name: 'dashboard' })">
      <RouterView />
    </main>
  </div>
</template>
