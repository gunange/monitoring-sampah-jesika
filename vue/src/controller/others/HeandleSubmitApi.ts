import { toastStore } from '@/stores/services/toast-store'
import { errorHeandlersMessage } from '@/controller/others/RequestApiController/heanleErrorMessage'

export class HeandleSubmitApi {
  get toast() {
    return toastStore().toast
  }
  error(status, response: any): boolean {
    if (status === 201 || status === 200) {
      return false
    }
    const { summaryMessge, error } = errorHeandlersMessage(response)

    this.toast.add({
      severity: 'error',
      summary: summaryMessge,
      detail: error,
      life: 5000,
    })
    return true
  }
  sukses(detail?: String) {
    this.toast.add({
      severity: 'success',
      summary: 'Sukses',
      detail: detail ?? 'Sukses !',
      life: 3000,
    })
  }
}
