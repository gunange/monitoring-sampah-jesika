import { defineStore } from 'pinia'

export const authStore = defineStore('authStore', {
  state: () => ({
    isAuth: false,
    user: null,
    token: null,
    proses: {
      sukses: false,
      load: false,
    },
    ganti_password: {
      show: false,
      proses: false,
    },
  }),
  actions: {},
})
