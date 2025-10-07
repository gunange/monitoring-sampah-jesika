export function getProgressClass(value) {
  if (value === 100) return 'progress-full'
  if (value >= 75) return 'progress-minim-75'
  if (value >= 40) return 'progress-minim-40'
  return 'progress-minim-20'
}
