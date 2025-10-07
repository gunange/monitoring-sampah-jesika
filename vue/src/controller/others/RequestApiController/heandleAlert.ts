import { HeandleSubmitApi } from '../HeandleSubmitApi'
import { ApiAlertResponse } from './interface'

export function heandleAllert(data: ApiAlertResponse): void {
  const heandle = new HeandleSubmitApi()

  if (!heandle.error(data.status, data.response)) {
    heandle.sukses(data.alert.detail)
  }
}
