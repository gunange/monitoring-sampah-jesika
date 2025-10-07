import { heandleAllert } from './heandleAlert'
import { heandleErrors } from './heandleErrors'
import { errorHeandlersMessage } from './heanleErrorMessage'
import { ApiResponse, ToastAlertSuccessResponse } from './interface'
import axios, { AxiosRequestConfig } from 'axios'

export async function get(
  collection: string,
  alert: boolean = false,
  config?: AxiosRequestConfig,
): Promise<ApiResponse> {
  try {
    const { data, status, statusText } = await axios.get(collection, config)

    if (alert) {
      heandleAllert({
        status: status,
        response: data,
        alert: {
          detail: data.message ?? statusText,
        },
      })
    }

    const { error } = errorHeandlersMessage(data)

    return {
      status: status,
      data: data.data ?? [],
      message: data.message ?? statusText,
      error: error,
      errors: data.errors ?? [],
    }
  } catch (error: any) {
    return heandleErrors(error, collection)
  }
}
