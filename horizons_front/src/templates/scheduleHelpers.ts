export const DAY_NAMES = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

export function formatHour(h: number): string {
  return h < 24 ? `${h}h` : `${h - 24}h`
}

export function renderVolunteerChips(names: string[]): string {
  if (names.length === 0) return '<span class="no-assignee">—</span>'
  return names
    .map(name => `<span class="volunteer-chip">${name}</span>`)
    .join('')
}