import { useActivity } from './useActivity'

// ─────────────────────────────────────────────────────────────────────────────
// Règles de formatage
//
// Ajouter un pattern = ajouter une entrée ici.
//
// Chaque règle :
//   pattern  : RegExp à matcher dans le titre brut
//   replace  : template HTML ($1 = premier groupe capturant)
//              ou fonction (...groups) => string pour les cas dynamiques
// ─────────────────────────────────────────────────────────────────────────────

type FormatRule = {
  pattern: RegExp
  replace: string | ((...groups: string[]) => string)
}

const FORMAT_RULES: FormatRule[] = [
  // Chip tâche  __TASK__Mon titre__ENDTASK__
  {
    pattern: /__TASK__(.*?)__ENDTASK__/g,
    replace: `<span class="task-chip">
      <svg class="w-2.5 h-2.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <polyline points="20 6 9 17 4 12"/>
      </svg>
      $1
    </span>`,
  },

  // Texte gras cyan  **mot**
  {
    pattern: /\*\*(.*?)\*\*/g,
    replace: '<span class="text-cyan-200 font-semibold">$1</span>',
  },

  // Texte italique slate  _mot_
  {
    pattern: /_(.*?)_/g,
    replace: '<span class="text-slate-400 italic">$1</span>',
  },

  // Mention utilisateur  @pseudo
  {
    pattern: /@(\w+)/g,
    replace: '<span class="text-violet-300 font-medium">@$1</span>',
  },

  // Compteur numérique mis en valeur  #42
  {
    pattern: /#(\d+)/g,
    replace: '<span class="text-amber-300 font-mono font-semibold">$1</span>',
  },

  // Métrique pill  ~~valeur|label~~
  {
    pattern: /~~(.*?)\|(.*?)~~/g,
    replace: (_, value, label) =>
      `<span class="metric-pill">
        <span class="metric-pill__value">${value}</span>
        <span class="metric-pill__label">${label}</span>
      </span>`,
  },
]


export const formatTitle = (title: string): string =>
  FORMAT_RULES.reduce((acc, { pattern, replace }) => {
    pattern.lastIndex = 0
    return typeof replace === 'function'
      ? acc.replace(pattern, replace as (...args: string[]) => string)
      : acc.replace(pattern, replace)
  }, title)


export const formatTimestamp = (timestamp: Date): string => {
  const diff    = Date.now() - timestamp.getTime()
  const minutes = Math.floor(diff / 60_000)
  const hours   = Math.floor(diff / 3_600_000)
  const days    = Math.floor(diff / 86_400_000)
  if (minutes < 1)  return "À l'instant"
  if (minutes < 60) return `${minutes}min`
  if (hours   < 24) return `${hours}h`
  if (days    < 7)  return `${days}j`
  return timestamp.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
}

// ─────────────────────────────────────────────────────────────────────────────
// Helpers de construction des messages
//
// Ces fonctions produisent les marqueurs bruts reconnus par FORMAT_RULES.
// Les utiliser dans les messages ACTIVITIES garantit la cohérence rendu/création.
// ─────────────────────────────────────────────────────────────────────────────

export const fmt = {
  task:    (t: string)          => `__TASK__${t}__ENDTASK__`,
  bold:    (t: string)          => `**${t}**`,
  italic:  (t: string)          => `_${t}_`,
  mention: (u: string)          => `@${u}`,
  counter: (n: number)          => `#${n}`,
  metric:  (v: string | number, label: string) => `~~${v}|${label}~~`,
}

const STATUS_LABELS: Record<string, string> = {
  open:   '🔵 Ouvert',
  review: '🟣 À vérifier',
  closed: '🟢 Fermé',
}
const statusLabel = (s: string) => STATUS_LABELS[s] ?? s


type ActivityDef<P extends unknown[]> = {
  action_type: string
  message:     (...args: P) => string
}

const ACTIVITIES = {

  taskCreated: {
    action_type: 'task_created',
    message: (taskTitle: string) =>
      `✨ Nouvelle tâche ${fmt.task(taskTitle)} créée`,
  } satisfies ActivityDef<[string]>,

  taskDeleted: {
    action_type: 'task_deleted',
    message: (taskTitle: string) =>
      `🗑️ Tâche ${fmt.task(taskTitle)} supprimée`,
  } satisfies ActivityDef<[string]>,

  taskStatusChanged: {
    action_type: 'task_status_changed',
    message: (taskTitle: string, from: string, to: string) =>
      `🔄 ${fmt.task(taskTitle)} · ${statusLabel(from)} → ${statusLabel(to)}`,
  } satisfies ActivityDef<[string, string, string]>,

  taskAssigned: {
    action_type: 'task_assigned',
    message: (taskTitle: string, assignee: string) =>
      `👤 ${fmt.task(taskTitle)} assignée à ${fmt.mention(assignee)}`,
  } satisfies ActivityDef<[string, string]>,

  commentAdded: {
    action_type: 'comment_added',
    message: (taskTitle: string) =>
      `💬 Nouveau commentaire sur ${fmt.task(taskTitle)}`,
  } satisfies ActivityDef<[string]>,

  calendarAdded: {
    action_type: 'calendar_added',
    message: (taskTitle: string) =>
      `📅 ${fmt.task(taskTitle)} synchronisée avec ${fmt.bold('Google Agenda')}`,
  } satisfies ActivityDef<[string]>,

  calendarRemoved: {
    action_type: 'calendar_removed',
    message: (taskTitle: string) =>
      `🗑️ ${fmt.task(taskTitle)} retirée de ${fmt.italic('Google Agenda')}`,
  } satisfies ActivityDef<[string]>,

  jobTableImported: {
    action_type: 'job_table_imported',
    message: (count: number) =>
      `🗂️ Importation de ${fmt.counter(count)} ${fmt.bold('postes')}`,
  } satisfies ActivityDef<[number]>,

  volunteerTableImported: {
    action_type: 'volunteer_table_imported',
    message: (count: number) =>
      `🙋 Importation de ${fmt.counter(count)} ${fmt.bold('bénévoles')}`,
  } satisfies ActivityDef<[number]>,

  scheduleModified: {
    action_type: 'schedule_modified',
    message: (count: number) =>
      `📅 ${fmt.counter(count)} modification${count > 1 ? 's' : ''} apportée${count > 1 ? 's' : ''} au ${fmt.bold('planning')}`,
  } satisfies ActivityDef<[number]>,
 
  geneticAlgorithmRun: {
    action_type: 'genetic_algorithm_run',
    message: (fitness: string, affectation_done: string, affected_volunteers: string) =>
      `🧬 Algorithme executé — ${fmt.metric(affected_volunteers, 'bénévoles affectés')} | ${fmt.metric(affectation_done, 'affectations')} | ${fmt.metric(fitness, 'satisfaction')}`,
  } satisfies ActivityDef<[string, string, string]>,

} satisfies Record<string, ActivityDef<any[]>>


type Loggers = {
  [K in keyof typeof ACTIVITIES]: (
    ...args: Parameters<(typeof ACTIVITIES)[K]['message']>
  ) => ReturnType<ReturnType<typeof useActivity>['createActivity']>
}

export function useActivityLogger(): Loggers {
  const { createActivity } = useActivity()

  return Object.fromEntries(
    Object.entries(ACTIVITIES).map(([key, def]) => [
      key,
      (...args: unknown[]) =>
        createActivity({
          title:       (def.message as (...a: unknown[]) => string)(...args),
          action_type: def.action_type
        }),
    ]),
  ) as Loggers
}