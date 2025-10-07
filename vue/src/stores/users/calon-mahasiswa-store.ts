import { defineStore } from 'pinia'
import { CalonMahasiswaController } from '@/controller/users/CalonMahasiswaController'

export const calonMahasiswaStore = defineStore('calonMahasiswaStore', {
  state: () => ({
    controller: new CalonMahasiswaController(),
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
