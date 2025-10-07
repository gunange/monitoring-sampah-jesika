import { toastStore } from '@/stores/services/toast-store'
import { watch, reactive, ref } from 'vue'

export class LocationApp {
  location = reactive({
    lat: null,
    long: null,
    error: {
      code: null,
      message: null,
    },
  })

  private get toast() {
    return toastStore().toast
  }

  async generateLocation(): Promise<void> {
    if (navigator.geolocation) {
      try {
        const position = await new Promise((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(resolve, reject)
        })

        const coords = position['coords'] ?? {}

        this.location.lat = coords.latitude
        this.location.long = coords.longitude
      } catch (err) {
        this.location.error = err
        this.toast.add({
          severity: 'error',
          summary: 'Error!',
          detail:
            err.code == 1
              ? 'Mohon aktifkan lokasi, karena anda tidak mengijinkan aplikasi untuk mengakses lokasi'
              : err.message,
          life: 5000,
        })
      }
    } else {
      this.toast.add({
        severity: 'error',
        summary: 'Error!',
        detail: 'Web Browser anda tidak mendukung Geolocation',
        life: 5000,
      })
    }
  }
}
