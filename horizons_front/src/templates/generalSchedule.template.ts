import type { Volunteer } from '../types/benevole.types'
import type { JobWithRelations } from '../types/planning.types'
import { SHARED_STYLES } from './scheduleStyles'
import { DAY_NAMES, formatHour, renderVolunteerChips } from './scheduleHelpers'

export function generateGeneralScheduleHtml(
  jobs: JobWithRelations[],
  allVolunteers: Volunteer[],
  assignmentsByJob: Map<number, { volunteer_id: string }[]>,
): string {
  const today     = new Date().toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })
  const totalJobs = jobs.length
  const totalFull = jobs.filter(j => (assignmentsByJob.get(j.id)?.length ?? 0) >= j.required_volunteers).length

  // ── Tri global croissant : jour puis heure de début ──────────────────────
  const sorted = [...jobs].sort((a, b) =>
    a.slot.day_index !== b.slot.day_index
      ? a.slot.day_index - b.slot.day_index
      : a.slot.start_time - b.slot.start_time,
  )

  // ── Regroupement par catégorie (ordre d'apparition après tri) ────────────
  const byCategory = new Map<string, JobWithRelations[]>()
  for (const job of sorted) {
    const label = job.category.label
    if (!byCategory.has(label)) byCategory.set(label, [])
    byCategory.get(label)!.push(job)
  }

  const sections = [...byCategory.entries()].map(([cat, catJobs]) => {
    const rows = catJobs.map(job => {
      const day          = DAY_NAMES[job.slot.day_index] ?? `Jour ${job.slot.day_index}`
      const start        = formatHour(job.slot.start_time)
      const end          = formatHour(job.slot.end_time)
      const assignedIds  = (assignmentsByJob.get(job.id) ?? []).map(a => a.volunteer_id)
      const assignedNames = assignedIds
        .map(id => allVolunteers.find(v => v.id === id))
        .filter(Boolean)
        .map(v => `${v!.first_name} ${v!.last_name}`)

      const isFull     = assignedIds.length >= job.required_volunteers
      const isPartial  = assignedIds.length > 0 && !isFull
      const badgeClass = isFull ? 'badge-full' : isPartial ? 'badge-partial' : 'badge-empty'
      const fillLabel  = `${assignedIds.length} / ${job.required_volunteers}`

      return `
        <tr>
          <td style="font-weight:600;color:#f1f5f9">${job.name}</td>
          <td><span class="badge badge-day">${day}</span></td>
          <td><span class="badge badge-time">${start} – ${end}</span></td>
          <td><span class="badge ${badgeClass}">${fillLabel}</span></td>
          <td><div class="volunteer-chips">${renderVolunteerChips(assignedNames)}</div></td>
        </tr>`
    }).join('')

    return `
      <div class="section-title">
        <div class="dot"></div><h2>${cat}</h2><div class="line"></div>
      </div>
      <table>
        <thead>
          <tr>
            <th>Poste</th><th>Jour</th><th>Horaire</th><th>Effectif</th><th>Bénévoles</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>`
  }).join('')

  return `<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <style>${SHARED_STYLES}</style>
</head>
<body>
<div class="page">

  <div class="header">
    <div class="header-left">
      <div class="festival-tag">Planning général</div>
      <h1>Vue d'ensemble</h1>
      <p class="subtitle">Récapitulatif de toutes les affectations</p>
    </div>
    <div class="header-meta" style="display:flex;gap:10px">
      <div class="meta-badge">
        <span class="count">${totalJobs}</span>
        <span class="label">postes</span>
      </div>
      <div class="meta-badge">
        <span class="count" style="color:#86efac">${totalFull}</span>
        <span class="label">complets</span>
      </div>
    </div>
  </div>

  ${sections}

  <footer>
    <span class="left">Généré automatiquement · Festival</span>
    <span class="right">${today}</span>
  </footer>

</div>
</body>
</html>`
}