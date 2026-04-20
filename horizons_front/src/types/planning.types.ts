export interface Category {
  id:            number
  label:         string
  pole_id?:      number | null
  preference_id?: number | null
}

export interface Preference {
  id:         number
  label:      string
  categories: Category[]
}

export interface Slot {
  id:         number
  day_index:  number
  start_time: number
  end_time:   number
}

export type RecruitmentType = 'Normal' | 'Specialise'

export interface Job {
  id:                  number
  name:                string
  category_id:         number
  slot_id:             number
  required_volunteers: number
  recruitment_type:    RecruitmentType
  responsible:         string | null
  sort_order:          number
}

export interface JobWithRelations extends Job {
  category: Category
  slot:     Slot
}

export interface CategoryGroup {
  category: Category
  jobs:     JobWithRelations[]
}

export interface JobGroupResponse {
  name:             string
  recruitment_type: RecruitmentType
  responsible:      string | null
  sort_order:       number
  slots:            JobWithRelations[]
}

export interface CategoryGroupResponse {
  category: Category
  jobs:     JobGroupResponse[]
}

export interface FestivalDay {
  label: string
  date:  string
  day:   number
}

export const GANTT_HOURS: number[] = [
  8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23,
  0, 1, 2, 3, 4, 5
]

export const HOURS_PER_DAY = GANTT_HOURS.length