import { defineStore } from 'pinia'
import { atribut } from '@/services/atribut'
import { StoreDataFormApi } from '@/services/interface'

export const storeId = 'siswa-store'

export const userStorage = defineStore(storeId, {
  state: (): {
    isAuth: boolean
    user: any | null
    guru: StoreDataFormApi
    penilaian: StoreDataFormApi
  } => ({
    penilaian: atribut.createStoreDefault(),
    guru: atribut.createStoreDefault(),
    isAuth: false,
    user: false,
  }),
})
