import { AxiosResponse } from 'axios'

export interface ApiResponse {
  status: number
  data: any
  message: string
  error: string | null | undefined
  errors: any
}

export interface ToastAlertSuccessResponse {
  detail: any
}

export interface ApiAlertResponse {
  status: number
  response: AxiosResponse
  alert: ToastAlertSuccessResponse
}
