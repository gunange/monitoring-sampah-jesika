import { StoreDataFormApi } from '../interface'

export const createStoreDefault = (): StoreDataFormApi => ({
  load: false,
  run: false,
  data: [],
  dataOnly: {},
  filter: null,
})
