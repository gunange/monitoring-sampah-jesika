import { defineStore } from 'pinia'
import { PanitiaController } from '@/controller/users/PanititaController'

export const panitiaStore = defineStore('panitiaStore', {
  state: () => ({
    controller: new PanitiaController(),
  }),
  getters: {
    data() {
      return this.controller.profil.data
    },
  },
  actions: {
    async reset() {
      await this.controller.reset()
      this.$reset()
    },
    async init() {
      await this.controller.init()
    },
  },
})
