import type { JobWithRelations } from './planning.types'

// ─────────────────────────────────────────────────────────────────────────────
// Shapes réseau (miroir exact des schémas Pydantic backend)
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Miroir de VolunteerShortResponse — embarqué dans AssignmentResponse.
 * Intentionnellement minimal : les données complètes du bénévole sont
 * croisées via useBenevoles() pour les métriques.
 */
export interface AssignmentVolunteerShort {
  id:         string   // UUID
  first_name: string
  last_name:  string
  email:      string
}

/**
 * Miroir de AssignmentResponse.
 * Note : pas de champ `id` — la clé primaire composite (volunteer_id, job_id)
 * est l'identifiant réel en base. À corriger côté backend si un id auto est ajouté.
 */
export interface AssignmentResponse {
  volunteer_id: string          // UUID — déduit de volunteer.id
  job_id:       number
  volunteer:    AssignmentVolunteerShort
  job:          JobWithRelations
}

// ─────────────────────────────────────────────────────────────────────────────
// Payloads API
// ─────────────────────────────────────────────────────────────────────────────

export interface AssignmentCreate {
  volunteer_id: string
  job_id:       number
}

export interface AssignmentDelete {
  volunteer_id: string
  job_id:       number
}

// ─────────────────────────────────────────────────────────────────────────────
// Modèle frontend enrichi
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Clé composite utilisée comme identifiant unique d'une affectation
 * dans les Maps et structures de l'état frontend.
 */
export type AssignmentKey = `${string}__${number}` // `${volunteer_id}__${job_id}`

export function makeAssignmentKey(volunteerId: string, jobId: number): AssignmentKey {
  return `${volunteerId}__${jobId}`
}

/**
 * Représentation frontend d'une affectation.
 * Aplatit la relation pour un accès direct sans re-navigation d'objet imbriqué.
 */
export interface Assignment {
  volunteer_id: string
  job_id:       number
  key:          AssignmentKey
}

// ─────────────────────────────────────────────────────────────────────────────
// Limites horaires journalières
// ─────────────────────────────────────────────────────────────────────────────

/** Limite horaire journalière par type de bénévole */
export const DAILY_HOUR_LIMITS = {
  Normal:     6,
  Specialise: 2,
} as const

// ─────────────────────────────────────────────────────────────────────────────
// Poids du score de satisfaction
//
// Les poids de base (WITH_MATES + WITH_PREFS) doivent sommer à 1.
// Quand un critère ne s'applique pas (pas de mates, pas de préférences),
// il est retiré et les poids restants sont renormalisés automatiquement
// par computeVolunteerMetrics — modifier ici suffit, pas besoin de toucher
// à la logique de renormalisation.
//
// Ordre d'importance retenu : C (mates) > D (horaire) > B (préférences)
// ─────────────────────────────────────────────────────────────────────────────

export const SATISFACTION_WEIGHTS = {
  /** Critère C — travailler avec un mate sur le même poste */
  MATES:       0.40,
  /** Critère D — qualité horaire du créneau (nuit + charge journalière) */
  SCHEDULE:    0.35,
  /** Critère B — catégorie du poste correspond à une préférence déclarée */
  PREFERENCES: 0.25,
} as const

/**
 * Sous-poids internes au critère D.
 * D_nuit et D_charge contribuent chacun à 50 % du score horaire.
 */
export const SCHEDULE_SUBWEIGHTS = {
  /**
   * Pénalité pour les postes nocturnes consécutifs enchaînés dans la même journée.
   * Un seul poste nocturne, aussi long soit-il, n'est pas pénalisé.
   * La pénalité s'applique uniquement lorsque plusieurs postes distincts se
   * suivent sans interruption (ou se touchent) en zone nocturne.
   */
  NIGHT_PENALTY: 0.50,
  /** Pénalité si la charge journalière totale approche ou dépasse la limite */
  DAILY_LOAD:    0.50,
} as const

