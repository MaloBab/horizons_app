export type VolunteerType = 'Normal' | 'Specialise'

export interface Slot {
  day_index: number
  start_time: number
  end_time: number
}

export interface VolunteerSlot {
  slot_id: number
  slot: Slot
}

export interface VolunteerPreference {
  rank: number
  preference: { id: number; label: string }
}


export interface VolunteerShort {
  id: string
  first_name: string
  last_name: string
  email: string
}

export interface Volunteer {
  id: string
  first_name: string
  last_name: string
  email: string
  address: string
  phone_number: string
  volunteer_type: VolunteerType
  preferences: VolunteerPreference[]
  slots: VolunteerSlot[]
  mates: VolunteerShort[]
}

export interface VolunteerTableRow extends Volunteer {
  fullName: string
  slotsCount: number
  actions?: any
}

export const JOURS_SEMAINE = [
  'Lundi',
  'Mardi',
  'Mercredi',
  'Jeudi',
  'Vendredi',
  'Samedi',
  'Dimanche',
  'Lundi (suivant)'
] as const

export const formatSlot = (slot: Slot): string => {
  const inf = slot.start_time > 23 ? slot.start_time - 24 : slot.start_time
  const sup = slot.end_time > 23 ? slot.end_time - 24 : slot.end_time

  let jourDebut = slot.day_index
  let jourFin = slot.day_index

  if (slot.start_time > 23) {
    jourDebut = slot.day_index < 7 ? slot.day_index + 1 : 7
  }
  if (slot.end_time > 23) {
    jourFin = slot.day_index < 7 ? slot.day_index + 1 : 7
  }

  const jourDebutStr = JOURS_SEMAINE[jourDebut]
  const jourFinStr = JOURS_SEMAINE[jourFin]

  if (jourDebut === jourFin) {
    return `${jourDebutStr} : ${inf}h - ${sup}h`
  }
  return `${jourDebutStr} : ${inf}h - ${jourFinStr} ${sup}h`
}