import { defineStore } from 'pinia'
import { ref } from 'vue'

export const dashboardStore = defineStore('dashboardStore', {
  state: () => {
    return {
      sidebarActive: true,
    }
  },
})
