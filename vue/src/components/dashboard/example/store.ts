import { defineStore } from 'pinia'
import { atribut } from '@/services/atribut'
import { StoreDataFormApi } from '@/services/interface'

export const storeId = 'admin-store'

export const userStorage = defineStore(storeId, {
  state: (): {
    atribut: StoreDataFormApi
    feeder: StoreDataFormApi
    priode: StoreDataFormApi
    websocket: WebSocket | null
  } => ({
    atribut: { ...atribut.storeDefault },
    feeder: { ...atribut.storeDefault },
    priode: { ...atribut.storeDefault },
    websocket: null,
  }),
})
