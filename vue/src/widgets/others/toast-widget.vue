<template>
  <Toast />
</template>
<script setup>
import { useToast } from 'primevue/usetoast'
import { toastStore } from '@/stores/services/toast-store'

const toast_store = toastStore()
toast_store.setToast(useToast())
</script>
