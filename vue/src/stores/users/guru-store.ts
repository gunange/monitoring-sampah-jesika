import { defineStore } from 'pinia'
import { GuruController } from '@/controller/users/GuruController'

export const guruStore = defineStore('guruStore', {
  state: () => ({
    controller: new GuruController(),
  }),
  actions: {
    reset() {
      this.controller.reset()
      this.$reset()
    },
  },
})
