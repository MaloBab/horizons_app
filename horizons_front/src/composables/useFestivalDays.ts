import { computed } from 'vue'
import { useFestivalStore } from '../stores/useFestivalStore'
import type { FestivalDay } from '../types/planning.types'

const DAY_NAMES   = ['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
const MONTH_NAMES = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

// JS getDay() → convention Python (Lundi=0 ... Dimanche=6)
const jsToPythonDay = (jsDay: number): number => jsDay === 0 ? 6 : jsDay - 1

export function useFestivalDays() {
  const festivalStore = useFestivalStore()

  const festivalDays = computed<FestivalDay[]>(() => {
    const f = festivalStore.festival
    if (!f?.start_date || !f?.end_date) return []

    const days: FestivalDay[] = []
    const current = new Date(f.start_date)
    const end     = new Date(f.end_date)

    while (current <= end) {
      days.push({
        label: `${DAY_NAMES[current.getDay()]} ${current.getDate()} ${MONTH_NAMES[current.getMonth()]} ${current.getFullYear()}`,
        date:  current.toISOString().split('T')[0]!,
        day:   jsToPythonDay(current.getDay()),  // ← Vendredi=4, Samedi=5, Dimanche=6
      })
      current.setDate(current.getDate() + 1)
    }

    return days
  })

  return { festivalDays }
}