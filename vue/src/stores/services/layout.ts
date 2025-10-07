import { defineStore } from 'pinia'
import { appCode } from '@/config/appInfo.js'

export const layoutState = defineStore('layout-state', {
  state: () => ({
    is_tema_dark: false,
    is_online: false,
    style: {
      fontFamily: null,
      fontSize: null,
    },
  }),
  actions: {
    listenerInternetConnnection() {
      this.is_online = navigator.onLine
      window.addEventListener('online', () => {
        this.is_online = true
      })
      window.addEventListener('offline', () => {
        this.is_online = false
      })
    },
    setTema() {
      this.is_tema_dark = !this.is_tema_dark
      var set_storage = this.is_tema_dark ? true : false
      localStorage.setItem('is_tema_dark', `set_storage`)
    },
    initTema() {
      var get_storage =
        localStorage.is_tema_dark !== undefined && localStorage.is_tema_dark == 'true'
          ? true
          : false
      this.is_tema_dark = get_storage
    },
    setStyle({ fs, ff }) {
      this.style.fontFamily = ff
      this.style.fontSize = fs

      const style = document.documentElement.style
      style.setProperty('--font-family', ff)
      style.setProperty('--font-size', fs)

      localStorage.setItem(`${appCode}-font-family`, ff)
      localStorage.setItem(`${appCode}-font-size`, fs)
    },
    initStyle() {
      const ff = localStorage.getItem(`${appCode}-font-family`)
      const fs = localStorage.getItem(`${appCode}-font-size`)

      if (ff && fs) {
        const style = document.documentElement.style

        this.style.fontFamily = ff
        this.style.fontSize = fs

        style.setProperty('--font-family', ff)
        style.setProperty('--font-size', fs)
      }
    },
  },
})
