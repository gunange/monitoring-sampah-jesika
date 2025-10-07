import { heandleAllert } from './heandleAlert'
import { heandleErrors } from './heandleErrors'
import { errorHeandlersMessage } from './heanleErrorMessage'
import { ApiResponse, ToastAlertSuccessResponse } from './interface'
import axios, { AxiosRequestConfig } from 'axios'

export async function patch(
  collection: string,
  body: any,
  alert: boolean = true,
  config?: AxiosRequestConfig,
): Promise<ApiResponse> {
  try {
    const { data, status, statusText } = await axios.patch(collection, body, config)
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
      errors: data.errors ?? [],
      error: error,
    }
  } catch (error: any) {
    return heandleErrors(error, collection)
  }
}
