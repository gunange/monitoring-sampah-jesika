import axios, { AxiosResponse } from 'axios'
import { ApiResponse } from './interface'
import { apps_debug } from '@/config/appInfo'

import { errorHeandlersMessage } from '@/controller/others/RequestApiController/heanleErrorMessage'

export function heandleErrors(errors: any, collection: string): ApiResponse {
  if (axios.isAxiosError(errors) && errors.response) {
    if (apps_debug)
      console.info(`⛔️ api response ${collection} status:`, errors.response.data.message)

    const { error } = errorHeandlersMessage(errors.response.data)

    return {
      status: errors.response.status,
      data: [],
      message: errors.response.data
        ? errors.response.data.message
        : errors.response.statusText || 'Error',
      error: error,
      errors: errors.response.data.erros,
    }
  } else if (errors.request) {
    if (apps_debug)
      console.info(
        `⛔️ api request ${collection} error :`,
        errors.request.status == 0 ? 'Server Connection Failed' : errors.request,
      )

    return {
      status: 500,
      data: [],
      message: 'Unknow error',
      errors: [],
      error: '',
    }
  } else {
    if (apps_debug) console.info(`⛔️ api error ${collection} error:`, errors.message)
    return {
      status: 500,
      data: [],
      message: 'Unknow error',
      errors: [],
      error: 'Internal Server Error',
    }
  }
}
