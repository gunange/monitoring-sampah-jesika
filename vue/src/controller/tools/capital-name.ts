export function capitalName(name: string): string {
  return name
    .split(',') // Pisahkan berdasarkan koma
    .map((part, index) => {
      if (index === 0) {
        // Ubah hanya bagian sebelum koma
        return part
          .split(' ')
          .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
          .join(' ')
      }
      // Bagian setelah koma tetap seperti aslinya
      return part.trim()
    })
    .join(', ')
}
