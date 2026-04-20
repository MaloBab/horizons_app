/**
 * composables/useMailTemplate.ts
 *
 * Centralise :
 *  - L'état du template (subject + bodyHtml)
 *  - La liste des variables disponibles (TEMPLATE_VARIABLES)
 *  - L'interpolation côté client (preview uniquement)
 *  - La génération du planning HTML personnel (preview + téléchargement PDF)
 *  - L'envoi batch via l'API backend
 *  - Le chargement / la sauvegarde de templates depuis l'API
 */

import { ref } from 'vue'

export interface Volunteer {
  id:             string
  first_name:     string
  last_name:      string
  email:          string
  phone_number?:  string
  volunteer_type?: string
}

export interface SlotResponse {
  id:         number
  day_index:  number
  start_time: number
  end_time:   number
}

export interface CategoryResponse {
  id:    number
  label: string
}

export interface JobWithRelations {
  id:                  number
  name:                string
  required_volunteers: number
  recruitment_type:    string
  responsible?:        string | null
  category_id:         number
  slot_id:             number
  category:            CategoryResponse
  slot:                SlotResponse
}

export interface FestivalConfig {
  name:          string
  edition:       number
  location_name: string
  location_city: string
  start_date?:   string  // 'YYYY-MM-DD'
  end_date?:     string
}

export interface SendResult {
  volunteer_id: string
  email:        string
  success:      boolean
  error?:       string | null
}

// ── Template persisté en base ─────────────────────────────────────────────────

export interface MailTemplateRecord {
  id:         string
  title:      string
  subject:    string
  content:    string
  is_active:  boolean
  created_at: string
  updated_at: string
}

// ────────────────────────────────────────────────────────────────────────────
// Variables template disponibles
// ────────────────────────────────────────────────────────────────────────────

export interface TemplateVariable {
  key:         string
  label:       string
  description: string
  example:     string
  category:    'volunteer' | 'planning' | 'festival'
}

export const TEMPLATE_VARIABLES: TemplateVariable[] = [
  // Bénévole
  { key: '{{prenom}}',     label: 'Prénom',        description: 'Prénom du bénévole',            example: 'Marie',                        category: 'volunteer' },
  { key: '{{nom}}',        label: 'Nom',            description: 'Nom de famille',                example: 'Dupont',                       category: 'volunteer' },
  { key: '{{prenom_nom}}', label: 'Prénom + Nom',   description: 'Nom complet',                   example: 'Marie Dupont',                 category: 'volunteer' },
  { key: '{{email}}',      label: 'Email',          description: 'Adresse email du bénévole',     example: 'marie@example.com',            category: 'volunteer' },
  { key: '{{telephone}}',  label: 'Téléphone',      description: 'Numéro de téléphone',           example: '06 12 34 56 78',               category: 'volunteer' },
  { key: '{{type}}',       label: 'Type bénévole',  description: 'Normal ou Spécialisé',          example: 'Normal',                       category: 'volunteer' },
  // Planning
  { key: '{{postes}}',       label: 'Liste des postes', description: 'Liste HTML des postes affectés',  example: '• Accueil — Samedi, de 10h à 12h', category: 'planning' },
  { key: '{{nb_postes}}',    label: 'Nombre de postes', description: 'Nombre total de postes assignés', example: '3',                                category: 'planning' },
   // Festival
  { key: '{{festival_nom}}',     label: 'Nom du festival', description: 'Nom officiel du festival', example: 'Horizons Open Sea',        category: 'festival' },
  { key: '{{festival_edition}}', label: 'Édition',         description: 'Numéro d\'édition',        example: '12',                       category: 'festival' },
  { key: '{{festival_lieu}}',    label: 'Lieu',            description: 'Nom du lieu',              example: 'Parc des Expositions',     category: 'festival' },
  { key: '{{festival_ville}}',   label: 'Ville',           description: 'Ville du festival',        example: 'Brest',                    category: 'festival' },
  { key: '{{festival_dates}}',   label: 'Dates',           description: 'Dates du festival',        example: 'du 14/06 au 16/06/2025',   category: 'festival' },
]

// ────────────────────────────────────────────────────────────────────────────
// Helpers locaux (pour le preview front)
// ────────────────────────────────────────────────────────────────────────────

const DAY_NAMES = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

function slotLabel(start: number, end: number): string {
  return `de ${start}h à ${end}h`
}

function dayLabel(dayIndex: number, festivalStart?: string): string {
  const name = DAY_NAMES[dayIndex % 7]!
  if (!festivalStart) return name
  const base = new Date(festivalStart)
  base.setDate(base.getDate() + dayIndex)
  return `${name} ${base.getDate()} ${base.toLocaleDateString('fr-FR', { month: 'long' })}`
}

function jobsListHtml(jobs: JobWithRelations[]): string {
  if (!jobs.length) return '<em>Aucun poste assigné</em>'
  const items = jobs
    .map(j => `<li><strong>${j.name}</strong> — ${dayLabel(j.slot.day_index)}, ${slotLabel(j.slot.start_time, j.slot.end_time)}</li>`)
    .join('')
  return `<ul>${items}</ul>`
}

function jobsListPlain(jobs: JobWithRelations[]): string {
  if (!jobs.length) return 'Aucun poste assigné'
  return jobs
    .map(j => `• ${j.name} — ${dayLabel(j.slot.day_index)}, ${slotLabel(j.slot.start_time, j.slot.end_time)}`)
    .join('\n')
}

// ────────────────────────────────────────────────────────────────────────────
// Interpolation (preview côté client uniquement)
// ────────────────────────────────────────────────────────────────────────────

