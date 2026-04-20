import type { JobWithRelations } from '../types/planning.types'
import type { Volunteer } from '../types/benevole.types'

export interface ImportWarning {
  ligne:   number
  nom:     string
  message: string
}

export interface ImportError {
  ligne:   number
  nom:     string | null
  message: string
}

export interface ImportReport<T = JobWithRelations | Volunteer> {
  persisted:       T[]
  warnings:        ImportWarning[]
  errors:          ImportError[]
  total_parsed:    number
  total_persisted: number
  total_warnings:  number
  total_errors:    number
}

// Variantes typées pour chaque domaine
export type JobImportReport       = ImportReport<JobWithRelations>
export type VolunteerImportReport = ImportReport<Volunteer>