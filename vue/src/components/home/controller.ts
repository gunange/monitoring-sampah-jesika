import { TimeApp } from '@/controller/tools'
import { getActivePinia } from 'pinia'

import { userStorage, storeId } from './store'

export class Controller {
  get store() {
    return userStorage()
  }

  get isAuth() {
    return this.store.isAuth
  }

  private get isInitStore() {
    const pinia = getActivePinia()
    return pinia.state.value.hasOwnProperty(storeId)
  }

  async dispose() {
    if (this.isInitStore) {
      await this.store.$reset()
      await this.store.$dispose()
    }
  }
  get time() {
    return new TimeApp()
  }
}
