const numberFormat = new Intl.NumberFormat('es-CR')

export function formatNumber(num: number): string {
  if (!num) return '0'
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return numberFormat.format(Math.round(num / 1000) * 1000)
  return numberFormat.format(Math.round(num))
}
