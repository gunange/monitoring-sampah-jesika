import { getActivePinia } from 'pinia'

import { delay } from '../tools'
import { del, get, RequestApiController } from '../others/RequestApiController'
import { tokenName } from '@/config/appInfo.js'
import { authStore } from '@/stores/users/auth'
import axios from 'axios'

const apiC = new RequestApiController()

export class AuthController {
  private get isInitStore() {
    const pinia = getActivePinia()
    return pinia.state.value.hasOwnProperty('authStore')
  }

  private setTokenToStore(): void {
    this.store.token = localStorage.getItem(tokenName)
      ? `Bearer ${localStorage.getItem(tokenName)}`
      : null
  }

  get store() {
    return authStore()
  }
  get token() {
    return this.store.token
  }
  get user() {
    return this.store.user
  }

  get isAuth() {
    return this.isInitStore ? this.store.isAuth : false
  }

  get gantiPasswordStore() {
    return this.store.ganti_password
  }

  setToken(): void {
    axios.defaults.headers['Authorization'] = this.token
  }

  async init(): Promise<void> {
    if (this.store.proses.load) return

    this.setTokenToStore()
    if (!this.store.token) return
    this.store.proses.load = true

    const { status, data } = await get('', false, {
      headers: {
        Authorization: this.token,
      },
    })

    this.store.proses.sukses = status === 200

    if (this.store.proses.sukses) {
      this.store.isAuth = true
      this.store.user = data
    }

    this.store.proses.load = false
  }

  async dispose(): Promise<void> {
    if (this.isInitStore) {
      await this.store.$dispose()
      await delay(50)
    }
  }
  async reset(): Promise<void> {
    if (this.isInitStore) {
      await this.store.$reset()
      await delay(50)
    }
  }

  async signOut(redirect: Function) {
    if (this.store.token) {
      const { status } = await del(`user`, false, {
        headers: {
          Authorization: this.token,
        },
      })
      console.info('👮🏻‍♂️ sign-out in server status : ', status)

      if (status == 200) {
        await this.reset()
        await localStorage.removeItem(tokenName)
      }
    }

    redirect()
  }
}
