import { reactive } from 'vue'

export class LoadHtml {
  items = reactive({
    html: {
      load: false,
    },
  })
  async run(): Promise<void> {
    const loadStatus = document.readyState

    this.items.html.load = true
    if (loadStatus === 'interactive') {
      await document.addEventListener('readystatechange', () => {
        if (document.readyState === 'complete') {
          this.items.html.load = false
        }
      })
    } else {
      this.items.html.load = false
    }
  }
}

export function delay(ms?: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export function generateUniqID(length = 3) {
  var charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  var password = ''
  for (var i = 0; i < length; i++) {
    password += charset.charAt(Math.floor(Math.random() * charset.length))
  }
  return password.toString()
}

export function normalisasiNomorWA(nomor) {
  if (!nomor) return '';
  return nomor
    .replace(/\s+/g, '')       // hilangkan spasi
    .replace(/^(\+62|62|0)/, '62') // ganti +62, 62, atau 0 di awal dengan 62
    .replace(/[^\d]/g, '');     // hilangkan karakter selain angka
}
