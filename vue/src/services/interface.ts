export interface StoreDataFormApi {
  id?: number
  load: boolean
  run: boolean
  data: any[]
  dataOnly: any
  filter: any | null
}
