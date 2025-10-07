import { defineStore } from 'pinia'

export const routerStore = defineStore('routerStore', {
  state: () => ({
    _router: null,
  }),
  getters: {
    router() {
      return this._router
    },
  },
  actions: {
    setRouter(data) {
      this._router = data
    },
  },
})