/**
 * Première heure considérée comme "nocturne" (notation décalée).
 * 24 = minuit, 29 = 5h du matin.
 */
export const NIGHT_HOUR_START = 24

/**
 * Nombre minimum de postes nocturnes CONSÉCUTIFS (se touchant ou se
 * chevauchant) déclenchant une pénalité de satisfaction.
 *
 * Règle :
 *   - 1 seul poste nocturne (quelle que soit sa durée) → aucune pénalité.
 *   - 2 postes nocturnes consécutifs → pénalité déclenchée (seuil = 2).
 *   - N postes → pénalité croissante au-delà du seuil.
 *
 * Exemples (seuil = 2) :
 *   Poste 1h–3h (1 poste)            → chaîne max = 1 < seuil → d_nuit = 1 (pas de pénalité)
 *   Postes 1h–2h + 2h–3h (2 postes)  → chaîne max = 2 = seuil → pénalité partielle
 *   Postes 1h–2h + 2h–3h + 3h–4h    → chaîne max = 3         → pénalité plus forte
 */
export const CONSECUTIVE_NIGHT_THRESHOLD = 2

// ─────────────────────────────────────────────────────────────────────────────
// Métriques par bénévole (calculées côté frontend)
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Métriques dérivées d'un bénévole, calculées à partir de ses affectations
 * courantes et de ses données (disponibilités, affinités, préférences).
 * Recalculées réactivement à chaque modification d'affectation.
 */
export interface VolunteerMetrics {
  volunteer_id:         string
  /** Nombre d'heures affectées au total */
  total_hours:          number
  /** Heures affectées par day_index */
  hours_per_day:        Record<number, number>
  /** true si au moins un jour dépasse la limite pour ce type de bénévole */
  daily_limit_exceeded: boolean
  /** Nombre de créneaux où le bénévole travaille avec un compagnon (mate) */
  slots_with_mate:      number
  /** Nombre de créneaux où le bénévole travaille sans compagnon */
  slots_without_mate:   number
  /**
   * Score de satisfaction global [0–1], moyenne des scores par poste.
   * Seuls les critères applicables au bénévole entrent dans le calcul
   * (ex : critère C ignoré si aucun mate déclaré).
   * null si aucune affectation.
   */
  satisfaction_score:   number | null
  /** Nombre de postes affectés */
  assignment_count:     number
}

// ─────────────────────────────────────────────────────────────────────────────
// Métriques globales (panneau de synthèse)
// ─────────────────────────────────────────────────────────────────────────────

export interface GlobalMetrics {
  /** Nombre de jobs ayant atteint required_volunteers */
  jobs_filled:         number
  jobs_total:          number
  /** Nombre de bénévoles ayant au moins une affectation */
  volunteers_assigned: number
  volunteers_total:    number
  /** Moyenne des satisfaction_score sur tous les bénévoles affectés */
  avg_satisfaction:    number
  /** Moyenne des heures totales par jour, sur l'ensemble des bénévoles */
  avg_hours_per_day:   number
}

// ─────────────────────────────────────────────────────────────────────────────
// Historique — pattern Command pour Undo/Redo
// ─────────────────────────────────────────────────────────────────────────────

export type CommandType = 'assign' | 'unassign' | 'reassign'

export interface AssignCommand {
  type:       'assign'
  assignment: Assignment
}

export interface UnassignCommand {
  type:       'unassign'
  assignment: Assignment
}

/**
 * Réaffectation = désaffectation d'un poste source + affectation sur un poste cible.
 * Stocké comme une commande atomique pour que Undo restaure les deux en une seule étape.
 */
export interface ReassignCommand {
  type: 'reassign'
  from: Assignment
  to:   Assignment
}

export type HistoryCommand = AssignCommand | UnassignCommand | ReassignCommand

// ─────────────────────────────────────────────────────────────────────────────
// État du store
// ─────────────────────────────────────────────────────────────────────────────

export type SaveState = 'saved' | 'unsaved' | 'saving' | 'error'