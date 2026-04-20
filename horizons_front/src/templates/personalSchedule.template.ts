import type { Volunteer } from '../types/benevole.types'
import type { JobWithRelations } from '../types/planning.types'
import { SHARED_STYLES } from './scheduleStyles'
import { DAY_NAMES, formatHour } from './scheduleHelpers'

export function generatePersonalScheduleHtml(
  volunteer: Volunteer,
  volunteerJobs: JobWithRelations[],
  allVolunteers: Volunteer[],
  assignmentsByJob: Map<number, { volunteer_id: string }[]>,
): string {
  const fullName = `${volunteer.first_name} ${volunteer.last_name}`
  const initials = `${volunteer.first_name[0]}${volunteer.last_name[0]}`
  const count    = volunteerJobs.length
  const today    = new Date().toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })

  // ── Tri croissant : jour puis heure de début ─────────────────────────────
  const sorted = [...volunteerJobs].sort((a, b) =>
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
      const day   = DAY_NAMES[job.slot.day_index] ?? `Jour ${job.slot.day_index}`
      const start = formatHour(job.slot.start_time)
      const end   = formatHour(job.slot.end_time)

      // Bénévole destinataire en premier (chip colorée), collègues ensuite
      const allIds  = (assignmentsByJob.get(job.id) ?? []).map(a => a.volunteer_id)
      const ordered = [volunteer.id, ...allIds.filter(id => id !== volunteer.id)]
      const names   = ordered
        .map(id => allVolunteers.find(v => v.id === id))
        .filter(Boolean)
        .map((v, i) => ({ name: `${v!.first_name} ${v!.last_name}`, isSelf: i === 0 }))

      const chips = names.length
        ? names
            .map(({ name, isSelf }) =>
              isSelf
                ? `<span class="volunteer-chip volunteer-chip--self">${name}</span>`
                : `<span class="volunteer-chip">${name}</span>`,
            )
            .join('')
        : '<span class="no-assignee">Aucun bénévole</span>'

      return `
        <tr>
          <td style="font-weight:600;color:#f1f5f9">${job.name}</td>
          <td><span class="badge badge-day">${day}</span></td>
          <td><span class="badge badge-time">${start} – ${end}</span></td>
          <td><div class="volunteer-chips">${chips}</div></td>
        </tr>`
    }).join('')

    return `
      <div class="section-title">
        <div class="dot"></div><h2>${cat}</h2><div class="line"></div>
      </div>
      <table>
        <thead>
          <tr>
            <th>Poste</th><th>Jour</th><th>Horaire</th><th>Équipe</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>`
  }).join('')

  return `<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <style>
    ${SHARED_STYLES}
    .avatar {
      width: 52px; height: 52px; border-radius: 14px;
      background: linear-gradient(135deg, rgba(6,182,212,0.3), rgba(99,102,241,0.3));
      border: 1px solid rgba(6,182,212,0.25);
      display: flex; align-items: center; justify-content: center;
      font-size: 1.1rem; font-weight: 700; color: #22d3ee;
      margin-bottom: 14px;
    }
  </style>
</head>
<body>
<div class="page">

  <div class="header">
    <div class="header-left">
      <div class="festival-tag">Planning bénévole</div>
      <div class="avatar">${initials}</div>
      <h1>${fullName}</h1>
      <p class="subtitle">${volunteer.email}</p>
    </div>
    <div class="header-meta">
      <div class="meta-badge">
        <span class="count">${count}</span>
        <span class="label">poste${count > 1 ? 's' : ''} affecté${count > 1 ? 's' : ''}</span>
      </div>
    </div>
  </div>

  ${sections || `
    <div class="section-title">
      <div class="dot"></div><h2>Affectations</h2><div class="line"></div>
    </div>
    <table>
      <tbody>
        <tr><td colspan="4" style="text-align:center;color:#334155;padding:24px">Aucun poste affecté</td></tr>
      </tbody>
    </table>`}

  <footer>
    <span class="left">Généré automatiquement · Festival</span>
    <span class="right">${today}</span>
  </footer>

</div>
</body>
</html>`
}