<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import toastWidget from '@/widgets/others/toast-widget.vue'
import { useRouter } from 'vue-router'

import { routerStore } from '@/stores/services/router-store'

routerStore().setRouter(useRouter())
</script>

<template>
  <div>
    <RouterView />
    <toastWidget />
  </div>
</template>
