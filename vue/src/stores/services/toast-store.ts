import { defineStore } from 'pinia'

export const toastStore = defineStore('toastStore', {
  state: () => ({
    _toast: null,
  }),
  getters: {
    toast() {
      return this._toast
    },
  },
  actions: {
    setToast(data) {
      this._toast = data
    },
  },
})
