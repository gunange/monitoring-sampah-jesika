<script setup>
import { ref } from 'vue'
import { breakpoints } from '@/config/vue-prime/appPrimeConfig.ts'

const show = ref(false)
const data = ref([])
const message = ref()
const open = (messages, errors) => {
  message.value = messages
  data.value = errors
  show.value = true
}
const close = () => {
  show.value = true
}

defineExpose({ open, close })
</script>

<template>
  <div>
    <Dialog
      v-model:visible="show"
      modal
      :style="{ width: '35vw' }"
      :breakpoints="breakpoints.dialog"
    >
      <template #header>
        <h6 class="text-red-400 flex items-center">
          <i class="pi pi-exclamation-triangle mr-2" />
          <span>{{ message ?? 'Error!!' }}</span>
        </h6>
      </template>

      <div class="text-center">
        <span class="pi pi-exclamation-triangle text-7xl text-red-500" />
        <p class="my-3">{{ data }}</p>
      </div>
    </Dialog>
  </div>
</template>
