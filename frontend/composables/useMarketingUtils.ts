export const statusClass = (status: string) => {
  const classes: Record<string, string> = {
    draft: 'px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800',
    scheduled: 'px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800',
    sending: 'px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800',
    sent: 'px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800'
  }
  return classes[status] || classes.draft
}

export const statusLabel = (status: string) => {
  const labels: Record<string, string> = {
    draft: 'Borrador',
    scheduled: 'Programado',
    sending: 'Enviando',
    sent: 'Enviado'
  }
  return labels[status] || status
}

export const formatNumber = (num: number) => {
  return new Intl.NumberFormat('es-CR').format(num || 0)
}

export const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('es-CR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}
