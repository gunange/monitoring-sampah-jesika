import { defineRule } from 'vee-validate'

defineRule('required', (e: any) => {
  if (typeof e === 'number' || typeof e === 'boolean') return true

  if (e === null || e === undefined || e === '') {
    return 'Data ini wajib diisi'
  }

  return true
})

defineRule('email', (e: any) => {
  if (!e || !e.length) {
    return true
  }
  if (!/^[^@]+@\w+(\.\w+)+\w$/.test(e)) {
    return 'Data yang anda masukan buka Email'
  }
  return true
})
defineRule('minLength', (e: any, [limit]: any) => {
  const str = String(e ?? '') // aman untuk null/undefined/0

  if (str.length === 0) return true // kalau kosong, anggap valid (opsional)

  if (str.length < limit) {
    return `Minimal karakter ${limit}`
  }

  return true
})
defineRule('maxLength', (e: any, [limit]: any) => {
  const str = String(e ?? '')
  if (str.length === 0) return true

  if (str.length > limit) return `Maksimal karakter ${limit}`

  return true
})

defineRule('minMax', (e: any, [min, max]: any) => {
  if (!e || !e.length) {
    return true
  }
  const numericValue = Number(e)
  if (numericValue < min) {
    return `Minimal Angka ${min}`
  }
  if (numericValue > max) {
    return `Maksimal ${max}`
  }
  return true
})

defineRule('between', (e: any, [min, max]: any) => {
  if (!e || !e.length) {
    return true
  }

  if (e.length < min) {
    return `Minimal Karakter ${min}`
  }
  if (e.length > max) {
    return `Maksimal Karakter ${max}`
  }
  return true
})

defineRule('confirmed', (e, [target]: any, ctx) => {
  if (e === ctx.form[target]) {
    return true
  }
  return 'Konfirmasi Password salah'
})

defineRule('number', (e: any) => {
  if (isNaN(e)) {
    return 'Data ini harus berupa angka'
  }
  return true
})

defineRule('onlyNumber', (input: any) => {
  const nonNumberPattern = /[^0-9]/

  if (nonNumberPattern.test(input)) {
    return 'Data ini harus berupa angka dan tidak boleh ada karakter lain.'
  }
  return true
})

defineRule('phone', (e: any) => {
  if (e === null || e === undefined || e === '') return true

  const value = String(e) // pastikan berupa string
  const regex = /^(?:\+62|08)[0-9]{8,12}$/

  if (!regex.test(value)) {
    return 'Nomor telepon tidak valid (format +62xxxxxxxxxxx atau 08xxxxxxxxxx)'
  }

  return true
})

defineRule('time', (e: any) => {
  // Regular expression for 24-hour time format (HH:MM)
  const regex = /^([0-1][0-9]|2[0-3]):([0-5][0-9])$/

  if (!regex.test(e)) {
    return 'Format waktu tidak valid (format HH:MM)'
  }

  // Additional validation (optional): Check if time is within valid range (00:00 - 23:59)
  const [hours, minutes] = e.split(':')
  if (hours < 0 || hours > 23 || minutes < 0 || minutes > 59) {
    return 'Waktu harus berada diantara 00:00 dan 23:59'
  }

  return true
})

defineRule('string', (e: any) => {
  if (typeof e !== 'string') {
    return 'Data harus berupa karakter'
  }
  return true
})
defineRule('field_name', (value: string) => {
  if (typeof value !== 'string') {
    return 'Field harus berupa teks.'
  }

  // Cek apakah mengandung karakter selain a-z, A-Z, 0-9, dan _
  const isValid = /^[a-zA-Z0-9_]+$/.test(value)

  if (!isValid) {
    return 'hanya (_) yang diperbolehkan.'
  }

  return true
})

defineRule('link', (e: any) => {
  const urlRegex =
    /https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)/g

  if (!urlRegex.test(e)) {
    return 'Data harus berupa URL yang valid'
  }
  return true
})

defineRule('maxNumber', (value: any, [max]: [number]) => {
  const number = Number(value)

  if (isNaN(number)) {
    return 'Data harus berupa angka.'
  }

  if (number > max) {
    return `Nilai tidak boleh lebih dari ${max}.`
  }

  return true
})

defineRule('macAddress', (e: any) => {
  if (!e || !e.length) {
    return true // Anggap valid jika kosong (opsional)
  }

  // Regex untuk memvalidasi format MAC Address
  const macAddressRegex = /^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/

  if (!macAddressRegex.test(e)) {
    return 'Format MAC Address tidak valid'
  }

  return true
})
defineRule('ipAddress', (e: any) => {
  if (!e || !e.length) {
    return true // Anggap valid jika kosong (opsional)
  }

  // Regex untuk memvalidasi format IPv4
  const ipAddressRegex =
    /^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)$/

  if (!ipAddressRegex.test(e)) {
    return 'Format IP Address tidak valid'
  }

  return true
})

defineRule('boolean', (e: any) => {
  if (e === null || e === undefined) {
    return true // Anggap valid jika nilai adalah null (opsional)
  }

  if (typeof e === 'boolean') {
    return true // Valid jika tipe data adalah boolean
  }

  return 'Data harus berupa nilai true atau false'
})
