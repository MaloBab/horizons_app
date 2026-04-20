export function getCategoryColor(id: number): string {
  const hue = (id * 137.508) % 360
  return `hsl(${hue}, 70%, 60%)`
}

export function getCategoryBg(id: number): string {
  const hue = (id * 137.508) % 360
  return `hsla(${hue}, 70%, 60%, 0.08)`
}