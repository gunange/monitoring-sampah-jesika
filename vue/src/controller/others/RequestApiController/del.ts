import { heandleAllert } from './heandleAlert'
import { heandleErrors } from './heandleErrors'
import { errorHeandlersMessage } from './heanleErrorMessage'
import { ApiResponse, ToastAlertSuccessResponse } from './interface'
import axios, { AxiosRequestConfig } from 'axios'

export async function del(
  collection: string,
  alert: boolean = true,
  config?: AxiosRequestConfig,
): Promise<ApiResponse> {
  try {
    const { data, status, statusText } = await axios.delete(collection, config)

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