export function interpolateTemplate(
  template: string,
  volunteer: Volunteer,
  jobs: JobWithRelations[],
  festival?: FestivalConfig,
): string {
  const sorted = [...jobs].sort((a, b) =>
    a.slot.day_index !== b.slot.day_index
      ? a.slot.day_index - b.slot.day_index
      : a.slot.start_time - b.slot.start_time
  )

  const map: Record<string, string> = {
    prenom:           volunteer.first_name,
    nom:              volunteer.last_name,
    prenom_nom:       `${volunteer.first_name} ${volunteer.last_name}`,
    nom_complet:      `${volunteer.first_name} ${volunteer.last_name}`,
    email:            volunteer.email,
    telephone:        volunteer.phone_number ?? '',
    type:             volunteer.volunteer_type ?? '',
    postes:           jobsListHtml(sorted),
    postes_texte:     jobsListPlain(sorted),
    nb_postes:        String(sorted.length),
    festival_nom:     festival?.name ?? '',
    festival_edition: festival ? String(festival.edition) : '',
    festival_lieu:    festival?.location_name ?? '',
    festival_ville:   festival?.location_city ?? '',
    festival_dates:   festival?.start_date && festival.end_date
      ? `du ${new Date(festival.start_date).toLocaleDateString('fr-FR')} au ${new Date(festival.end_date).toLocaleDateString('fr-FR')}`
      : '',
  }

  return template.replace(/\{\{(\w+)\}\}/g, (_, key) => map[key.toLowerCase()] ?? `{{${key}}}`)
}

// ────────────────────────────────────────────────────────────────────────────
// Téléchargement PDF / HTML
// ────────────────────────────────────────────────────────────────────────────

export async function downloadPdf(html: string, filename: string): Promise<void> {
  const win = window.open('', '_blank', 'width=900,height=700')
  if (!win) {
    downloadHtml(html, filename.replace('.pdf', '.html'))
    return
  }
  win.document.write(html)
  win.document.close()
}

export function downloadHtml(html: string, filename: string): void {
  const blob = new Blob([html], { type: 'text/html;charset=utf-8' })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  a.href     = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

// ────────────────────────────────────────────────────────────────────────────
// Envoi batch via l'API backend
// ────────────────────────────────────────────────────────────────────────────

export interface SendBatchParams {
  apiBaseUrl:             string
  volunteers:             Volunteer[]
  subject:                string
  bodyHtml:               string
  jobs:                   JobWithRelations[]
  assignmentsByVolunteer: Map<string, { job_id: number }[]>
  allVolunteers:          Volunteer[]
  assignmentsByJob:       Map<number, { volunteer_id: string }[]>
  includeSchedule:        boolean   // ← nouveau flag pièce jointe
  onProgress?:            (done: number, total: number) => void
}

export async function sendBatchMails(params: SendBatchParams): Promise<SendResult[]> {
  const { apiBaseUrl, volunteers, subject, bodyHtml, includeSchedule, onProgress } = params

  const token = localStorage.getItem('access_token')

  const response = await fetch(`${apiBaseUrl}/mail/send-batch`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({
      subject,
      body_html:        bodyHtml,
      recipient_ids:    volunteers.map(v => v.id),
      include_schedule: includeSchedule,   // ← transmis au backend
    }),
  })

  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail ?? `Erreur serveur (${response.status})`)
  }

  const data = await response.json() as {
    total:   number
    success: number
    errors:  number
    results: SendResult[]
  }

  onProgress?.(data.total, data.total)
  return data.results
}

// ────────────────────────────────────────────────────────────────────────────
// API — Gestion des templates persistés
// ────────────────────────────────────────────────────────────────────────────

function authHeaders(): Record<string, string> {
  const token = localStorage.getItem('access_token')
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
}

export async function fetchMailTemplates(apiBaseUrl: string): Promise<MailTemplateRecord[]> {
  const res = await fetch(`${apiBaseUrl}/mail-templates/`, { headers: authHeaders() })
  if (!res.ok) throw new Error('Impossible de charger les templates')
  return res.json()
}

export async function createMailTemplate(
  apiBaseUrl: string,
  data: { title: string; subject: string; content: string },
): Promise<MailTemplateRecord> {
  const res = await fetch(`${apiBaseUrl}/mail-templates/`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ ...data, is_active: true }),
  })
  if (!res.ok) throw new Error('Impossible de créer le template')
  return res.json()
}

export async function updateMailTemplate(
  apiBaseUrl: string,
  id: string,
  data: { title?: string; subject?: string; content?: string },
): Promise<MailTemplateRecord> {
  const res = await fetch(`${apiBaseUrl}/mail-templates/${id}`, {
    method: 'PUT',
    headers: authHeaders(),
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error('Impossible de mettre à jour le template')
  return res.json()
}

export async function deleteMailTemplate(apiBaseUrl: string, id: string): Promise<void> {
  const res = await fetch(`${apiBaseUrl}/mail-templates/${id}`, {
    method: 'DELETE',
    headers: authHeaders(),
  })
  if (!res.ok) throw new Error('Impossible de supprimer le template')
}

// ────────────────────────────────────────────────────────────────────────────
// Composable principal (état partagé du template)
// ────────────────────────────────────────────────────────────────────────────

const DEFAULT_SUBJECT = ''
const DEFAULT_BODY    = ''

export function useMailTemplate() {
  const subject  = ref<string>(DEFAULT_SUBJECT)
  const bodyHtml = ref<string>(DEFAULT_BODY)

  return { subject, bodyHtml }
}